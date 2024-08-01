import os
from unittest.mock import mock_open, patch

import pandas as pd
import pytest

from src.reports import spending_by_category


@pytest.fixture
def sample_transactions():
    return [
        {"Дата операции": "01.01.2023 12:00:00", "Категория": "Еда", "Сумма": 100},
        {"Дата операции": "15.02.2023 12:00:00", "Категория": "Транспорт", "Сумма": 50},
        {"Дата операции": "10.03.2023 12:00:00", "Категория": "Еда", "Сумма": 200},
        {"Дата операции": "20.04.2023 12:00:00", "Категория": "Еда", "Сумма": 300},
    ]


def test_spending_by_category(sample_transactions):
    df_transactions = pd.DataFrame(sample_transactions)
    current_datetime = "20.04.2023 12:00:00"
    category = "Еда"

    mock_open_func = mock_open()

    with patch("builtins.open", mock_open_func):
        result = spending_by_category(df_transactions, category, current_datetime)

    # Проверяем, что возвращаемый результат соответствует ожидаемому
    expected_result = [
        {"Дата операции": "10.03.2023 12:00:00", "Категория": "Еда", "Сумма": 200},
        {"Дата операции": "20.04.2023 12:00:00", "Категория": "Еда", "Сумма": 300},
    ]
    assert result == expected_result

    # Проверяем, что файл был открыт для записи
    mock_open_func.assert_called_once_with(os.path.abspath("../data/log_file.json"), "w", encoding="utf-8")


# Запуск тестов
if __name__ == "__main__":
    pytest.main()
