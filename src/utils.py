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
    logger.info("Файл успешно открыт")
    return df


def greetings() -> str:
    """Функция приветствия по времени суток"""
    today = datetime.now()
    logger.info("Функция начала свою работу.")
    if 5 <= today.hour < 12:
        logger.info("Функция успешно завершила свою работу.")
        return "Доброе утро"
    elif 12 <= today.hour < 17:
        logger.info("Функция успешно завершила свою работу.")
        return "Добрый день"
    elif 17 <= today.hour < 23:
        logger.info("Функция успешно завершила свою работу.")
        return "Добрый вечер"
    else:
        logger.info("Функция успешно завершила свою работу.")
        return "Доброй ночи"


def filter_transactions_by_date(transactions: pd.DataFrame, end_date: str = None) -> pd.DataFrame:
    """Функция, фильтрующая данные транзакций по дате.
    Вводимый формат даты: %d.%m.%Y %H:%M:%S.
    Возвращает DataFrame с отфильтрованными транзакциями."""
    logger.info("Функция начала свою работу.")
    if end_date is None:
        end_date_time = datetime.now()
    else:
        try:
            end_date_time = datetime.strptime(end_date, "%d.%m.%Y %H:%M:%S")
        except ValueError:
            logger.error("Введена некорректная дата. Будет использована текущая дата")
            end_date_time = datetime.now()

    start_date = end_date_time.replace(day=1)

    # Преобразуем столбец 'Дата операции' в формат datetime
    transactions["Дата операции"] = pd.to_datetime(transactions["Дата операции"], format="%d.%m.%Y %H:%M:%S")
    logger.info("Функция обрабатывает данные транзакций.")
    # Фильтруем транзакции по дате
    filtered_transactions = transactions[
        (transactions["Дата операции"] >= start_date) & (transactions["Дата операции"] <= end_date_time)
    ]
    logger.info("Функция успешно завершила свою работу.")
    return filtered_transactions.reset_index(drop=True)


def filter_transactions_by_card(df_transactions: pd.DataFrame) -> list[dict]:
    """Функция, фильтрующая информацию об операциях по номеру карты
    и выводящая общую информацию по каждой карте в словаре"""
    logger.info("Функция начала свою работу.")
    cards_dict = (
        df_transactions.loc[df_transactions["Сумма платежа"] < 0]
        .groupby(by="Номер карты")
        .agg("Сумма платежа")
        .sum()
        .to_dict()
    )
    logger.info("Функция обрабатывает данные транзакций.")
    expenses_cards = []
    for card, expenses in cards_dict.items():
        expenses_cards.append(
            {"last_digits": card[-4:], "total_spent": abs(expenses), "cashback": abs(round(expenses / 100, 2))}
        )
    logger.info("Функция успешно завершила свою работу.")
    return expenses_cards


def get_top_five_transactions(filtered_transactions: pd.DataFrame) -> list[dict]:
    """Функция, выдающая информацию о ТОП-5 транзакциях по сумме платежа."""
    logger.info("Функция начала свою работу.")
    # Сортируем транзакции по сумме и выбираем топ-5
    top_5_transactions = filtered_transactions.nlargest(5, "Сумма операции")
    logger.info("Функция обрабатывает данные транзакций.")
    # Создаем список словарей с нужными данными
    top_list = []
    for _, transaction in top_5_transactions.iterrows():
        transaction_dict = {
            "date": transaction["Дата операции"].strftime("%d.%m.%Y"),
            "amount": transaction["Сумма операции"],
            "category": transaction["Категория"],
            "description": transaction["Описание"],
        }
        top_list.append(transaction_dict)
    logger.info("Функция успешно завершила свою работу.")
    return top_list


def fetch_exchange_rates(currencies: list) -> dict:
    """Функция, получающая курсы валют"""
    logger.info("Функция начала свою работу.")
    api_key = ER_API_KEY
    exchange_rates = []
    logger.info("Функция обрабатывает данные транзакций.")
    for currency in currencies:
        url = f"https://api.apilayer.com/exchangerates_data/convert?to=RUB&from={currency}&amount=1"
        headers = {"apikey": api_key}
        response = requests.get(url, headers=headers)
        data = response.json()
        if "result" in data:
            exchange_rate_dict = {"currency": currency, "rate": round(data["result"], 2)}
            exchange_rates.append(exchange_rate_dict)
        else:
            exchange_rates[currency] = {"rate_to_rub": "N/A", "error": data.get("error", "Unknown error")}
    logger.info("Функция успешно завершила свою работу.")
    return exchange_rates


def fetch_stock_prices(stocks: list) -> dict:
    """Функция, получающая цены на акции"""
    logger.info("Функция начала свою работу.")
    api_key = SP_API_KEY
    stock_prices = []
    logger.info("Функция обрабатывает данные транзакций.")
    for stock in stocks:
        url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={stock}&apikey={api_key}"
        response = requests.get(url, timeout=5, allow_redirects=False)
        result = response.json()
        logger.info(f"{result}")
        stock_prices.append({"stock": stock, "price": round(float(result["Global Quote"]["05. price"]), 2)})
    logger.info("Функция успешно завершила свою работу.")
    return stock_prices


if __name__ == "__main__":
    df_transactions = read_xls_file("../data/operations.xls")
    my_list = df_transactions.to_dict(orient="records")
    sortirovka = filter_transactions_by_date(df_transactions)

    # print(get_top_five_transactions(sortirovka))

    # print(fetch_exchange_rates(["USD", "EUR"]))
    print(fetch_stock_prices(["AAPL", "AMZN", "GOOGL", "MSFT", "TSLA"]))
    # fltr = filter_transactions_by_date(my_transactions)
    # print(process_transactions(my_transactions, date=datetime.now()))
    # print(filter_transactions_by_card(df_transactions))
    # print(get_top_five_transactions(fltr))
