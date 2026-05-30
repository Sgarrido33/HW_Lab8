import os
import json
import pytest
from unittest.mock import MagicMock, patch
from domain.models import CustomerAccount, Transaction
from adapters.repository.json_repository import JsonTransactionRepository
from adapters.messaging.rabbit_publisher import RabbitMQPublisher
from adapters.messaging.rabbit_consumer import RabbitMQConsumer

def test_json_repository_lifecycle(tmp_path):
    # Usar una ruta de archivo temporal provista por pytest
    db_file = tmp_path / "test_db.json"
    repo = JsonTransactionRepository(str(db_file))
    
    # 1. Recuperar cuenta inexistente
    acc = repo.get_by_card_number("9999")
    assert acc is None
    
    # 2. Guardar cuenta
    new_acc = CustomerAccount("9999", puntos_acumulados=10, cashback_acumulado=1.5)
    repo.save(new_acc)
    
    # Verificar que el archivo se creó y contiene los datos
    assert db_file.exists()
    
    # 3. Recuperar cuenta existente
    fetched_acc = repo.get_by_card_number("9999")
    assert fetched_acc is not None
    assert fetched_acc.tarjeta_cliente == "9999"
    assert fetched_acc.puntos_acumulados == 10
    assert fetched_acc.cashback_acumulado == 1.5

def test_json_repository_corrupt_file(tmp_path):
    # Archivo corrupto (no es JSON válido)
    db_file = tmp_path / "corrupt_db.json"
    db_file.write_text("not a valid json")
    
    repo = JsonTransactionRepository(str(db_file))
    # No debe lanzar excepción, debe retornar None
    acc = repo.get_by_card_number("9999")
    assert acc is None

@patch("pika.BlockingConnection")
def test_rabbitmq_publisher(mock_blocking_connection):
    # Configurar mocks
    mock_conn = MagicMock()
    mock_channel = MagicMock()
    mock_blocking_connection.return_value = mock_conn
    mock_conn.channel.return_value = mock_channel
    
    publisher = RabbitMQPublisher()
    
    # Publicar transacción
    tx = Transaction(100.0, "1234-5678", "REST01", "2026-05-30T10:00:00")
    publisher.publish_transaction(tx)
    
    # Verificar interacción con el canal de RabbitMQ
    mock_channel.queue_declare.assert_called_with(queue="transacciones_restaurante", durable=True)
    mock_channel.basic_publish.assert_called()
    mock_conn.close.assert_called_once()
    
    # Publicar procesamiento de recompensa
    publisher.publish_reward_processed("1234-5678", 100, 2.0)
    mock_channel.queue_declare.assert_called_with(queue="recompensas_procesadas", durable=True)

@patch("pika.BlockingConnection")
def test_rabbitmq_consumer_start_stop(mock_blocking_connection):
    # Configurar mocks
    mock_conn = MagicMock()
    mock_channel = MagicMock()
    mock_blocking_connection.return_value = mock_conn
    mock_conn.channel.return_value = mock_channel
    
    use_case = MagicMock()
    consumer = RabbitMQConsumer(use_case)
    
    # Mockear basic_consume para simular la recepción de un mensaje
    def mock_consume(queue, on_message_callback, auto_ack):
        # Crear un body de transacción simulado
        body = b'{"monto_consumido": 150.0, "tarjeta_cliente": "1234-5678", "codigo_restaurante": "REST01", "fecha_hora": "2026-05-30"}'
        method = MagicMock()
        method.delivery_tag = 1
        properties = MagicMock()
        
        # Llamar al callback
        on_message_callback(mock_channel, method, properties, body)
        
    mock_channel.basic_consume.side_effect = mock_consume
    
    # Iniciar consumidor (se ejecutará y cerrará al procesar)
    consumer.start()
    
    # Verificar que el caso de uso fue invocado con éxito y el mensaje fue confirmado
    use_case.execute.assert_called_once()
    mock_channel.basic_ack.assert_called_once_with(delivery_tag=1)
    
    # Detener consumidor
    consumer.stop()
    assert mock_conn.close.called
