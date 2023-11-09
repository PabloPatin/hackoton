import openpyxl
from task_manager import TaskManager
from excel_parser import ExcelParser
from data_types import *
import os
from dotenv import load_dotenv
# from database_API import DatabaseAPI
import database_ORM
from database_ORM import *
from yandex_API import ask_yandex_for_time_matrix
from settings import CITY, DEFAULT_PASSWORD, DEFAULT_LOGIN


def set_user_list():
    employees = Employee.select(Employee)
    for employee in employees:
        user = User.select().where(User.employee == employee.id)
        if not user.exists():
            User.create(full_name=employee.full_name, employee=employee, is_admin=False,
                        login=DEFAULT_LOGIN + str(employee.id), password_hash=hex(hash(DEFAULT_PASSWORD)))


def set_admin(full_name, login, password):
    user = User.select().where(User.login == login)
    if not user.exists():
        User.create(full_name=full_name, is_admin=True,
                    login=login, password_hash=hex(hash(password)))


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
    employees = [Employee('Василий', locations[0], Grade.middle, []),
                 Employee('Пётр', locations[1], Grade.junior, []),
                 Employee('Григорий', locations[0], Grade.senior, [])]
    # db.set_employees(employees)
    points = [Point(locations[0], True, False, 7, 9, 5),
              Point(locations[1], False, True, 7, 16, 10)]
    # db.set_points(points)
    tasks = []
    TaskManager(points, employees, tasks).create_tasks()
    employees[0].daily_route.append(tasks[0])
    print(employees[0].daily_route)
    # db.set_tasks(tasks)
    db.set_routes(employees)


if __name__ == '__main__':
    db = SqliteDatabase(DATABASE_FILE)
    BaseDataTable.set_tables()
    set_admin("Липатников Павел Андрееич", 'pashkalop', 'admin')
    book = openpyxl.open("data.xlsx", read_only=True)
    parser = ExcelParser(book)
    parser.parse_employees()
    parser.parse_points()
    set_user_list()

    manager = TaskManager()
    manager.create_tasks()
    manager.create_routes()
