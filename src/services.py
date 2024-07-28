import datetime
import json
import logging
from typing import List, Dict, Any
from src.utils import setting_log, xls_to_dict


logger = setting_log("services")


def investment_bank(month: str, transactions: List[Dict[str, Any]], limit: int) -> float:
    """Функция, которая возвращает сумму, которую удалось бы отложить в Инвесткопилку"""
    try:
        year_month = datetime.datetime.strptime(month, "%Y-%m")
    except ValueError:
        logger.error("Месяц должен быть указан в формате 'ГГГГ-ММ'")
        raise ValueError("Месяц должен быть указан в формате 'ГГГГ-ММ'")

    # Инициализируем общую сумму, которую нужно сохранить
    total_saved = 0.0

    for transaction in transactions:
        try:
            transaction_date = datetime.datetime.strptime(transaction['Дата операции'], "%d.%m.%Y %H:%M:%S")
            transaction_date = datetime.datetime.strftime(transaction_date, "%Y-%m-%d")
            transaction_date = datetime.datetime.strptime(transaction_date, "%Y-%m-%d")
            # Проверяем, произошла ли транзакция в указанном месяце
            if transaction_date.year == year_month.year and transaction_date.month == year_month.month:
                amount = transaction['Сумма операции']

                # Рассчитываем округленную сумму
                rounded_amount = ((amount + limit - 1) // limit) * limit
                saved_amount = rounded_amount - amount

                # Добавляем к общей сумме
                total_saved += saved_amount

                logger.debug(
                    f"Транзакция на {transaction['Дата операции']} на сумму {amount} ₽, округленная до {rounded_amount} ₽. Сэкономлено: {saved_amount} ₽.")

        except ValueError:
            logger.error(f"Дата транзакции должна быть в формате «ГГГГ-ММ-ДД» для транзакции {transaction}.")
            continue

    logger.info(f"Общая сумма сбережений за месяц {month}: {total_saved} ₽")
    return round(total_saved, 2)


# Sample usage
if __name__ == "__main__":
    transactions = xls_to_dict("../data/operations.xls")
    month = "2024-05"
    limit = 50
    print(f"Total saved: {investment_bank(month, transactions, limit)} ₽")