import requests
from litecoinutils.setup import setup
from litecoinutils.keys import P2pkhAddress, PrivateKey
from litecoinutils.transactions import Transaction, TxInput, TxOutput
from litecoinutils.script import Script
from litecoinutils.utils import to_satoshis

class LitecoinPayment:
    def __init__(self):
        setup('mainnet')  # Используем тестовую сеть для отладки
        self.private_key = PrivateKey("TAGzS8BL9C78McHT2zS51dbCUA5kqDrk698doK5Jt2B8GJoeeHvE")
        self.address = self.private_key.get_public_key().get_address().to_string()
        print(f'Created Litecoin Wallet. Address: {self.address}')

    def get_address(self):
        return self.address

    def check_balance(self):
        url = f'https://api.blockcypher.com/v1/ltc/main/addrs/{self.address}/balance'
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            balance = data['final_balance'] / 1e8  # баланс в сатоши, конвертируем в LTC
            print(f'Balance: {balance} LTC')
            return balance
        else:
            print(f'Error fetching balance: {response.status_code}')
            return None

    def send_transaction(self, to_address, amount):
        # Получаем непотраченные выходы (UTXO)
        url = f'https://api.blockcypher.com/v1/ltc/main/addrs/{self.address}'
        response = requests.get(url)
        if response.status_code != 200:
            print(f'Error fetching UTXO: {response.status_code}')
            return None

        data = response.json()
        
        if 'txrefs' not in data:
            print('No UTXOs available.')
            return None

        utxos = data['txrefs']
        
        # Создаем входы для транзакции
        inputs = []
        total_input = 0
        for utxo in utxos:
            txid = utxo['tx_hash']
            output_idx = utxo['tx_output_n']
            value = to_satoshis(utxo['value'] / 1e8)  # значение в сатоши, конвертируем в LTC
            total_input += value
            inputs.append(TxInput(txid, output_idx, value))
            if total_input >= to_satoshis(amount):
                break

        if total_input < to_satoshis(amount):
            print('Not enough funds')
            return None

        # Создаем выходы для транзакции
        outputs = []
        outputs.append(TxOutput(to_satoshis(amount), P2pkhAddress(to_address)))

        # Добавляем сдачу
        change = total_input - to_satoshis(amount) - to_satoshis(0.001)  # 0.001 LTC комиссия
        if change > 0:
            outputs.append(TxOutput(change, P2pkhAddress(self.address)))

        # Создаем транзакцию
        tx = Transaction(inputs, outputs)
        for i, txin in enumerate(tx.inputs):
            txin.script_sig = self.private_key.sign_input(tx, i, P2pkhAddress(self.address).to_script_pub_key())

        # Отправляем транзакцию через API
        raw_tx = tx.serialize()
        url = 'https://api.blockcypher.com/v1/ltc/main/txs/push'
        response = requests.post(url, json={'tx': raw_tx})
        if response.status_code == 201:
            data = response.json()
            tx_hash = data['tx']['hash']
            print(f'Transaction sent. Hash: {tx_hash}')
            return tx_hash
        else:
            print(f'Error sending transaction: {response.status_code}')
            print(response.json())
            return None

# Пример использования
wallet = LitecoinPayment()
print(wallet.check_balance())
wallet.send_transaction("Lbq2vajeoovtGKY5DNp7LVrquHLcDS1GoB", 0.1)  # Замените на реальный адрес и сумму
