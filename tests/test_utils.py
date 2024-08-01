import unittest
from unittest.mock import Mock, patch

import pandas as pd
import pytest
from freezegun import freeze_time

from src.utils import (
    fetch_exchange_rates,
    fetch_stock_prices,
    filter_transactions_by_card,
    get_top_five_transactions,
    greetings,
    read_xls_file,
)


class TestReadXlsFile(unittest.TestCase):

    @patch("src.utils.pd.read_excel")
    def test_read_xls_file(self, mock_read_excel):
        # Создаем тестовый DataFrame
        test_data = {"Column1": [1, 2, 3], "Column2": ["A", "B", "C"]}
        test_df = pd.DataFrame(test_data)

        # Настраиваем mock для функции read_excel
        mock_read_excel.return_value = test_df

        # Вызываем тестируемую функцию
        file_path = "dummy_path.xlsx"
        result = read_xls_file(file_path)

        # Проверяем, что mock был вызван с правильными аргументами
        mock_read_excel.assert_called_once_with(file_path)

        # Проверяем, что результат соответствует ожидаемому DataFrame
        pd.testing.assert_frame_equal(result, test_df)


@freeze_time("2023-01-01 10:00:00")
def test_greetings_morning():
    assert greetings() == "Доброе утро"


@freeze_time("2023-01-01 15:00:00")
def test_greetings_day():
    assert greetings() == "Добрый день"


@freeze_time("2023-01-01 19:00:00")
def test_greetings_evening():
    assert greetings() == "Добрый вечер"


@freeze_time("2023-01-01 23:00:00")
def test_greetings_night():
    assert greetings() == "Доброй ночи"


@pytest.fixture
def sample_transactions():
    data = {
        "Номер карты": ["1234567812345678", "1234567812345678", "8765432187654321", "8765432187654321"],
        "Сумма платежа": [-1000, -2000, -1500, 3000],
    }
    return pd.DataFrame(data)


def test_filter_transactions_by_card(sample_transactions):
    result = filter_transactions_by_card(sample_transactions)

    expected_result = [
        {"last_digits": "5678", "total_spent": 3000, "cashback": 30.0},
        {"last_digits": "4321", "total_spent": 1500, "cashback": 15.0},
    ]

    assert result == expected_result


def test_no_negative_transactions():
    df_empty = pd.DataFrame(columns=["Номер карты", "Сумма платежа"])
    result = filter_transactions_by_card(df_empty)
    assert result == []


def test_single_transaction():
    df_single = pd.DataFrame({"Номер карты": ["1234567812345678"], "Сумма платежа": [-500]})
    result = filter_transactions_by_card(df_single)
    assert result == [{"last_digits": "5678", "total_spent": 500, "cashback": 5.0}]


def test_mixed_transactions():
    df_mixed = pd.DataFrame(
        {
            "Номер карты": ["1234567812345678", "1234567812345678", "8765432187654321", "8765432187654321"],
            "Сумма платежа": [-1000, 500, -1500, 3000],
        }
    )
    result = filter_transactions_by_card(df_mixed)
    expected_result = [
        {"last_digits": "5678", "total_spent": 1000, "cashback": 10.0},
        {"last_digits": "4321", "total_spent": 1500, "cashback": 15.0},
    ]

    assert result == expected_result


@pytest.fixture
def sample_transactions_2():
    data = {
        "Дата операции": pd.to_datetime(
            ["2023-01-01", "2023-01-02", "2023-01-03", "2023-01-04", "2023-01-05", "2023-01-06"]
        ),
        "Сумма операции": [1000, 2000, 1500, 3000, 2500, 500],
        "Категория": ["Продукты", "Транспорт", "Развлечения", "Путешествия", "Кафе", "Магазин"],
        "Описание": ["Покупка в магазине", "Билет на автобус", "Кино", "Отпуск", "Обед", "Кофе"],
    }
    return pd.DataFrame(data)


def test_get_top_five_transactions(sample_transactions_2):
    result = get_top_five_transactions(sample_transactions_2)

    expected_result = [
        {"date": "04.01.2023", "amount": 3000, "category": "Путешествия", "description": "Отпуск"},
        {"date": "05.01.2023", "amount": 2500, "category": "Кафе", "description": "Обед"},
        {"date": "02.01.2023", "amount": 2000, "category": "Транспорт", "description": "Билет на автобус"},
        {"date": "03.01.2023", "amount": 1500, "category": "Развлечения", "description": "Кино"},
        {"date": "01.01.2023", "amount": 1000, "category": "Продукты", "description": "Покупка в магазине"},
    ]

    assert result == expected_result


def test_get_top_five_transactions_less_than_five(sample_transactions_2):
    # Удалим некоторые транзакции для проверки поведения с меньшим количеством данных
    reduced_transactions = sample_transactions_2.head(3)
    result = get_top_five_transactions(reduced_transactions)

    expected_result = [
        {"date": "02.01.2023", "amount": 2000, "category": "Транспорт", "description": "Билет на автобус"},
        {"date": "03.01.2023", "amount": 1500, "category": "Развлечения", "description": "Кино"},
        {"date": "01.01.2023", "amount": 1000, "category": "Продукты", "description": "Покупка в магазине"},
    ]

    assert result == expected_result


@patch("requests.get")
def test_fetch_exchange_rates(mock_get):
    mock_response_usd = Mock()
    mock_response_usd.json.return_value = {"result": 74.5}
    mock_response_eur = Mock()
    mock_response_eur.json.return_value = {"result": 89.3}
    mock_get.side_effect = [mock_response_usd, mock_response_eur]

    result = fetch_exchange_rates(["USD", "EUR"])
    expected = [{"currency": "USD", "rate": 74.5}, {"currency": "EUR", "rate": 89.3}]
    assert result == expected


@patch("requests.get")
def test_fetch_stock_prices(mock_get):

    mock_get.return_value.json.return_value = {"Global Quote": {"05. price": 150.00}}

    list_stocks = ["AAPL"]

    result = fetch_stock_prices(list_stocks)
    expected = [
        {"stock": "AAPL", "price": 150.00},
    ]
    assert result == expected
