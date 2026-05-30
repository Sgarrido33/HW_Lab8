# Documento - Sistema de Recompensas de Restaurantes

## 1. Patrones Arquitectónicos Utilizados

La solución fue diseñada e implementada aplicando dos patrones principales:
1. **Arquitectura Hexagonal (Puertos y Adaptadores)**: Para aislar las reglas de negocio del sistema de los detalles de infraestructura (bases de datos, colas de mensajería).
2. **Arquitectura Orientada a Eventos (EDA - Event-Driven Architecture)**: Utilizando RabbitMQ como broker de mensajería para procesar de manera asíncrona y desacoplada las transacciones de consumo.

---

## 2. Justificación de los Atributos de Calidad

* **Bajo Acoplamiento**: La capa de negocio (domain y application) no depende de librerías externas de infraestructura (como pika para RabbitMQ o librerías de bases de datos). Esto permite que, si en el futuro se decide cambiar el broker a Apache Kafka o la base de datos a PostgreSQL, la lógica del negocio permanezca intacta; solo se tendrían que desarrollar nuevos adaptadores.
* **Alta Cohesión**: Cada módulo tiene una responsabilidad única delimitada:
  * El Dominio se encarga únicamente de las validaciones de datos y reglas de cálculo de puntos.
  * La Aplicación coordina los flujos de trabajo (Casos de Uso).
  * Los Adaptadores se encargan exclusivamente de la comunicación externa (guardar en JSON y conectarse al Broker).
* **Modularidad**: El código está organizado en directorios que reflejan sus capas arquitectónicas, facilitando el mantenimiento y las pruebas automatizadas (91% de cobertura).

---

## 3. Estructura de Capas y Componentes

### A. Capa de Dominio
Ubicada en el núcleo del sistema, es totalmente independiente de tecnologías externas.
* **Modelos (domain/models.py)**: Define las entidades Transaction, Reward y CustomerAccount. Valida que los datos de entrada sean consistentes (ej. montos positivos, tarjetas obligatorias).
* **Puertos (domain/ports.py)**: Define los interfaces abstractas (contratos) del sistema:
  * TransactionRepositoryPort: Contrato para guardar y consultar saldos.
  * EventPublisherPort: Contrato para publicar eventos de notificación.
* **Servicios (domain/services.py)**: RewardService calcula las recompensas bajo una regla estándar (1 punto por $1 consumido con redondeo y 2% de cashback).

### B. Capa de Aplicación (Application)
Orquesta el comportamiento del sistema.
* **Casos de Uso (application/use_cases.py)**: ProcessTransactionUseCase recibe la transacción, solicita a RewardService el cálculo de las recompensas, recupera o crea la cuenta del cliente a través del repositorio port, actualiza los saldos, persiste la información y publica el evento de confirmación en la cola.

### C. Capa de Adaptadores e Infraestructura (Adapters)
Contiene las implementaciones físicas que conectan los puertos con tecnologías reales.
* **Persistencia (adapters/repository/json_repository.py)**: Implementa TransactionRepositoryPort y simula una base de datos escribiendo el estado del cliente de forma persistente en un archivo local rewards_db.json.
* **Mensajería - Productor (adapters/messaging/rabbit_publisher.py)**: Implementa EventPublisherPort utilizando la librería pika para enviar datos en formato JSON a las colas de RabbitMQ.
* **Mensajería - Consumidor (adapters/messaging/rabbit_consumer.py)**: Se suscribe a la cola de RabbitMQ y escucha la llegada de nuevas transacciones en segundo plano para delegar su procesamiento al caso de uso de la aplicación. Utiliza el mecanismo de basic_ack (auto_ack=False) para garantizar que ningún mensaje se pierda en caso de fallo de red.
