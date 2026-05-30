from unittest.mock import MagicMock
from domain.models import Transaction, CustomerAccount
from domain.ports import TransactionRepositoryPort, EventPublisherPort
from application.use_cases import ProcessTransactionUseCase

def test_process_transaction_new_customer():
    # Mock de dependencias
    repo = MagicMock(spec=TransactionRepositoryPort)
    repo.get_by_card_number.return_value = None  # Nuevo cliente sin cuenta previa
    
    pub = MagicMock(spec=EventPublisherPort)
    
    use_case = ProcessTransactionUseCase(repository=repo, publisher=pub)
    
    tx = Transaction(
        monto_consumido=100.0,
        tarjeta_cliente="1111-2222",
        codigo_restaurante="REST001",
        fecha_hora="2026-05-30T10:00:00"
    )
    
    account = use_case.execute(tx)
    
    # Verificar cálculos (100 puntos y 2.0 de cashback)
    assert account.tarjeta_cliente == "1111-2222"
    assert account.puntos_acumulados == 100
    assert account.cashback_acumulado == 2.0
    
    # Verificar que se interactuó correctamente con el repositorio y el broker
    repo.get_by_card_number.assert_called_once_with("1111-2222")
    repo.save.assert_called_once()
    pub.publish_reward_processed.assert_called_once_with(
        card_number="1111-2222",
        points=100,
        cashback=2.0
    )

def test_process_transaction_existing_customer():
    # Mock de dependencias
    existing_account = CustomerAccount(tarjeta_cliente="3333-4444", puntos_acumulados=50, cashback_acumulado=1.5)
    
    repo = MagicMock(spec=TransactionRepositoryPort)
    repo.get_by_card_number.return_value = existing_account
    
    pub = MagicMock(spec=EventPublisherPort)
    
    use_case = ProcessTransactionUseCase(repository=repo, publisher=pub)
    
    tx = Transaction(
        monto_consumido=200.0,
        tarjeta_cliente="3333-4444",
        codigo_restaurante="REST001",
        fecha_hora="2026-05-30T10:00:00"
    )
    
    account = use_case.execute(tx)
    
    # Verificar cálculos acumulados (50 + 200 puntos = 250, 1.5 + 4.0 cashback = 5.5)
    assert account.tarjeta_cliente == "3333-4444"
    assert account.puntos_acumulados == 250
    assert account.cashback_acumulado == 5.5
    
    # Verificar interacciones
    repo.get_by_card_number.assert_called_once_with("3333-4444")
    repo.save.assert_called_once_with(existing_account)
    pub.publish_reward_processed.assert_called_once_with(
        card_number="3333-4444",
        points=200,
        cashback=4.0
    )
