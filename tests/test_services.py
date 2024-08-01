import pytest

from src.services import investment_bank


def test_investment_bank():
    """Тестирование функции"""
    transactions = [
        {"Дата операции": "10.07.2023 00:00:00", "Сумма операции": 1712},
        {"Дата операции": "15.07.2023 00:00:00", "Сумма операции": 185},
        {"Дата операции": "20.07.2023 00:00:00", "Сумма операции": 499},
        {"Дата операции": "01.08.2023 00:00:00", "Сумма операции": 130},
    ]
    month = "2023-07"
    limit = 50
    assert investment_bank(month, transactions, limit) == (38.0 + 15.0 + 1.0)


def test_invalid_month_format():
    """Тестирование функции, когда введен неправильный формат месяца"""
    transactions = []
    month = "2023/07"
    limit = 50
    with pytest.raises(ValueError):
        investment_bank(month, transactions, limit)


def test_no_transactions_in_month():
    """Тестирование функции, когда нет введенного в функцию месяца в структуре данных"""
    transactions = [{"Дата операции": "10.08.2023 00:00:00", "Сумма операции": 1712}]
    month = "2023-07"
    limit = 50
    assert investment_bank(month, transactions, limit) == 0.0


def test_different_limits():
    """Тестирование функции с разными лимитами"""
    transactions = [
        {"Дата операции": "10.07.2023 00:00:00", "Сумма операции": 1712},
        {"Дата операции": "15.07.2023 00:00:00", "Сумма операции": 185},
        {"Дата операции": "20.07.2023 00:00:00", "Сумма операции": 499},
    ]
    month = "2023-07"
    assert investment_bank(month, transactions, 10) == (8.0 + 5.0 + 1.0)
    assert investment_bank(month, transactions, 100) == (88.0 + 15.0 + 1.0)


if __name__ == "__main__":
    pytest.main()
