from typing import Dict, Any

class Transaction:
    def __init__(self, monto_consumido: float, tarjeta_cliente: str, codigo_restaurante: str, fecha_hora: str):
        if monto_consumido < 0:
            raise ValueError("El monto consumido no puede ser negativo.")
        if not tarjeta_cliente:
            raise ValueError("El número de tarjeta del cliente es obligatorio.")
        if not codigo_restaurante:
            raise ValueError("El código del restaurante afiliado es obligatorio.")
            
        self.monto_consumido = monto_consumido
        self.tarjeta_cliente = tarjeta_cliente
        self.codigo_restaurante = codigo_restaurante
        self.fecha_hora = fecha_hora

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Transaction':
        return cls(
            monto_consumido=float(data["monto_consumido"]),
            tarjeta_cliente=str(data["tarjeta_cliente"]),
            codigo_restaurante=str(data["codigo_restaurante"]),
            fecha_hora=str(data["fecha_hora"])
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "monto_consumido": self.monto_consumido,
            "tarjeta_cliente": self.tarjeta_cliente,
            "codigo_restaurante": self.codigo_restaurante,
            "fecha_hora": self.fecha_hora
        }


class Reward:
    def __init__(self, puntos: int, cashback: float):
        self.puntos = puntos
        self.cashback = cashback


class CustomerAccount:
    def __init__(self, tarjeta_cliente: str, puntos_acumulados: int = 0, cashback_acumulado: float = 0.0):
        if not tarjeta_cliente:
            raise ValueError("El número de tarjeta del cliente es obligatorio.")
        self.tarjeta_cliente = tarjeta_cliente
        self.puntos_acumulados = puntos_acumulados
        self.cashback_acumulado = cashback_acumulado

    def acumular_recompensas(self, reward: Reward):
        self.puntos_acumulados += reward.puntos
        self.cashback_acumulado += reward.cashback

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tarjeta_cliente": self.tarjeta_cliente,
            "puntos_acumulados": self.puntos_acumulados,
            "cashback_acumulado": round(self.cashback_acumulado, 2)
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CustomerAccount':
        return cls(
            tarjeta_cliente=str(data["tarjeta_cliente"]),
            puntos_acumulados=int(data["puntos_acumulados"]),
            cashback_acumulado=float(data["cashback_acumulado"])
        )
