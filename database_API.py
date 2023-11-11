import openpyxl
from abc import ABC
from peewee import DoesNotExist, IntegrityError
from settings import DEFAULT_PASSWORD, DEFAULT_LOGIN,DATA_PATH ,EXCELL_DATAFILE, CITY
from functions import hash_string
from exceptions import AuthorisationError
from yandex_API import request_coordinates
from excel_parser import ExcelParser
from task_manager import TaskManager
from logger import logger
from tqdm import tqdm


class BaseDBAPI(ABC):
    def __init__(self, database):
        self.database = database
        for table in database.__subclasses__():
            self.__setattr__(table.__name__, table)


class _SetupAPI(BaseDBAPI):
    def parse_data_from_excel(self):
        file_path = f'{DATA_PATH}/{EXCELL_DATAFILE}'
        book = openpyxl.open(file_path, read_only=True)
        excel_parser = ExcelParser(book, self)
        excel_parser.parse_employees()
        excel_parser.parse_points()

    def create_tasks(self):
        task_manager = TaskManager(self)
        task_manager.create_tasks()

    def clear_database(self):
        logger.info('Очистка базы данных')
        self.database.clear_tables()

    def set_database(self):
        logger.info('Инициализация таблиц базы')
        self.database.set_tables()

    def reset_database(self):
        self.clear_database()
        self.set_database()

    def set_admin(self, full_name, login, password):
        self._set_user(full_name, login, password, is_admin=True)
        logger.info(f'Добавлен новый администратор {login}')

    @staticmethod
    def try_to_set_table_row(table, **data):
        try:
            data = table.create(**data)
        except IntegrityError as ex:
            field = str(ex.orig).split('.')[-1]
            logger.debug(f'{ex}\n{data[field]}')

    def set_user_list(self):
        employees = self.Employee.select(self.Employee)
        for employee in employees:
            self._set_user(employee.full_name, DEFAULT_LOGIN + str(employee.id), DEFAULT_PASSWORD, employee=employee)
        logger.info(f'Добавлены сведенья о пользователях')

    def set_location_coordinates(self):
        logger.info('Получение координат точек...')
        locations = self.Location
        for location in tqdm(locations):
            if not location.address.startswith(CITY):
                location.address = f'{CITY}, {location.address}'
                location.save()
            if not (location.latitude and location.longitude):
                try:
                    location.latitude, location.longitude = request_coordinates(location.address)
                except Exception as ex:
                    logger.error(f'Не удалось получить координаты адреса {location.address}\n{ex}')
                location.save()
        logger.info('Успешно!')

    def create_routes(self):
        task_manager = TaskManager(self)
        task_manager.create_routes()

    def _set_user(self, full_name, login, password, is_admin=False, employee=None):
        try:
            self.User.create(full_name=full_name, employee=employee, is_admin=is_admin,
                             login=login, password_hash=hash_string(password))
        except IntegrityError as ex:
            raise AuthorisationError('Пользователь с таким логином уже существует', ex)

    def print_routes(self):
        employees = self.Employee.select()
        for employee in employees:
            select = self.Task.select().join(self.Employee, on=(self.Employee.route == self.Task.route)).where(
                self.Employee.id == employee.id)
            self.Employee.get(self.Employee.route == employee.route)
            print(employee.grade)
            for data in select:
                print(data.point, end='  ')
            print()


class _UserAPI(BaseDBAPI):
    ...


class _AdminAPI(BaseDBAPI):
    ...


class DatabaseAPI(BaseDBAPI):
    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.database.connect()
    _setup = _SetupAPI
    _user = _UserAPI
    _admin = _AdminAPI

    def _get_user_by_login(self, login: str):
        try:
            user = self.User.get(self.User.login == login)
        except DoesNotExist as ex:
            raise AuthorisationError(f'Пользователя с логином {login} нет в базе данных', ex)
        return user

    def setup(self):
        return self._setup(self.database)

    def user(self, login: str, password: str):
        if self._check_user_data(login, password):
            logger.info(f'Полььзователь {login} успешно подключился к базе данных {self.database.name}')
            return self._user(self.database)
        else:
            logger.error(f'Неверный пароль')

    def admin(self, login: str, password: str):
        if not self._check_user_data(login, password):
            logger.error(f'Неверный пароль')
            return 'wrong login or password'
        elif not self._check_if_admin(login):
            logger.error(f'Пользователь {login} не является администратором, доступ запрещён')
            return 'user is not admin'
        else:
            logger.info(f'Администратор {login} успешно подключился к базе данных {self.database.name}')
            return self._admin(self.database)

    def _check_if_admin(self, login: str):
        user = self._get_user_by_login(login)
        return user.is_admin

    def _check_user_data(self, login: str, password: str):
        user = self._get_user_by_login(login)
        print(user.password_hash, hash_string(password))
        return user.password_hash == hash_string(password)


if __name__ == "__main__":
    import os
    from dotenv import load_dotenv

    load_dotenv()

    main_bd_password = os.getenv("MAIN_DB_PASSWORD")
    auth_db_password = os.getenv("AUTHORISATION_DB_PASSWORD")
