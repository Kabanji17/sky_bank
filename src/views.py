import json

import pandas as pd

from src.utils import (
    fetch_exchange_rates,
    fetch_stock_prices,
    filter_transactions_by_card,
    filter_transactions_by_date,
    get_top_five_transactions,
    greetings,
    read_xls_file,
    setting_log,
)

logger = setting_log("views")

df_transactions = read_xls_file("../data/operations.xls")


def generate_json_response(df_transactions: pd.DataFrame, input_date: str):
    """Функция, получения json-запроса для главной страницы"""
    logger.info("Функция начала свою работу.")
    with open("../user_settings.json", "r") as f:
        user_settings = json.load(f)
    logger.info("Файл успешно открыт")

    user_currencies = user_settings["user_currencies"]
    user_stocks = user_settings["user_stocks"]

    greeting = greetings()
    sorted_transactions = filter_transactions_by_date(df_transactions, input_date)
    cards_operations = filter_transactions_by_card(df_transactions)
    top_transactions = get_top_five_transactions(sorted_transactions)
    currency_rates = fetch_exchange_rates(user_currencies)
    stock_prices = fetch_stock_prices(user_stocks)
    logger.info("Функция обрабатывает данные транзакций.")
    date_json = json.dumps(
        {
            "greeting": greeting,
            "cards": cards_operations,
            "top_transactions": top_transactions,
            "currency_rates": currency_rates,
            "stock_prices": stock_prices,
        },
        indent=4,
        ensure_ascii=False,
    )
    logger.info("Функция успешно завершила свою работу.")
    return date_json


# Example usage
if __name__ == "__main__":
    input_date = "2023-05-20 14:30:00"
    print(generate_json_response(df_transactions, input_date))
