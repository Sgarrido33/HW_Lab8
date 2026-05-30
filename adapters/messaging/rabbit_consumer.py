import json
import pika
from domain.models import Transaction
from application.use_cases import ProcessTransactionUseCase
import config

class RabbitMQConsumer:
    def __init__(self, use_case: ProcessTransactionUseCase, connection_params: pika.ConnectionParameters = None):
        self.use_case = use_case
        self.connection_params = connection_params or config.get_rabbitmq_connection_params()
        self.connection = None
        self.channel = None

    def start(self) -> None:
        try:
            self.connection = pika.BlockingConnection(self.connection_params)
            self.channel = self.connection.channel()
            
            # Declarar cola
            self.channel.queue_declare(queue=config.QUEUE_TRANSACTIONS, durable=True)
            
            # Prefetch
            self.channel.basic_qos(prefetch_count=1)

            def callback(ch, method, properties, body):
                try:
                    print(f"\n [x] Recibido mensaje en cola '{config.QUEUE_TRANSACTIONS}'")
                    data = json.loads(body.decode("utf-8"))
                    transaction = Transaction.from_dict(data)
                    
                    # Ejecutar caso de uso
                    account = self.use_case.execute(transaction)
                    
                    print(f" [x] Procesado con éxito. Tarjeta: {account.tarjeta_cliente} | "
                          f"Puntos Totales: {account.puntos_acumulados} | Cashback Total: {account.cashback_acumulado}")
                    
                    # Confirmar mensaje
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                except Exception as ex:
                    print(f" [!] Error al procesar el mensaje: {ex}")
                    # Rechazar mensaje
                    ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

            self.channel.basic_consume(
                queue=config.QUEUE_TRANSACTIONS,
                on_message_callback=callback,
                auto_ack=False
            )

            print(f" [*] Esperando transacciones en '{config.QUEUE_TRANSACTIONS}'. Presione CTRL+C para salir.")
            self.channel.start_consuming()

        except Exception as e:
            print(f" [!] Error en el consumidor de RabbitMQ: {e}")
        finally:
            self.stop()

    def stop(self) -> None:
        try:
            if self.channel and self.channel.is_open:
                self.channel.stop_consuming()
            if self.connection and self.connection.is_open:
                self.connection.close()
        except Exception:
            pass
