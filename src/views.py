import json

from src.utils import (
    read_xls_file,
    setting_log,
    greetings,
    filter_transactions_by_date,
    filter_transactions_by_card,
    get_top_five_transactions,
    fetch_exchange_rates,
    fetch_stock_prices,
)


# Main function to generate JSON response
def generate_json_response(file_path, input_date):
    """Функция, получения json-запроса для главной страницы"""
    with open("../user_settings.json", "r") as f:
        user_settings = json.load(f)

    user_currencies = user_settings["user_currencies"]
    user_stocks = user_settings["user_stocks"]

    greeting = greetings()
    df_transactions = read_xls_file(file_path)
    sorted_transactions = filter_transactions_by_date(df_transactions, input_date)
    cards_operations = filter_transactions_by_card(df_transactions)
    top_transactions = get_top_five_transactions(sorted_transactions)
    currency_rates = fetch_exchange_rates(user_currencies)
    stock_prices = fetch_stock_prices(user_stocks)

    date_json = json.dumps(
        {
            "greeting": greeting,
            "cards": cards_operations,
            "top_transactions": top_transactions,
            "currency_rates": currency_rates,
            "stock_prices": stock_prices
        },
        indent=4,
        ensure_ascii=False
    )
    return date_json


# Example usage
if __name__ == "__main__":
    input_date = "2023-05-20 14:30:00"
    print(generate_json_response("../data/operations.xls" ,input_date))
