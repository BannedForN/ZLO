from flask import Flask, render_template, request, redirect, url_for
from web3 import Web3
from web3.middleware import geth_poa_middleware
from contract_info import abi, contract_address
from enum import Enum
import re

app = Flask(__name__)

W3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))
W3.middleware_onion.inject(geth_poa_middleware, layer=0)

contract = W3.eth.contract(address=contract_address, abi=abi)
print(contract.address)

class AdStatus(Enum):
    OPEN = 0
    CLOSED = 1

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

def register(password):
    valid, message = validate_password(password)
    if not valid:
        return message
    address = W3.geth.personal.new_account(password)
    return f"Ваш адрес: {address}"

def auth(public_key, password):
    try:
        W3.geth.personal.unlock_account(public_key, password)
        return public_key
    except Exception as e:
        return f"Ошибка {e}"

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        result = auth(username, password)
        if result.startswith("Ошибка"):
            return render_template("login.html", error=result)
        else:
            return redirect(url_for('funcs', account=username))
    else:
        return render_template("login.html", error=None)

@app.route('/reg', methods=['GET', 'POST'])
def reg():
    if request.method == 'POST':
        password = request.form.get('password')
        result = register(password)
        if result.startswith("Пароль"):
            return render_template("reg.html", error=result)
        else:
            address = result.split(": ")[1]  # Извлекаем адрес из сообщения
            return render_template("reg.html", success=result, address=address)
    else:
        return render_template("reg.html", error=None)

@app.route('/funcs', methods=['GET', 'POST'])
def funcs():
    account = request.args.get('account')
    message = None
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'buy_estate':
            ad_id = int(request.form.get('ad_id'))
            value = int(request.form.get('value'))
            message = buy_estate(ad_id, value, account)
        elif action == 'get_balance':
            message = getBalance(account)
        elif action == 'withdraw':
            amount = int(request.form.get('amount'))
            message = withDraw(account, amount)
        elif action == 'show_balance':
            balance = W3.eth.get_balance(account)
            message = f"Баланс аккаунта: {balance}"
        elif action == 'create_estate':
            square = int(request.form.get('square'))
            rooms = int(request.form.get('rooms'))
            es_type = int(request.form.get('es_type'))
            message = create_estate(square, rooms, es_type, account)
        elif action == 'create_ad':
            estate_id = int(request.form.get('estate_id'))
            price = int(request.form.get('price'))
            message = create_ad(estate_id, price, account)
        elif action == 'update_estate_status':
            estate_id = int(request.form.get('estate_id'))
            message = update_estate_status(estate_id, account)
        elif action == 'update_ad_status':
            estate_id = int(request.form.get('estate_id'))
            ad_id = int(request.form.get('ad_id'))
            message = update_ad_status(estate_id, ad_id, account)
    return render_template("funcs.html", account=account, message=message)

def validate_inputs(inputs, expected_types):
    for input_value, expected_type in zip(inputs, expected_types):
        if input_value is None:
            return False, "Пустое значение не допускается"
        if isinstance(input_value, str) and input_value.strip() == "":
            return False, "Пустое значение не допускается"
        if not isinstance(input_value, expected_type):
            return False, f"Неверный тип данных: ожидается {expected_type}, получено {type(input_value)}"
    return True, "Валидация прошла успешно"

def buy_estate(ad_id, value, account):
    valid, message = validate_inputs((ad_id, value, account), (int, int, str))
    if not valid:
        return message
    try:
        tx_hash = contract.functions.buyEstate(ad_id).transact({
            'from': account,
            'value': value
        })
        return f"Недвижимость приобретена: {tx_hash.hex()}"
    except Exception as e:
        return f"Ошибка: {e}"

def getBalance(account):
    valid, message = validate_inputs((account,), (str,))
    if not valid:
        return message
    try:
        balance = contract.functions.getBalance().call({
            'from': account,
        })
        return f"Баланс на смартконтракте: {balance} wei"
    except Exception as e:
        return f"Error: {e}"

def withDraw(account, amount):
    valid, message = validate_inputs((account, amount), (str, int))
    if not valid:
        return message
    try:
        tx_hash = contract.functions.withdraw(amount).transact({
            'from': account,
        })
        return f"Средства сняты: {tx_hash.hex()}"
    except Exception as e:
        return f"Ошибка: {e}"

def create_estate(square, rooms, es_type, account):
    valid, message = validate_inputs((square, rooms, es_type, account), (int, int, int, str))
    if not valid:
        return message
    try:
        tx_hash = contract.functions.createEstate(square, rooms, es_type).transact({
            'from': account
        })
        return f"Недвижимость создана: {tx_hash.hex()}"
    except Exception as e:
        return f"Ошибка: {e}"

def update_estate_status(estate_id, account):
    valid, message = validate_inputs((estate_id, account), (int, str))
    if not valid:
        return message
    try:
        tx_hash = contract.functions.updateEstateStatus(estate_id).transact({
            'from': account
        })
        return f"Статус недвижимости обновлён: {tx_hash.hex()}"
    except Exception as e:
        return f"Ошибка: {e}"

def create_ad(estate_id, price, account):
    valid, message = validate_inputs((estate_id, price, account), (int, int, str))
    if not valid:
        return message
    try:
        tx_hash = contract.functions.createAd(estate_id, price).transact({
            'from': account
        })
        return f"Объявление создано: {tx_hash.hex()}"
    except Exception as e:
        return f"Ошибка: {e}"

def update_ad_status(estate_id, ad_id, account):
    valid, message = validate_inputs((estate_id, ad_id, account), (int, int, str))
    if not valid:
        return message
    try:
        tx_hash = contract.functions.updateAdStatus(estate_id, ad_id).transact({
            'from': account
        })
        return f"Статус объявления обновлён: {tx_hash.hex()}"
    except Exception as e:
        return f"Ошибка: {e}"

if __name__ == "__main__":
    app.run(debug=True)