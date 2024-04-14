import json

import requests
from starlette.config import Config

config = Config(".env")

CREATE_INVOICE_PATH = 'https://api.monobank.ua/api/merchant/invoice/create'
HEADERS = {"X-Token": config('MONO_TOKEN')}
# RATE_USD = 39.5
WEBHOOK_URL = f"{config('WEBHOOK_URL')}/payment/web-shop"


async def set_webhook():
    url = "https://api.monobank.ua/personal/webhook"
    data = {"webHookUrl": WEBHOOK_URL}
    json_data = json.dumps(data)  # Перетворюємо словник на рядок JSON
    response = requests.post(url=url, headers=HEADERS, data=json_data)
    print(f"{response.status_code=}")
    return {"ok": True}


def get_usd_rate_mono() -> float:
    """функція отримання поточного курсу валюти USD"""
    print(f"Start getting USD rate")
    url = "https://api.monobank.ua/bank/currency"
    response = requests.get(url=url)
    if response.status_code == 200:
        print(f"Response Status {response.status_code}")
        data = response.json()
        for curr in data:
            if curr.get('currencyCodeA') == 840:
                usd_rate = round(curr.get("rateSell"), 2)
                print(f"USD rate is {usd_rate}")
                return usd_rate


def create_invoice(total_price: float, products: list[dict]) -> dict:
    """Функція для стровення інвойсу"""
    print(f"Start create_invoice")
    order_basket = []
    RATE_USD = get_usd_rate_mono()
    for product in products:
        item = {
            "name": product.get("title"),
            "qty": 1,
            "sum": int(product.get("price") * RATE_USD * 100),
            "icon": "https://res.cloudinary.com/myfinance/image/upload/v1693416024/syncwave//img/phones/apple-iphone-xs-max/gold/00.png",
            "unit": "шт.",
            "code": product.get("id"),
            "barcode": product.get("id"),
            "header": "string",
            "footer": "string",
            "tax": [],
            "uktzed": "string",
            "discounts": [
                {
                    "type": "DISCOUNT",
                    "mode": "PERCENT",
                    "value": "10"
                }]}
        order_basket.append(item)

    body = {
        "amount": 100,  # int(total_price * RATE_USD * 100),  # todo this is real price from web shop
        "ccy": 980,
        "merchantPaymInfo": {
            "reference": "123",
            "destination": "Order from Telegram Bot",
            "comment": "Покупка Apple",
            "customerEmails": [],
            "basketOrder": order_basket},
        "redirectUrl": "https://t.me/table_trans_4_bot",
        "webHookUrl": WEBHOOK_URL,
        "validity": 3600,
        "paymentType": "debit"
    }
    response = requests.post(url=CREATE_INVOICE_PATH, headers=HEADERS, data=json.dumps(body))
    print(f"{response.status_code=}")
    print(response.json())
    return response.json()
