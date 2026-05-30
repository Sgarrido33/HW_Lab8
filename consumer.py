import sys
from adapters.repository.json_repository import JsonTransactionRepository
from adapters.messaging.rabbit_publisher import RabbitMQPublisher
from adapters.messaging.rabbit_consumer import RabbitMQConsumer
from application.use_cases import ProcessTransactionUseCase

def main():
    print("--- INICIANDO SERVICIO DE RECOMPENSAS (CONSUMER) ---")
    
    # 1. Instanciar adaptadores de infraestructura
    repository = JsonTransactionRepository("rewards_db.json")
    publisher = RabbitMQPublisher()
    
    # 2. Instanciar caso de uso de aplicación
    use_case = ProcessTransactionUseCase(repository, publisher)
    
    # 3. Instanciar y arrancar el consumidor de eventos
    consumer = RabbitMQConsumer(use_case)
    
    try:
        consumer.start()
    except KeyboardInterrupt:
        print("\n [*] Deteniendo el servicio de recompensas...")
        consumer.stop()
        sys.exit(0)

if __name__ == "__main__":
    main()
