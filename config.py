import pika

RABBITMQ_USER = "students"
RABBITMQ_PASSWORD = "Ut3c2026"
RABBITMQ_HOST = "213.199.42.57"
RABBITMQ_PORT = 5672
RABBITMQ_VIRTUAL_HOST = "/"

# Colas
QUEUE_TRANSACTIONS = "transacciones_restaurante"
QUEUE_NOTIFICATIONS = "recompensas_procesadas"

def get_rabbitmq_connection_params() -> pika.ConnectionParameters:
    credenciales = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD)
    return pika.ConnectionParameters(
        host=RABBITMQ_HOST,
        port=RABBITMQ_PORT,
        virtual_host=RABBITMQ_VIRTUAL_HOST,
        credentials=credenciales,
        connection_attempts=3,
        retry_delay=5
    )
