import os
import json
from domain.models import CustomerAccount
from domain.ports import TransactionRepositoryPort

class JsonTransactionRepository(TransactionRepositoryPort):
    def __init__(self, file_path: str = "rewards_db.json"):
        self.file_path = file_path

    def _read_db(self) -> dict:
        if not os.path.exists(self.file_path):
            return {}
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}

    def _write_db(self, data: dict) -> None:
        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        except IOError as e:
            print(f" [!] Error al escribir en base de datos JSON: {e}")

    def get_by_card_number(self, card_number: str) -> CustomerAccount:
        db = self._read_db()
        account_data = db.get(card_number)
        if account_data:
            return CustomerAccount.from_dict(account_data)
        return None

    def save(self, account: CustomerAccount) -> None:
        db = self._read_db()
        db[account.tarjeta_cliente] = account.to_dict()
        self._write_db(db)
