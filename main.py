import openpyxl
from task_manager import TaskManager
from excel_parser import ExcelParser
from data_types import *
import os
from dotenv import load_dotenv
from dtabase_API import DatabaseAPI, BaseDBAPI
from yandex_API import ask_yandex_for_time_matrix
from settings import CITY

load_dotenv()

main_bd_password = os.getenv("MAIN_DB_PASSWORD")
auth_db_password = os.getenv("AUTHORISATION_DB_PASSWORD")

employees = EmployeeList()
points = PointList()
tasks = TaskList()
users = UserList()
locations = LocationList()

book = openpyxl.open("data.xlsx", read_only=True)
parser = ExcelParser(book, points, employees)
parser.parse_employees()
parser.parse_points()
manager = TaskManager(points, employees, tasks)
manager.create_tasks()
manager.create_routes()


def set_location_matrix():
    address_set = set()
    for employee in employees:
        if not employee.location.address.startswith(CITY):
            employee.location.address = f'{CITY}, {employee.location.address}'
        address_set.add(employee.location.address)
    for point in points:
        if not point.location.address.startswith(CITY):
            point.location.address = f'{CITY}, {point.location.address}'
        address_set.add(point.location.address)
    print(len(list(address_set)))
    ask_yandex_for_time_matrix(*list(address_set))


def set_database(db):
    users = [User('Василий', 'avdas', '0000', False),
             User('Пётр', 'asdas', '0000', False),
             User('Пвел', 'admin', 'admin', True),
             User('Григорий', 'andas', '0000', False)]
    # db.set_users(users)
    locations = [Location('Велен', 12.56, 15.031),
                 Location('Вызима', 12.019202, 15.213123)]
    # db.set_locations(locations)
    employees = [Employee('Василий', locations[0], Grade.middle, None),
                 Employee('Пётр', locations[1], Grade.junior, None),
                 Employee('Григорий', locations[0], Grade.senior, None)]
    # db.set_employees(employees)
    points = [Point(locations[0], True, False, 7, 9, 5),
              Point(locations[1], False, True, 7, 16, 10)]
    # db.set_points(points)
    tasks = []
    TaskManager(points, employees, tasks).create_tasks()
    # db.set_tasks(tasks)
    db.set_routes(employees)


with DatabaseAPI(is_setup=True) as db:
    ...
    # set_database(db)
