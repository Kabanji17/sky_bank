import json
from unittest.mock import patch, MagicMock
import pytest
from src.views import generate_json_response


def test_generate_json_response():
    # Подменяем зависимости
    mock_user_settings = {"user_currencies": ["USD", "EUR"], "user_stocks": ["AAPL", "AMZN"]}

    mock_transactions = MagicMock()
    mock_transactions.to_dict.return_value = {
        "Дата операции": ["21.12.2021", "20.12.2021", "20.12.2021", "16.12.2021", "16.12.2021"],
        "Сумма": [1198.23, 829.00, 421.00, -14216.42, 453.00],
        "Категория": ["Переводы", "Супермаркеты", "Различные товары", "ЖКХ", "Бонусы"],
        "Описание": [
            "Перевод Кредитная карта. ТП 10.2 RUR",
            "Лента",
            "Ozon.ru",
            "ЖКУ Квартира",
            "Кешбэк за обычные покупки"
        ]
    }

    expected_json = {
        "greeting": "Добрый день",
        "cards": [
            {
                "last_digits": "5814",
                "total_spent": 1262.00,
                "cashback": 12.62
            },
            {
                "last_digits": "7512",
                "total_spent": 7.94,
                "cashback": 0.08
            }
        ],
        "top_transactions": [
            {
                "date": "21.12.2021",
                "amount": 1198.23,
                "category": "Переводы",
                "description": "Перевод Кредитная карта. ТП 10.2 RUR"
            },
            {
                "date": "20.12.2021",
                "amount": 829.00,
                "category": "Супермаркеты",
                "description": "Лента"
            },
            {
                "date": "20.12.2021",
                "amount": 421.00,
                "category": "Различные товары",
                "description": "Ozon.ru"
            },
            {
                "date": "16.12.2021",
                "amount": -14216.42,
                "category": "ЖКХ",
                "description": "ЖКУ Квартира"
            },
            {
                "date": "16.12.2021",
                "amount": 453.00,
                "category": "Бонусы",
                "description": "Кешбэк за обычные покупки"
            }
        ],
        "currency_rates": [
            {
                "currency": "USD",
                "rate": 73.21
            },
            {
                "currency": "EUR",
                "rate": 87.08
            }
        ],
        "stock_prices": [
            {
                "stock": "AAPL",
                "price": 150.12
            },
            {
                "stock": "AMZN",
                "price": 3173.18
            },
            {
                "stock": "GOOGL",
                "price": 2742.39
            },
            {
                "stock": "MSFT",
                "price": 296.71
            },
            {
                "stock": "TSLA",
                "price": 1007.08
            }
        ]
    }

    with patch('builtins.open', new_callable=MagicMock) as mock_open:
        mock_open.return_value.__enter__.return_value = json.dumps(mock_user_settings)

        with patch('src.utils.read_xls_file', return_value=mock_transactions), \
                patch('src.utils.greetings', return_value="Добрый день"), \
                patch('src.utils.filter_transactions_by_date', return_value=mock_transactions), \
                patch('src.utils.filter_transactions_by_card', return_value=[
                    {"last_digits": "5814", "total_spent": 1262.00, "cashback": 12.62},
                    {"last_digits": "7512", "total_spent": 7.94, "cashback": 0.08}
                ]), \
                patch('src.utils.get_top_five_transactions', return_value=[
                    {"date": "21.12.2021", "amount": 1198.23, "category": "Переводы",
                     "description": "Перевод Кредитная карта. ТП 10.2 RUR"},
                    {"date": "20.12.2021", "amount": 829.00, "category": "Супермаркеты", "description": "Лента"},
                    {"date": "20.12.2021", "amount": 421.00, "category": "Различные товары", "description": "Ozon.ru"},
                    {"date": "16.12.2021", "amount": -14216.42, "category": "ЖКХ", "description": "ЖКУ Квартира"},
                    {"date": "16.12.2021", "amount": 453.00, "category": "Бонусы",
                     "description": "Кешбэк за обычные покупки"}
                ]), \
                patch('src.utils.fetch_exchange_rates', return_value=[
                    {"currency": "USD", "rate": 73.21},
                    {"currency": "EUR", "rate": 87.08}
                ]), \
                patch('src.utils.fetch_stock_prices', return_value=[
                    {"stock": "AAPL", "price": 150.12},
                    {"stock": "AMZN", "price": 3173.18},
                    {"stock": "GOOGL", "price": 2742.39},
                    {"stock": "MSFT", "price": 296.71},
                    {"stock": "TSLA", "price": 1007.08}
                ]):
            result = generate_json_response("dummy_path.xlsx", "2023-01-01")

            # Проверяем результат
            assert result == expected_json
