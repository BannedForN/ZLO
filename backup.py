from web3 import Web3
from web3.middleware import geth_poa_middleware
from contract_info import abi, contract_address
from enum import Enum
from flask import *
app = Flask(__name__)

W3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))
W3.middleware_onion.inject(geth_poa_middleware, layer=0)

contract = W3.eth.contract(address=contract_address, abi=abi)
print(contract.address)

address1 = Web3.to_checksum_address('0x11be109ca605509c7b56b34504ceded1ffd1bddd')
address2 = Web3.to_checksum_address('0xc54afd35321c76dcc369f9740c98e793d53f51aa')
address3 = Web3.to_checksum_address('0x2d41e729704d06d4878a7ad71181e8c32541f649')
address4 = Web3.to_checksum_address('0xa73de473fb4c02cb81b7ba526e1bf6b598a39457')
address5 = Web3.to_checksum_address('0x73d79bc7ecfb57068db3e805babe7cb2cdff0137')

balance1 = W3.eth.get_balance(address1)
balance2 = W3.eth.get_balance(address2)
balance3 = W3.eth.get_balance(address3)
balance4 = W3.eth.get_balance(address4)
balance5 = W3.eth.get_balance(address5)



print(balance1, balance2, balance3, balance4, balance5)
print(address2)
print(address3)


class AdStatus(Enum):
    OPEN = 0
    CLOSED = 1


import re

def validate_password(password):
    if len(password) < 8:
        return False, "Пароль должен содержать минимум 8 символов."
    if not re.search("[0-9]", password):
        return False, "Пароль должен содержать хотя бы одну цифру."
    if not re.search("[A-Z]", password):
        return False, "Пароль должен содержать хотя бы одну заглавную букву."
    if not re.search("[a-z]", password):
        return False, "Пароль должен содержать хотя бы одну строчную букву."
    if not re.search("[!@#$%^&*(),.?\":{}|<>]", password):
        return False, "Пароль должен содержать хотя бы один специальный символ."
    return True, "Пароль валиден."

def register():
    password = input('Введите пароль: ')
    valid, message = validate_password(password)
    if not valid:
        print(message)
        return
    address = W3.geth.personal.new_account(password)
    print(f"Ваш адрес: {address}")

def auth():
    public_key = input('Введите публичный ключ: ')
    password = input('Введите пароль: ')
    try:
        W3.geth.personal.unlock_account(public_key, password)
        return public_key
    except Exception as e:
        print(f"Ошибка {e}")
        return None




def sendEth(account):
    try:
        value = int(input("Введите сумму для перевода: "))
        tx_hash = contract.functions.sendEth().transact({
            'from': account,
            'value': value,
        })
        print(f"Транзакция выполнена: {tx_hash.hex()}")

    except Exception as e:
        print(f"Ошибка: {e}")


def getBalance(account):
    try:
        balance = contract.functions.getBalance().call({
            'from': account,
        })
        print(f"Баланс на смартконтракте: {balance} wei")
    except Exception as e:
        print(f"Error: {e}")

def withDraw(account):
    try:
        amount = int(input("Введите сумму для вывода со смартконтракта: "))
        tx_hash = contract.functions.withdraw(amount).transact({
            'from': account,
        })
        print(f"Баланс на смартконтракте: {tx_hash.hex()} ")
    except Exception as e:
        print(f"Ошибка: {e}")
def create_estate(square, rooms, es_type, account):
    try:
        tx_hash = contract.functions.createEstate(square, rooms, es_type).transact({
            'from': account
        })
        print(f"Недвижимость создана: {tx_hash.hex()}")
    except Exception as e:
        print(f"Ошибка: {e}")

def update_estate_status(estate_id, account):
    try:
        tx_hash = contract.functions.updateEstateStatus(estate_id).transact({
            'from': account
        })
        print(f"Статус недвижимости обновлён: {tx_hash.hex()}")
    except Exception as e:
        print(f"Ошибка: {e}")

def create_ad(estate_id, price, account):
    try:
        tx_hash = contract.functions.createAd(estate_id, price).transact({
            'from': account
        })
        print(f"Объявление создано: {tx_hash.hex()}")
    except Exception as e:
        print(f"Ошибка: {e}")

def update_ad_status(estate_id, ad_id, account):
    try:
        tx_hash = contract.functions.updateAdStatus(estate_id, ad_id).transact({
            'from': account
        })
        print(f"Статус объявления обновлён: {tx_hash.hex()}")
    except Exception as e:
        print(f"Ошибка: {e}")

def buy_estate(ad_id, value, account):
    try:
        tx_hash = contract.functions.buyEstate(ad_id).transact({
            'from': account,
            'value': value
        })
        print(f"Недвижимость приобретена: {tx_hash.hex()}")
    except Exception as e:
        print(f"Ошибка: {e}")


def get_balance(account):
    balance = contract.functions.getBalance().call({
        'from': account
    })
    print(f"Баланс: {balance} wei")
    return balance

def main():
    account = ""
    is_auth = False
    while True:
        if not is_auth:
            choice = input("Выберите:\n1. Авторизация\n2. Регистрация\n")
            match choice:
                case "1":
                    account = auth()
                    if account is not None and account != "":
                        is_auth = True
                case "2":
                    register()
                case _:
                    print("Ошибка ввода.")
        elif is_auth:
            choice = input("Введите:\n1. Приобрести недвижимость\n2. Проверить баланс\n3. Снять средства\n4. Показать баланс аккаунта\n5. Создать недвижимость\n6. Создать объявление\n7. Обновить статус недвижимости\n8. Обновить статус объявления\n9. Выход\n")
            match choice:
                case "1":
                    ad_id = int(input("Введите ID объявления: "))
                    value = int(input("Введите сумму для покупки: "))
                    buy_estate(ad_id, value, account)
                case "2":
                    getBalance(account)
                case "3":
                    withDraw(account)
                case "4":
                    print(f"Баланс аккаунта: {W3.eth.get_balance(account)}")
                case "5":
                    square = int(input("Введите площадь: "))
                    rooms = int(input("Введите количество комнат: "))
                    es_type = int(input("Введите тип недвижимости (0, 1, 2...): "))
                    create_estate(square, rooms, es_type, account)
                case "6":
                    estate_id = int(input("Введите ID недвижимости: "))
                    price = int(input("Введите цену: "))
                    create_ad(estate_id, price, account)
                case "7":
                    estate_id = int(input("Введите ID недвижимости: "))
                    #new_status = input("Введите новый статус (true/false): ").lower() == 'true'
                    update_estate_status(estate_id, account)
                case "8":
                    estate_id = int(input("Введите ID недвижимости: "))
                    ad_id = int(input("Введите ID объявления: "))
                    #new_status = input("Введите новый статус (0 - Открыто, 1 - Закрыто): ")
                    update_ad_status(estate_id, ad_id, account)
                case "9":
                    is_auth = False
                case _:
                    print("Некорректный ввод.")

if __name__ == "__main__":
    main()