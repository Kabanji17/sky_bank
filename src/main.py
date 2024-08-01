from datetime import datetime

from src.reports import spending_by_category
from src.services import investment_bank
from src.utils import read_xls_file, setting_log
from src.views import generate_json_response

logger = setting_log("main")

df_transactions = read_xls_file("../data/operations.xls")

logger.info("Функция начала свою работу.")
print(
    """Выберите категорию для отображения
        1 Главная страница
        2 Сервис фильтрации по переводам (физическим лицам)
        3 Отчет по категории трат"""
)
menu = ""
while menu not in ("1", "2", "3"):
    menu = input("Введите номер категории\n")
    if menu not in ("1", "2", "3"):
        print("Некорректный ввод.Введите 1, 2, или 3. \n")
    if menu == "1":
        print("Главная страница")
        input_date = input("Введите дату в формате: 'ДД.ММ.ГГГГ ЧЧ:ММ:СС'")
        logger.info("Функция обрабатывает данные транзакций.")
        print(generate_json_response(df_transactions, input_date))
        logger.info("Функция успешно завершила свою работу.")
    elif menu == "2":
        print("Выбран сервис который возвращает сумму, которую удалось бы отложить в Инвесткопилку")
        transactions = df_transactions.to_dict(orient="records")
        month = input("Введите месяц в формате: 'ГГГГ-ММ'")
        limit = int(input("Введите лимит: 10/50/100"))
        logger.info("Функция обрабатывает данные транзакций.")
        print(f"Total saved: {investment_bank(month, transactions, limit)} ₽")
        logger.info("Функция успешно завершила свою работу.")
    elif menu == "3":
        print("Выбран очет по категории трат")
        category = input("Введите категорию трат\n")
        try:
            date = input("Введите дату для формирования отчета в формате 'ДД.ММ.ГГГГ ЧЧ:ММ:СС'")
        except ValueError:
            print("Введена некорректная дата. Была использована текущая дата")
            date = datetime.now()
        logger.info("Функция обрабатывает данные транзакций.")
        result_js = spending_by_category(df_transactions, category, date)
        print(result_js)
        logger.info("Функция успешно завершила свою работу.")
