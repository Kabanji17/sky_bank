import logging
import os
from datetime import datetime, timedelta

import pandas as pd
import requests
from dotenv import load_dotenv

load_dotenv()

SP_API_KEY = os.getenv("SP_API_KEY")
ER_API_KEY = os.getenv("ER_API_KEY")


def setting_log(name: str) -> logging.Logger:
    """Функция для настройки логера"""
    logger = logging.getLogger(name)
    file_handler = logging.FileHandler(f"../logs/{name}.log", "w", encoding="utf-8")
    file_formatter = logging.Formatter("%(asctime)s %(module)s %(funcName)s %(levelname)s: %(message)s")
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    logger.setLevel(logging.DEBUG)
    return logger


logger = setting_log("utils")


def read_xls_file(file_path: str) -> pd.DataFrame:
    """Функция преобразования Excel-файла в DataFrame"""
    df = pd.read_excel(file_path)
    return df


def xls_to_dict(file_path: str) -> list[dict]:
    """Функция преобразования датафрейма транзакций в список словарь"""
    df = read_xls_file(file_path)
    transactions = df.to_dict(orient="records")
    return transactions


def greetings() -> str:
    """Функция приветствия по времени суток"""
    today = datetime.now()
    if 5 <= today.hour < 12:
        return "Доброе утро"
    elif 12 <= today.hour < 17:
        return "Добрый день"
    elif 17 <= today.hour < 23:
        return "Добрый вечер"
    else:
        return "Доброй ночи"


def filter_transactions_by_date(transactions: list[dict], end_date: str = datetime.now()) -> list[dict]:
    """Функция, фильтрующая данные транзакций по дате, вводимый формат даты %d.%m.%Y %H:%M:%S"""
    if end_date:
        try:
            end_date_time = datetime.strptime(end_date, "%d.%m.%Y %H:%M:%S")
        except:
            print("Введена некорректная дата. Будет использована текущая дата")
            end_date_time = datetime.now()
    start_date = end_date_time.replace(day=1)
    filtered_transactions = []
    for transaction in transactions:
        transaction_date_str = transaction.get("Дата операции")
        transaction_date = datetime.strptime(transaction_date_str, "%d.%m.%Y %H:%M:%S")
        if start_date <= transaction_date <= end_date_time:
            filtered_transactions.append(transaction)
    return filtered_transactions


def filter_transactions_by_card(df_transactions: pd.DataFrame) -> list[dict]:
    """Функция, фильтрующая информацию об операциях по номеру карты
    и выводящая общую информацию по каждой карте в словаре"""
    cards_dict = (
        df_transactions.loc[df_transactions["Сумма платежа"] < 0]
        .groupby(by="Номер карты")
        .agg("Сумма платежа")
        .sum()
        .to_dict()
    )
    expenses_cards = []
    for card, expenses in cards_dict.items():
        expenses_cards.append(
            {"last_digits": card[-4:], "total_spent": abs(expenses), "cashback": abs(round(expenses / 100, 2))}
        )
    return expenses_cards


def get_top_five_transactions(filtered_transactions: list[dict]) -> list[dict]:
    """Функция, выдающая информацию о ТОП-5 транзакциях по сумме платежа"""
    top_5_transactions = sorted(filtered_transactions, key=lambda x: x["Сумма операции"], reverse=True)[:5]
    top_list = []
    for transaction in top_5_transactions:
        transaction_dict = {
            "date": transaction["Дата операции"],
            "amount": transaction["Сумма платежа"],
            "category": transaction["Категория"],
            "description": transaction["Описание"],
        }
        top_list.append(transaction_dict)
    return top_list


def fetch_exchange_rates(currencies: list) -> dict:
    """Функция, получающая курсы валют"""
    api_key = ER_API_KEY
    exchange_rates = []
    for currency in currencies:
        url = f"https://api.apilayer.com/exchangerates_data/convert?to=RUB&from={currency}&amount=1"
        headers = {"apikey": api_key}
        response = requests.get(url, headers=headers)
        data = response.json()
        if "result" in data:
            exchange_rate_dict = {"currency": currency,
                              "rate": round(data["result"], 2)
                              }
            exchange_rates.append(exchange_rate_dict)
        else:
            exchange_rates[currency] = {"rate_to_rub": "N/A", "error": data.get("error", "Unknown error")}
    return exchange_rates


def fetch_stock_prices(stocks: list) -> dict:
    """Функция, получающая цены на акции"""
    api_url = "https://www.alphavantage.co/query"
    api_key = SP_API_KEY
    stock_prices = []
    for stock in stocks:
        params = {"function": "TIME_SERIES_DAILY", "symbol": stock, "apikey": api_key}
        response = requests.get(api_url, params=params)
        if response.status_code == 200:
            data = response.json()
            time_series = data.get("Time Series (Daily)")
            if time_series:
                latest_date = list(time_series.keys())[0]
                stock_price_dict = {
                    "stock": stock,
                    "price": time_series[latest_date]["4. close"]
                }
                stock_prices.append(stock_price_dict)
    return stock_prices


if __name__ == "__main__":
    my_transactions = xls_to_dict("../data/operations.xls")
    df_transactions = read_xls_file("../data/operations.xls")

    #print(fetch_exchange_rates(["USD", "EUR"]))
    print(fetch_stock_prices(["AAPL", "AMZN", "GOOGL", "MSFT", "TSLA"]))
    #fltr = filter_transactions_by_date(my_transactions)
    # print(process_transactions(my_transactions, date=datetime.now()))
    # print(filter_transactions_by_card(df_transactions))
    #print(get_top_five_transactions(fltr))
