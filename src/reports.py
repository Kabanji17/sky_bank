import json
import os.path
from datetime import datetime
from functools import wraps
from typing import Any, Callable

import pandas as pd
from dateutil.relativedelta import relativedelta

from src.utils import read_xls_file, setting_log

logger = setting_log("reports")


def save_to_file_decorator(filename: str = "log_file.json"):
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            logger.info("Декоратор получает результат работы декорируемой функции.")
            result = func(*args, **kwargs)
            logger.info("Декоратор записывает полученный результат в файл.")
            full_path = os.path.abspath(filename)
            with open(full_path, "w", encoding="utf-8") as file:
                json.dump(result, file, ensure_ascii=False, indent=4)
            logger.info("Декоратор успешно завершил свою работу.")
            return result

        return wrapper

    return decorator


def filter_transactions_by_category(transactions: list[dict], category: str) -> list[dict]:
    """Фильтрует транзакции по заданной категории и возвращает DataFrame."""
    filtered_transactions = [transaction for transaction in transactions if transaction["Категория"] == category]
    return filtered_transactions


@save_to_file_decorator("../data/log_file.json")
def spending_by_category(df_transactions: pd.DataFrame, category: str, current_datetime: str) -> str:
    """Функция, возвращающая транзакции за 3 месяца по определенной категории."""
    all_transactions = df_transactions.to_dict(orient="records")
    # Определяем дату 3 месяца назад
    date = datetime.strptime(current_datetime, "%d.%m.%Y %H:%M:%S")
    three_months_ago = date - relativedelta(months=3)
    print(f"Начало отсчета периода: {datetime.strftime(three_months_ago, "%d.%m.%Y %H:%M:%S")}")
    print(f"Конец отсчета периода: {current_datetime}")

    transactions_3_months = []
    for transaction in all_transactions:
        date_str = transaction.get("Дата операции")
        if date_str:
            try:
                # Преобразуем строку с датой в объект datetime
                transaction_date = datetime.strptime(date_str, "%d.%m.%Y %H:%M:%S")
                # Проверяем, попадает ли дата транзакции в нужный диапазон
                if three_months_ago <= transaction_date <= date:
                    transactions_3_months.append(transaction)
                    # print(transactions_3_months['Дата операции'])
            except ValueError as e:
                print(f"Ошибка преобразования даты: {e}")
    if not transactions_3_months:
        return json.dumps([], ensure_ascii=False, indent=4)

    # Фильтруем транзакции по категории
    result = filter_transactions_by_category(transactions_3_months, category)
    if not result:
        list_of_dicts = []
    else:
        list_of_dicts = result
    return list_of_dicts


if __name__ == "__main__":
    transactions = read_xls_file("../data/operations.xls")

    print(spending_by_category(transactions, "Экосистема Яндекс", "31.03.2024 00:00:00"))
