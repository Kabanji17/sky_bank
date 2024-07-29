import unittest
from unittest.mock import patch, Mock
from datetime import datetime
from freezegun import freeze_time
import pytest
import pandas as pd

from src.utils import (
    read_xls_file,
    greetings,
    filter_transactions_by_date,
    filter_transactions_by_card,
    get_top_five_transactions,
    fetch_exchange_rates,
    fetch_stock_prices,
)


class TestReadXlsFile(unittest.TestCase):

    @patch('src.utils.pd.read_excel')
    def test_read_xls_file(self, mock_read_excel):
        # Создаем тестовый DataFrame
        test_data = {
            'Column1': [1, 2, 3],
            'Column2': ['A', 'B', 'C']
        }
        test_df = pd.DataFrame(test_data)

        # Настраиваем mock для функции read_excel
        mock_read_excel.return_value = test_df

        # Вызываем тестируемую функцию
        file_path = 'dummy_path.xlsx'
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


def test_filter_transactions_by_date():
    # Создаем тестовые данные
    test_data = {
        'Дата операции': [
            '01.01.2023 12:00:00',
            '15.01.2023 12:00:00',
            '20.02.2023 12:00:00',
            '05.03.2023 12:00:00',
            '10.03.2023 12:00:00'
        ],
        'Сумма': [100, 200, 300, 400, 500]
    }

    transactions = pd.DataFrame(test_data)

    # Тест: фильтрация до 16 января 2023
    end_date = '16.01.2023 13:00:00'
    expected_data = {
        'Дата операции': [
            '01.01.2023 12:00:00',
            '15.01.2023 12:00:00',
        ],
        'Сумма': [100, 200]
    }
    expected_df = pd.DataFrame(expected_data)

    result_df = filter_transactions_by_date(transactions, end_date)

    # Проверка результата
    pd.testing.assert_frame_equal(result_df, expected_df)

    # Тест: фильтрация с некорректной датой
    end_date_invalid = 'неправильная_дата'
    result_df_invalid = filter_transactions_by_date(transactions, end_date_invalid)

    # Проверка, что все транзакции возвращаются, так как используется текущая дата
    expected_df_all = transactions.reset_index(drop=True)
    pd.testing.assert_frame_equal(result_df_invalid, expected_df_all)


@pytest.fixture
def sample_transactions():
    data = {
        "Номер карты": ["1234567812345678", "1234567812345678", "8765432187654321", "8765432187654321"],
        "Сумма платежа": [-1000, -2000, -1500, 3000]
    }
    return pd.DataFrame(data)


def test_filter_transactions_by_card(sample_transactions):
    result = filter_transactions_by_card(sample_transactions)

    expected_result = [
        {"last_digits": "5678", "total_spent": 3000, "cashback": 30.0},
        {"last_digits": "4321", "total_spent": 1500, "cashback": 15.0}
    ]

    assert result == expected_result


def test_no_negative_transactions():
    df_empty = pd.DataFrame(columns=["Номер карты", "Сумма платежа"])
    result = filter_transactions_by_card(df_empty)
    assert result == []


def test_single_transaction():
    df_single = pd.DataFrame({
        "Номер карты": ["1234567812345678"],
        "Сумма платежа": [-500]
    })
    result = filter_transactions_by_card(df_single)
    assert result == [{"last_digits": "5678", "total_spent": 500, "cashback": 5.0}]


def test_mixed_transactions():
    df_mixed = pd.DataFrame({
        "Номер карты": ["1234567812345678", "1234567812345678", "8765432187654321", "8765432187654321"],
        "Сумма платежа": [-1000, 500, -1500, 3000]
    })
    result = filter_transactions_by_card(df_mixed)
    expected_result = [
        {"last_digits": "5678", "total_spent": 1000, "cashback": 10.0},
        {"last_digits": "4321", "total_spent": 1500, "cashback": 15.0}
    ]

    assert result == expected_result


@pytest.fixture
def sample_transactions_2():
    data = {
        "Дата операции": pd.to_datetime([
            "2023-01-01", "2023-01-02", "2023-01-03",
            "2023-01-04", "2023-01-05", "2023-01-06"
        ]),
        "Сумма операции": [1000, 2000, 1500, 3000, 2500, 500],
        "Категория": ["Продукты", "Транспорт", "Развлечения", "Путешествия", "Кафе", "Магазин"],
        "Описание": ["Покупка в магазине", "Билет на автобус", "Кино", "Отпуск", "Обед", "Кофе"]
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
    expected = [
        {"currency": "USD", "rate": 74.5},
        {"currency": "EUR", "rate": 89.3}
    ]
    assert result == expected


@patch("requests.get")
def test_fetch_stock_prices(mock_get):
    mock_response_aapl = Mock()
    mock_response_aapl.json.return_value = {
        "Time Series (Daily)": {"2024-07-25": {"4. close": "150.00"}}
    }
    mock_response_amzn = Mock()
    mock_response_amzn.json.return_value = {
        "Time Series (Daily)": {"2024-07-25": {"4. close": "3300.00"}}
    }
    mock_get.side_effect = [mock_response_aapl, mock_response_amzn]

    result = fetch_stock_prices(mock_get)
    expected = [
        {"stock": "AAPL", "price": "150.00"},
        {"stock": "AMZN", "price": "3300.00"}
    ]
    assert result == expected

