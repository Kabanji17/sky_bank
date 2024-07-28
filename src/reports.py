import re
import pandas as pd
import json
from datetime import datetime, timedelta
from typing import Optional, Callable, Any
from functools import wraps
from utils import setting_log, read_xls_file
from dateutil.relativedelta import relativedelta

# Setting up logging

logger = setting_log("reports")


def save_to_file_decorator(default_filename: str = 'report_default.json'):
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            result = func(*args, **kwargs)

            filename = kwargs.get('filename', default_filename)
            if not filename.endswith('.json'):
                filename += '.json'

            # Convert result to JSON and save it
            try:
                with open(filename, 'w') as f:
                    json.dump(result.to_dict(orient='records'), f, indent=4)
                logger.info(f"Отчет сохранен в {filename}")
            except Exception as e:
                logger.error(f"Не удалось сохранить отчет в {filename}: {e}")

            return result

        return wrapper

    return decorator


@save_to_file_decorator("reports")
def spending_by_category(transactions: pd.DataFrame, category: str, date: Optional[str] = None) -> pd.DataFrame:
    """Функция выводит транзакции за последние 3 месяца из списка транзакций"""
    if date is None:
        date = datetime.now().strftime('%d-%m-%Y')

    date = datetime.strptime(date, '%d-%m-%Y')
    three_months_ago = date - relativedelta(days=90)

    filtered_transactions = transactions[
        (transactions['Категория'] == category) &
        (transactions['Дата платежа'] >= three_months_ago) &
        (transactions['Дата платежа'] <= date)
        ]

    spending = filtered_transactions.groupby('Категория')['Сумма платежа'].sum().reset_index()
    return spending


if __name__ == "__main__":
    transactions = read_xls_file("../data/operations.xls")

    print(spending_by_category(transactions,"Супермаркеты", "31-03-2022"))