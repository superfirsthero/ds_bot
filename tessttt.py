# from web3 import Web3

# # # Подключаемся к провайдеру
# infura_url = "https://mainnet.infura.io/v3/02b62268c6b04bd49ded8090a5f539e4"
# web3 = Web3(Web3.HTTPProvider(infura_url))

# # # Приватный ключ, который вы уже имеете
# private_key = "0xd1f9d2b8fefb3f52588785fece5d92963db9b64de0f24560937d2877238284cd"

# # # Создаем аккаунт из приватного ключа
# account = web3.eth.account.from_key(private_key)

# # # Получаем адрес
# address = account.address
# print(f'Address: {address}')

# # # Получаем баланс
# balance = web3.eth.get_balance(account.address)
# balance_in_ether = web3.from_wei(balance, 'ether')
# print(f'Balance: {balance_in_ether} ETH')

# # # Параметры транзакции
# value_to_send = 0.0011  # ETH
# gas = 21000  # Стандартное количество газа для обычной транзакции
# gas_price = web3.to_wei('50', 'gwei')

# # # Расчет стоимости газа и общей стоимости транзакции
# gas_cost = gas * gas_price
# value = web3.to_wei(value_to_send, 'ether')
# total_cost = gas_cost + value

# # # Проверка баланса
# transaction = {
#         'to': '0xc0e0300a568F316C1F0E64b037C49919896c0Fc6',  # Замените на адрес получателя
#         'value': value,
#         'gas': gas,
#         'gasPrice': gas_price,
#         'nonce': web3.eth.get_transaction_count(account.address),
#         'chainId': 1  # Mainnet
# }

# # Подписание транзакции
# signed_tx = web3.eth.account.sign_transaction(transaction, private_key)

# #     # Отправка транзакции
# tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
# print(f'Transaction sent: {tx_hash.hex()}')



from solana.keypair import Keypair
from solana.rpc.api import Client
from solana.transaction import Transaction as trans
from solana.system_program import TransferParams, transfer
from solana.publickey import PublicKey


private_key_hex = "6805d45ffd901f8d6a3754a92bcb6545220e4dacf9a236ef5f7971b1ab7ac28123f51b14372bb910f31ebe2464090cd8351ab8f2a3f6a7d29988c9262c233ec7"

# Преобразуем hex в байты
private_key_bytes = bytes.fromhex(private_key_hex)

# Создаем Keypair из приватного ключа
keypair = Keypair.from_secret_key(private_key_bytes)
public_key = keypair.public_key
print(public_key)
# Создаем клиента для подключения к Solana
client = Client("https://api.devnet.solana.com")

# Проверяем баланс аккаунта
balance = client.get_balance(keypair.public_key)
print(f"Balance: {balance['result']['value']} lamports")

to_pubkey = PublicKey("3aiQ1Xiirk2N9W5JLbXZaciUrMx2ZUvmh235iN6DWmT6")

transaction = trans().add(
        transfer(
                TransferParams(
                        from_pubkey=public_key,
                        to_pubkey=to_pubkey,
                        lamports=1,
                        )# 0.08
                        )
                        )


response = client.send_transaction(transaction, keypair)
print(response)