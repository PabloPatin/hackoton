from peewee import *
from database_API import DatabaseAPI
from database_ORM import DataBase
from logger import logger


def reset_database_using_excel():
    logger.info('Запущен процесс перезаписи базы данных!!!')
    DataBase.open()
    db_api = DatabaseAPI(DataBase).setup()
    db_api.reset_database()
    db_api.set_admin('Администратор', 'admin', 'admin')
    db_api.parse_data_from_excel()
    db_api.set_user_list()
    db_api.create_tasks()
    db_api.set_location_coordinates()
    db_api.create_routes()
    employees = db_api.Employee.select()
    for employee in employees:
        select = db_api.Task.select().join(db_api.Employee, on=(db_api.Employee.route == db_api.Task.route)).where(
            db_api.Employee.id == employee.id)
        db_api.Employee.get(db_api.Employee.route == employee.route)
        print(employee.grade)
        for data in select:
            print(data.point, end='  ')
        print()
    DataBase.exit()
    logger.info('Процесс завершён')


if __name__ == '__main__':
    reset_database_using_excel()
