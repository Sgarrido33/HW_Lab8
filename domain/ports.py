from abc import ABC, abstractmethod
from domain.models import CustomerAccount, Transaction

class TransactionRepositoryPort(ABC):
    @abstractmethod
    def get_by_card_number(self, card_number: str) -> CustomerAccount:
        pass

    @abstractmethod
    def save(self, account: CustomerAccount) -> None:
        pass


class EventPublisherPort(ABC):
    @abstractmethod
    def publish_transaction(self, transaction: Transaction) -> None:
        pass

    @abstractmethod
    def publish_reward_processed(self, card_number: str, points: int, cashback: float) -> None:
        pass
