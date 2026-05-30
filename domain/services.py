import math
from domain.models import Transaction, Reward

class RewardService:
    @staticmethod
    def calculate_reward(transaction: Transaction) -> Reward:
        # 1 punto por $1 gastado (redondeo matematico)
        puntos = math.floor(transaction.monto_consumido + 0.5)
        
        # 2% de cashback del total
        cashback = round(transaction.monto_consumido * 0.02, 2)
        
        return Reward(puntos=puntos, cashback=cashback)
