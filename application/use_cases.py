from domain.models import Transaction, CustomerAccount
from domain.ports import TransactionRepositoryPort, EventPublisherPort
from domain.services import RewardService

class ProcessTransactionUseCase:
    def __init__(self, repository: TransactionRepositoryPort, publisher: EventPublisherPort):
        self.repository = repository
        self.publisher = publisher

    def execute(self, transaction: Transaction) -> CustomerAccount:
        # Calcular recompensas
        reward = RewardService.calculate_reward(transaction)

        # Obtener o crear cuenta de cliente
        account = self.repository.get_by_card_number(transaction.tarjeta_cliente)
        if account is None:
            account = CustomerAccount(tarjeta_cliente=transaction.tarjeta_cliente)

        # Acumular recompensas
        account.acumular_recompensas(reward)

        # Persistir cuenta
        self.repository.save(account)

        # Publicar evento de exito
        self.publisher.publish_reward_processed(
            card_number=account.tarjeta_cliente,
            points=reward.puntos,
            cashback=reward.cashback
        )

        return account
