from tronpy import Tron
from tronpy.providers import HTTPProvider
from tronpy.keys import PrivateKey
import requests

# ABI контракта USDT на TRON
USDT_ABI = [
    {
        "constant": True,
        "inputs": [{"name": "_owner", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "balance", "type": "uint256"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function",
    },
    {
        "constant": False,
        "inputs": [
            {"name": "_to", "type": "address"},
            {"name": "_value", "type": "uint256"}
        ],
        "name": "transfer",
        "outputs": [{"name": "", "type": "bool"}],
        "payable": False,
        "stateMutability": "nonpayable",
        "type": "function",
    }
    # Добавьте другие функции из ABI, если это необходимо
]


class TRONUSDTClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.tron = self.initialize_client()
        self.private_key = self.generate_private_key()
        self.tron.private_key = self.private_key
        self.tron.default_address = self.private_key.public_key.to_base58check_address()
        self.usdt_contract_address = 'TXLAQ63Xg1NAzckPwKHvzw7CSEmLMEqcdj'  # Адрес контракта для USDT на основной сети TRON

    def generate_private_key(self):
        return PrivateKey.random()

    def generate_new_address(self):
        private_key = self.generate_private_key()
        public_key = private_key.public_key
        address = public_key.to_base58check_address()
        return address, private_key

    def initialize_client(self):
        # Используем Trongrid в качестве провайдера
        provider = HTTPProvider(api_key=self.api_key)
        return Tron(provider)

    def get_usdt_contract(self):
        try:
            # Загружаем контракт с указанным ABI
            contract = self.tron.get_contract(self.usdt_contract_address)
            contract.abi = USDT_ABI  # Устанавливаем ABI
            return contract
        except Exception as e:
            print(f"Ошибка при получении контракта: {e}")
            return None
            
    def get_balance(self, address):
        try:
            balance =  self.tron.get_account_balance(address)
            return balance
        except Exception:
            return 0
    
    def send_usdt(self, to_address, amount):
        try:
            txn = (
                self.tron.trx.transfer(self.tron.default_address, to_address, 1_000)
                .memo("test memo")
                .build()
                .sign(self.private_key)
            )
            print(txn.txid)
            print(txn.broadcast().wait())
        except Exception as e:
            print(f"Ошибка при отправке транзакции: {e}")
            return None

# Пример использования
api_key = '62ee4e3d-4432-4dee-909f-d8d39f897c67'
client = TRONUSDTClient(api_key)

print(f"Сгенерированный приватный ключ отправителя: {client.private_key.hex()}")
print(f"Адрес отправителя: {client.tron.default_address}")

# Генерация нового адреса для получателя
receiver_address, receiver_private_key = client.generate_new_address()
print(f"Сгенерированный адрес получателя: {receiver_address}")

amount = 10  # сумма в USDT

print(f"Баланс отправителя: {client.get_balance(client.tron.default_address)} USDT")
tx_id = client.send_usdt(receiver_address, amount)
print(f"ID транзакции: {tx_id}")
