import json
import pika
from domain.models import Transaction
from domain.ports import EventPublisherPort
import config

class RabbitMQPublisher(EventPublisherPort):
    def __init__(self, connection_params: pika.ConnectionParameters = None):
        self.connection_params = connection_params or config.get_rabbitmq_connection_params()

    def _publish(self, queue_name: str, body: dict) -> None:
        try:
            # Conexion
            connection = pika.BlockingConnection(self.connection_params)
            channel = connection.channel()
            
            # Declarar cola
            channel.queue_declare(queue=queue_name, durable=True)
            
            # Enviar mensaje
            mensaje_str = json.dumps(body)
            channel.basic_publish(
                exchange="",
                routing_key=queue_name,
                body=mensaje_str,
                properties=pika.BasicProperties(
                    delivery_mode=2,  # Mensaje persistente
                )
            )
            print(f" [x] Evento publicado en '{queue_name}': {mensaje_str}")
            connection.close()
        except Exception as e:
            print(f" [!] Error al publicar en RabbitMQ en la cola '{queue_name}': {e}")
            raise

    def publish_transaction(self, transaction: Transaction) -> None:
        self._publish(config.QUEUE_TRANSACTIONS, transaction.to_dict())

    def publish_reward_processed(self, card_number: str, points: int, cashback: float) -> None:
        body = {
            "tarjeta_cliente": card_number,
            "puntos_ganados": points,
            "cashback_ganado": cashback,
            "estado": "PROCESADO"
        }
        self._publish(config.QUEUE_NOTIFICATIONS, body)
