import openpyxl
from task_manager import TaskManager
from database_API import DatabaseAPI
from database_ORM import DataBase
from yandex_API import ask_yandex_for_time_matrix
from settings import CITY, DEFAULT_PASSWORD, DEFAULT_LOGIN, DEFAULT_ADMIN, DATABASE_FILE
from exceptions import AuthorisationError


# def set_location_matrix():
#     address_set = set()
#     for employee in employees:
#         if not employee.location.address.startswith(CITY):
#             employee.location.address = f'{CITY}, {employee.location.address}'
#         address_set.add(employee.location.address)
#     for point in points:
#         if not point.location.address.startswith(CITY):
#             point.location.address = f'{CITY}, {point.location.address}'
#         address_set.add(point.location.address)
#     print(len(list(address_set)))
#     ask_yandex_for_time_matrix(*list(address_set))
#

def reset_database_using_excel():
    db_api = DatabaseAPI(DataBase).setup()
    db_api.set_admin('Администратор', 'admin', 'admin')
    db_api.reset_database()
    db_api.parse_data_from_excel()
    db_api.set_user_list()


if __name__ == '__main__':
    reset_database_using_excel()
