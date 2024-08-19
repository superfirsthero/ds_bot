from solana.keypair import Keypair
from solana.rpc.api import Client
from solana.transaction import Transaction as trans
from solana.system_program import TransferParams, transfer
from solana.publickey import PublicKey
from bitcoin import *
from web3 import Web3, HTTPProvider

from web3.middleware import geth_poa_middleware
import requests
import random
from bitcoinlib.wallets import Wallet
from bitcoinlib.transactions import Transaction


from tronpy import Tron
from tronpy.keys import PrivateKey
from tronpy.contract import Contract
from litecoinutils.setup import setup
from litecoinutils.keys import P2pkhAddress, PrivateKey
from litecoinutils.transactions import Transaction, TxInput, TxOutput
from litecoinutils.utils import to_satoshis
from bit import Key
from bit.network import NetworkAPI


USDT_CONTRACT_ADDRESS = "0xdAC17F958D2ee523a2206206994597C13D831ec7"

class LitecoinPayment:
    def __init__(self):
        setup('mainnet')  # Use 'mainnet' or 'testnet'
        self.private_key = PrivateKey()
        self.address = self.private_key.get_public_key().get_address().to_string()
        print(f"Private key: {self.private_key.to_wif()}")
        print(f'Created Litecoin Wallet. Address: {self.address}')

    def get_address(self):
        return self.address
    
    def get_private_key(self):
        listt = {
            "private_key" : self.my_private_key,
            "public_key" : self.address
        }
        return listt

    def check_balance(self):
        url = f'https://api.blockcypher.com/v1/ltc/main/addrs/{self.address}/balance'
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            balance = data['final_balance'] / 1e8  # Balance in satoshis, convert to LTC
            print(f'Balance: {balance} LTC')
            return balance
        else:
            print(f'Error fetching balance: {response.status_code}')
            return None

    def send_payment(self, to_address, amount):
        # Получение неподтвержденных выходов (UTXO)
        url = f'https://api.blockcypher.com/v1/ltc/main/addrs/{self.address}'
        response = requests.get(url)
        if response.status_code != 200:
            print(f'Ошибка при получении UTXO: {response.status_code}')
            return None

        data = response.json()
        
        if 'txrefs' not in data:
            print('Нет доступных UTXO.')
            return None

        utxos = data['txrefs']
        
        # Создание входов транзакции
        inputs = []
        total_input = 0
        for utxo in utxos:
            txid = utxo['tx_hash']
            output_idx = utxo['tx_output_n']
            value = to_satoshis(utxo['value'] / 1e8)  # Значение в сатоши, конвертация в LTC
            total_input += value
            inputs.append(TxInput(txid, output_idx, value))
            if total_input >= to_satoshis(amount):
                break

        if total_input < to_satoshis(amount):
            print('Недостаточно средств')
            return None

        # Создание выходов транзакции
        outputs = []
        outputs.append(TxOutput(to_satoshis(amount), P2pkhAddress(to_address)))

        # Добавление сдачи
        change = total_input - to_satoshis(amount) - to_satoshis(0.001)  # Комиссия 0.001 LTC
        if change > 0:
            outputs.append(TxOutput(change, P2pkhAddress(self.address)))

        # Создание транзакции
        tx = Transaction(inputs, outputs)
        for i, txin in enumerate(tx.inputs):
            txin.script_sig = self.private_key.sign_input(tx, i, P2pkhAddress(self.address).to_script_pub_key())

        # Отправка транзакции через API
        raw_tx = tx.serialize()
        url = 'https://api.blockcypher.com/v1/ltc/main/txs/push'
        response = requests.post(url, json={'tx': raw_tx})
        if response.status_code == 201:
            data = response.json()
            tx_hash = data['tx']['hash']

            # Создание ссылки для отслеживания транзакции
            tracking_link = f'https://live.blockcypher.com/ltc/tx/{tx_hash}'

            print(f'Транзакция отправлена. Хеш: {tx_hash}')
            print(f'Отслеживайте транзакцию здесь: {tracking_link}')
            return tracking_link
        else:
            print(f'Ошибка при отправке транзакции: {response.status_code}')
            print(response.json())
            return None



class BitcoinPayment:
    def __init__(self, api_token):
        self.api_token = api_token
        self.base_url = "https://api.blockcypher.com/v1/btc/main"
        self.wallet = Wallet.create(f'Wallet{random.randint(1, 10000000000000000)}')
        self.key = self.wallet.get_key()  # Get the key from the wallet
        self.my_private_key = self.key.wif  # Private key in WIF format
        self.my_address = self.wallet.get_key().address

        print(self.my_private_key)
        print(f'Bitcoin Wallet Address: {self.my_address}')

    def get_address(self):
        return self.my_address

    def get_private_key(self):
        listt = {
            "private_key" : self.my_private_key,
            "public_key" : self.my_address
            }
        return listt

    def check_balance(self):
        url = f"{self.base_url}/addrs/{self.my_address}/balance"
        response = requests.get(url)
        response.raise_for_status()  # Error checking
        balance = response.json().get('balance', 0) / 1e8  # Convert satoshi to BTC
        print(f'Balance: {balance} BTC')
        return balance

    def send_payment(self, destination_address, amount):
        tx = {
            "inputs": [{"addresses": [self.my_address]}],
            "outputs": [{"addresses": [destination_address], "value": int(amount * 1e8)}]  # Конвертируем BTC в сатоши
        }
        url = f"{self.base_url}/txs/new?token={self.api_token}"
        response = requests.post(url, json=tx)
        response.raise_for_status()  # Проверка на ошибки
        tx = response.json()

        # Подписываем транзакцию
        transaction = Transaction.import_dict(tx)
        transaction.sign(self.wallet.key_private)

        # Отправляем подписанную транзакцию
        signed_tx = transaction.as_dict()
        url = f"{self.base_url}/txs/send?token={self.api_token}"
        response = requests.post(url, json=signed_tx)
        response.raise_for_status()  # Проверка на ошибки
        tx_hash = response.json().get('tx', {}).get('hash', '')

        # Создаем ссылку для отслеживания транзакции
        tracking_link = f'https://live.blockcypher.com/btc/tx/{tx_hash}'
        
        print(f'Транзакция отправлена: {tx_hash}')
        print(f'Отслеживайте транзакцию здесь: {tracking_link}')
        
        return tx_hash



