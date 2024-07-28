import pytest
from unittest.mock import patch, mock_open
import json
import pandas as pd
from datetime import datetime
from src.utils import (
    read_xls_file,
    xls_to_dict,
    setting_log,
    greetings,
    filter_transactions_by_date,
    filter_transactions_by_card,
    get_top_five_transactions,
    fetch_exchange_rates,
    fetch_stock_prices,
)
from src.views import generate_json_response


mock_user_settings = {
    "user_currencies": ["USD", "EUR"],
    "user_stocks": ["AAPL", "AMZN"]
}

mock_transactions = [
    {"Дата операции": "01.05.2023 10:00:00", "Сумма платежа": -100.0, "Номер карты": "1234", "Категория": "Cat1", "Описание": "Desc1"},
    {"Дата операции": "15.05.2023 12:00:00", "Сумма платежа": -200.0, "Номер карты": "5678", "Категория": "Cat2", "Описание": "Desc2"}
]

mock_df = pd.DataFrame(mock_transactions)

mock_currency_rates = [
    {"currency": "USD", "rate": 74.5},
    {"currency": "EUR", "rate": 89.3}
]

mock_stock_prices = [
    {"stock": "AAPL", "price": "150.00"},
    {"stock": "AMZN", "price": "3300.00"}
]

mock_greeting = "Добрый день"

mock_cards_operations = [
    {"last_digits": "1234", "total spent": 100.0, "cashback": 1.0},
    {"last_digits": "5678", "total spent": 200.0, "cashback": 2.0}
]

mock_top_transactions = [
    {"date": "15.05.2023 12:00:00", "amount": -200.0, "category": "Cat2", "description": "Desc2"},
    {"date": "01.05.2023 10:00:00", "amount": -100.0, "category": "Cat1", "description": "Desc1"}
]


@patch("builtins.open", new_callable=mock_open, read_data=json.dumps(mock_user_settings))
@patch("src.utils.read_xls_file", return_value=mock_df)
@patch("src.utils.xls_to_dict", return_value=mock_transactions)
@patch("src.utils.greetings", return_value=mock_greeting)
@patch("src.utils.filter_transactions_by_date", return_value=mock_transactions)
@patch("src.utils.filter_transactions_by_card", return_value=mock_cards_operations)
@patch("src.utils.get_top_five_transactions", return_value=mock_top_transactions)
@patch("src.utils.fetch_exchange_rates", return_value=mock_currency_rates)
@patch("src.utils.fetch_stock_prices", return_value=mock_stock_prices)
def test_generate_json_response(mock_open, mock_greetings,
                                mock_filter_transactions_by_date, mock_filter_transactions_by_card,
                                mock_get_top_five_transactions, mock_fetch_exchange_rates, mock_fetch_stock_prices):
    input_date = "20.05.2023 14:30:00"
    result = generate_json_response("dummy_path.xls", input_date)

    expected_result = json.dumps(
        {
            "greeting": mock_greeting,
            "cards": mock_cards_operations,
            "top_transactions": mock_top_transactions,
            "currency_rates": mock_currency_rates,
            "stock_prices": mock_stock_prices
        },
        indent=4,
        ensure_ascii=False
    )

    assert result == expected_result


if __name__ == "__main__":
    pytest.main()