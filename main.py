import openpyxl
from task_manager import TaskManager
from excel_parser import ExcelParser
from data_types import *
import os
from dotenv import load_dotenv
from dtabase_API import DatabaseAPI
from yandex_API import ask_yandex_for_time_matrix
from settings import CITY

load_dotenv()

main_bd_password = os.getenv("MAIN_DB_PASSWORD")
auth_db_password = os.getenv("AUTHORISATION_DB_PASSWORD")

employees = EmployeeList(list())
points = PointList(list())
tasks = TaskList(list())
book = openpyxl.open("data.xlsx", read_only=True)
parser = ExcelParser(book, points, employees)
parser.parse_employees()
parser.parse_points()
manager = TaskManager(points, employees, tasks)
manager.create_tasks()


address_set = set()
for employee in employees:
    if not employee.location.adress.startswith(CITY):
        employee.location.adress = f'{CITY}, {employee.location.adress}'
    address_set.add(employee.location.adress)
for point in points:
    if not point.location.adress.startswith(CITY):
        point.location.adress = f'{CITY}, {point.location.adress}'
    address_set.add(point.location.adress)
print(len(list(address_set)))
ask_yandex_for_time_matrix(*list(address_set))

with DatabaseAPI(is_setup=True) as db:
    ...
    # db.set_users([User('Василий', 'avdas', '0000', False),
    #               User('Пётр', 'asdas', '0000', False),
    #               User('Пвел', 'akdas', '0000', True),
    #               User('Григорий', 'andas', '0000', False)])
    # db.set_employees([Employee('Василий', Location('Вызима', id=1), Grade.middle, None),
    #                   Employee('Пётр', Location('Вызима', id=1), Grade.junior, None),
    #                   Employee('Григорий', Location('Вызима', id=1), Grade.senior, None)])