class EthereumPayment:
    def __init__(self, infura_url):
        self.infura_url = infura_url
        self.web3 = Web3(Web3.HTTPProvider(infura_url))
        self.web3.middleware_stack.inject(geth_poa_middleware, layer=0)
        self.private_key = self.web3.eth.account.create().key
        self.address = self.web3.eth.account.from_key(self.private_key).address
        print(f'Ethereum Address: {self.address}')
        print(f'Private Key: {self.private_key.hex()}')

    def get_address(self):
        return self.address

    def get_private_key(self):
        listt = {
            "private_key" : self.private_key.hex(), 
            "public_key" : self.address
            }
        return listt

    def check_balance(self):
        balance_wei = self.web3.eth.get_balance(self.address)
        balance_eth = self.web3.from_wei(balance_wei, 'ether')
        print(f'Balance: {balance_eth} ETH')
        return balance_eth

    def send_payment(self, to_address, amount_eth):
        nonce = self.web3.eth.get_transaction_count(self.address)
        gas_price = self.web3.eth.gas_price
        gas_limit = 21000
        tx = {
            'nonce': nonce,
            'to': to_address,
            'value': self.web3.to_wei(amount_eth, 'ether'),
            'gas': gas_limit,
            'gasPrice': gas_price,
            'chainId': 1
        }

        signed_tx = self.web3.eth.account.sign_transaction(tx, private_key=self.private_key)
        tx_hash = self.web3.eth.send_raw_transaction(signed_tx.rawTransaction)
        
        # Создаем ссылку для отслеживания транзакции
        tracking_link = f'https://etherscan.io/tx/{tx_hash.hex()}'
        
        print(f'Транзакция отправлена: {tx_hash.hex()}')
        print(f'Отслеживайте транзакцию здесь: {tracking_link}')
        
        return tracking_link

class SolanaPayment:
    def __init__(self, rpc_url="https://api.devnet.solana.com"):
        self.client = Client(rpc_url)
        self.keypair = Keypair()
        self.public_key = self.keypair.public_key
        self.secret_key = self.keypair.secret_key
        print(f'Public Key: {self.public_key}')
        print(f'Secret Key: {self.secret_key.hex()}')

    def get_address(self):
        return str(self.public_key)
    
    def get_private_key(self):
        listt = {
            "public_key" : self.public_key,
            "private_key" : self.secret_key.hex(),
        }
        return listt

    def check_balance(self):
        balance_response = self.client.get_balance(self.public_key)
        balance = balance_response['result']['value'] / 1e9  # Convert lamports to SOL
        print(f'Balance: {balance} SOL')
        return balance

    def send_payment(self, to_address, amount):
        to_pubkey = PublicKey(to_address)
        transaction = trans().add(
            transfer(
                TransferParams(
                    from_pubkey=self.public_key,
                    to_pubkey=to_pubkey,
                    lamports=int(amount),  # Convert SOL to lamports
                )
            )
        )
        response = self.client.send_transaction(transaction, self.keypair)
        print(f'Transaction sent: {response}')
        tx_signature = response['result']
        tracking_link = f'https://explorer.solana.com/tx/{tx_signature}?cluster=mainnet-beta'
        return tracking_link

class UsdtPayment:
    def __init__(self):
        self.client = Tron()
        self.private_key = PrivateKey.random()
        self.address = self.private_key.public_key.to_base58check_address()
        print(f'Created Tron Wallet. Address: {self.address}')

    def get_address(self):
        return self.address

    def get_private_key(self):
        listt = {
            "public_key" : self.public_key,
            "private_key" : self.secret_key
        }
        return listt

    def check_balance(self):
        balance = self.client.get_account_balance(self.address)
        print(f'Balance: {balance} TRX')
        return balance

    def send_payment(self, to_address, amount):
        txn = (
            self.client.trx.transfer(self.address, to_address, amount)
            .memo("Payment")
            .build()
            .sign(self.private_key)
        )
        result = txn.broadcast().wait()
        tx_id = result['id']

        # Создание ссылки для отслеживания транзакции
        tracking_link = f'https://tronscan.org/#/transaction/{tx_id}'

        print(f'Transaction sent: {tx_id}')
        print(f'Track your transaction here: {tracking_link}')
        
        return tracking_link