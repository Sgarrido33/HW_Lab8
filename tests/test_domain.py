import pytest
from domain.models import Transaction, CustomerAccount, Reward
from domain.services import RewardService

def test_transaction_valid_creation():
    tx = Transaction(
        monto_consumido=150.50,
        tarjeta_cliente="1234-5678",
        codigo_restaurante="REST001",
        fecha_hora="2026-05-30T10:00:00"
    )
    assert tx.monto_consumido == 150.50
    assert tx.tarjeta_cliente == "1234-5678"
    assert tx.codigo_restaurante == "REST001"
    assert tx.fecha_hora == "2026-05-30T10:00:00"

def test_transaction_invalid_amount():
    with pytest.raises(ValueError, match="El monto consumido no puede ser negativo."):
        Transaction(-10.0, "1234-5678", "REST001", "2026-05-30T10:00:00")

def test_transaction_missing_card():
    with pytest.raises(ValueError, match="El número de tarjeta del cliente es obligatorio."):
        Transaction(100.0, "", "REST001", "2026-05-30T10:00:00")

def test_transaction_missing_restaurant():
    with pytest.raises(ValueError, match="El código del restaurante afiliado es obligatorio."):
        Transaction(100.0, "1234-5678", "", "2026-05-30T10:00:00")

def test_transaction_serialization():
    tx = Transaction(100.0, "1234-5678", "REST001", "2026-05-30T10:00:00")
    data = tx.to_dict()
    assert data["monto_consumido"] == 100.0
    assert data["tarjeta_cliente"] == "1234-5678"
    
    tx2 = Transaction.from_dict(data)
    assert tx2.monto_consumido == 100.0
    assert tx2.tarjeta_cliente == "1234-5678"

def test_customer_account_invalid_creation():
    with pytest.raises(ValueError, match="El número de tarjeta del cliente es obligatorio."):
        CustomerAccount("")

def test_customer_account_accumulation():
    acc = CustomerAccount(tarjeta_cliente="1234-5678", puntos_acumulados=10, cashback_acumulado=2.5)
    reward = Reward(puntos=5, cashback=1.2)
    acc.acumular_recompensas(reward)
    
    assert acc.puntos_acumulados == 15
    assert acc.cashback_acumulado == 3.7
    
    data = acc.to_dict()
    assert data["tarjeta_cliente"] == "1234-5678"
    assert data["puntos_acumulados"] == 15
    assert data["cashback_acumulado"] == 3.7

    acc2 = CustomerAccount.from_dict(data)
    assert acc2.tarjeta_cliente == "1234-5678"
    assert acc2.puntos_acumulados == 15
    assert acc2.cashback_acumulado == 3.7

def test_reward_service_calculation():
    # Caso 1: redondeo arriba (150.50 -> 151 puntos, 2% = 3.01)
    tx1 = Transaction(150.50, "1234-5678", "REST001", "2026-05-30T10:00:00")
    reward1 = RewardService.calculate_reward(tx1)
    assert reward1.puntos == 151
    assert reward1.cashback == 3.01

    # Caso 2: redondeo abajo (150.40 -> 150 puntos, 2% = 3.01)
    tx2 = Transaction(150.40, "1234-5678", "REST001", "2026-05-30T10:00:00")
    reward2 = RewardService.calculate_reward(tx2)
    assert reward2.puntos == 150
    assert reward2.cashback == 3.01
