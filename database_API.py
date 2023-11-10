import openpyxl
from abc import ABC
from peewee import DoesNotExist, IntegrityError
from settings import DEFAULT_PASSWORD, DEFAULT_LOGIN, EXCELL_DATAFILE
from exceptions import AuthorisationError
from excel_parser import ExcelParser
from logger import logger


class BaseDBAPI(ABC):
    def __init__(self, database):
        self.database = database
        for table in database.__subclasses__():
            self.__setattr__(table.__name__, table)


class _SetupAPI(BaseDBAPI):
    def parse_data_from_excel(self):
        book = openpyxl.open("data.xlsx", read_only=True)
        excel_parser = ExcelParser(book, self)
        excel_parser.parse_employees()
        excel_parser.parse_points()

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
            table.create(**data)
        except IntegrityError as ex:
            logger.debug(ex)

    def set_user_list(self):
        employees = self.Employee.select(self.Employee)
        for employee in employees:
            self._set_user(employee.full_name, DEFAULT_LOGIN + str(employee.id), DEFAULT_PASSWORD, employee=employee)
        logger.info(f'Добавлены сведенья о пользователях')

    def _set_user(self, full_name, login, password, is_admin=False, employee=None):
        try:
            self.User.create(full_name=full_name, employee=employee, is_admin=is_admin,
                             login=login, password_hash=hex(hash(password)))
        except IntegrityError as ex:
            raise AuthorisationError('Пользователь с таким логином уже существует', ex)

    # @staticmethod
    # def _hash_password(password):
    #     return str(hex(hash(password)))
    #
    # # def _load_employees(self) -> EmployeeList:
    # #     cursor = self.db.cursor()
    # #     employees = EmployeeList()
    # #     cursor.execute('SELECT full_name, address, latitude, longitude, location_id, grade, id WHERE')
    #
    # def set_users(self, users: UserList):
    #     cursor = self.db.cursor()
    #     cursor.execute("""
    #                 CREATE TABLE IF NOT EXISTS Users (
    #                 uid INTEGER PRIMARY KEY AUTOINCREMENT,
    #                 full_name TEXT NOT NULL UNIQUE,
    #                 login TEXT UNIQUE,
    #                 password_hash TEXT,
    #                 is_admin INTEGER NOT NULL
    #                 )
    #                 """)
    #     for user in users:
    #         cursor.execute('INSERT INTO Users (full_name, login, password_hash, is_admin) VALUES (?, ?, ?, ?)',
    #                        (user.full_name, user.login, self._hash_password(user.password), int(user.is_admin)))
    #     self.db.commit()
    #
    # def set_employees(self, employees: EmployeeList):
    #     cursor = self.db.cursor()
    #     cursor.execute("""
    #                 CREATE TABLE IF NOT EXISTS Employees (
    #                 id INTEGER PRIMARY KEY,
    #                 location_id INTEGER,
    #                 daily_route_id INTEGER DEFAULT NULL,
    #                 grade TEXT
    #                 )
    #                 """)
    #     for i, employee in enumerate(employees):
    #         cursor.execute(f"SELECT id FROM Locations WHERE address=='{employee.location.address}'")
    #         employees[i].location.id = cursor.fetchone()[0]
    #     cursor.execute('SELECT uid, full_name FROM Users WHERE is_admin==0')
    #     for uid, full_name in cursor.fetchall():
    #         employee = self._find_value_in_datalist(employees, 'full_name', full_name)
    #         employee.id = uid
    #         print(employee)
    #         cursor.execute('INSERT INTO Employees (id, location_id, grade) VALUES (?, ?, ?)',
    #                        (employee.id, employee.location.id, employee.grade))
    #     self.db.commit()
    #
    # def set_locations(self, locations: LocationList):
    #     cursor = self.db.cursor()
    #     cursor.execute("""
    #                 CREATE TABLE IF NOT EXISTS Locations (
    #                 id INTEGER PRIMARY KEY AUTOINCREMENT,
    #                 address TEXT UNIQUE,
    #                 latitude REAL,
    #                 longitude REAL
    #                 )
    #                 """)
    #     for location in locations:
    #         cursor.execute('INSERT INTO Locations (id, address, latitude, longitude) VALUES (?, ?, ?, ?)',
    #                        (location.id, location.address, location.latitude, location.longitude))
    #     self.db.commit()
    #
    # def set_points(self, points: PointList):
    #     cursor = self.db.cursor()
    #     cursor.execute("""
    #                 CREATE TABLE IF NOT EXISTS Points (
    #                 id INTEGER PRIMARY KEY AUTOINCREMENT,
    #                 location_id INTEGER NOT NULL,
    #                 is_connected_yesterday INTEGER,
    #                 have_cards_and_materials INTEGER,
    #                 issued_cards INTEGER,
    #                 accepted_requests INTEGER,
    #                 days_from_last_card INTEGER
    #                 )
    #                 """)
    #     for i, point in enumerate(points):
    #         cursor.execute(f"SELECT id FROM Locations WHERE address=='{point.location.address}'")
    #         points[i].location.id = cursor.fetchone()[0]
    #     for point in points:
    #         cursor.execute(
    #             'INSERT INTO Points (location_id, is_connected_yesterday, have_cards_and_materials, issued_cards, '
    #             'accepted_requests, days_from_last_card) VALUES (?, ?, ?, ?, ?, ?)',
    #             (point.location.id, point.is_connected_yesterday, point.have_cards_and_materials,
    #              point.issued_cards, point.accepted_requests, point.days_from_last_card))
    #     self.db.commit()
    #
    # def set_tasks(self, tasks: TaskList):
    #     cursor = self.db.cursor()
    #     cursor.execute("""
    #                 CREATE TABLE IF NOT EXISTS Tasks (
    #                 id INTEGER PRIMARY KEY AUTOINCREMENT,
    #                 route_id INTEGER DEFAULT NULL,
    #                 sequence_number INTEGER DEFAULT NULL,
    #                 point_id INTEGER NOT NULL,
    #                 time INTEGER NOT NULL,
    #                 priority INTEGER NOT NULL,
    #                 task_name TEXT,
    #                 required_grade TEXT
    #                 )
    #                 """)
    #     for i, task in enumerate(tasks):
    #         cursor.execute(f"SELECT id FROM Points WHERE location_id=={task.point.location.id}")
    #         tasks[i].point.id = cursor.fetchone()[0]
    #     for task in tasks:
    #         cursor.execute(
    #             'INSERT INTO Tasks (point_id, time, priority, task_name, required_grade) VALUES (?, ?, ?, ?, ?)',
    #             (task.point.id, task.duration, task.priority, task.task_name, task.required_grade))
    #     self.db.commit()
    #
    # def set_routes(self, employees: EmployeeList):
    #     cursor = self.db.cursor()
    #     cursor.execute("""
    #                 CREATE TABLE IF NOT EXISTS Routes (
    #                 id INTEGER PRIMARY KEY AUTOINCREMENT,
    #                 employee_id INTEGER NOT NULL,
    #                 sequence_len INTEGER NOT NULL,
    #                 date TEXT
    #                 )
    #                 """)
    #     date = datetime.now().strftime('%d-%m-%Y')
    #     if employees[0].id is None:
    #         for i, employee in enumerate(employees):
    #             cursor.execute(
    #                 f'SELECT id FROM Employees, Users WHERE Employees.id=Users.uid AND Users.full_name=="{employee.full_name}"')
    #             employees[i].id = cursor.fetchone()[0]
    #     for employee in employees:
    #         if len(employee.daily_route) > 0:
    #             print(employee.id, len(employee.daily_route), date)
    #             cursor.execute('INSERT INTO Routes (employee_id, sequence_len, date) VALUES (?, ?, ?)',
    #                            (employee.id, len(employee.daily_route), date))
    #             cursor.execute(f'SELECT id FROM Routes WHERE employee_id=={employee.id} AND date=="{date}"')
    #             route_id = cursor.fetchone()[0]
    #             cursor.execute(f"UPDATE Employees SET daily_route_id={route_id} WHERE id=={employee.id}")
    #             for i, task in enumerate(employee.daily_route):
    #                 cursor.execute(f'UPDATE Tasks SET route_id={route_id}, sequence_number={i} WHERE id=={task.id}')
    #     self.db.commit()
    #
    # def set_finished_tasks(self):
    #     cursor = self.db.cursor()
    #     cursor.execute("""
    #                 CREATE TABLE IF NOT EXISTS FinishedTasks (
    #                 task_id INTEGER PRIMARY KEY,
    #                 implementor_id INTEGER NOT NULL,
    #                 date TEXT
    #                 )
    #                 """)
    #     self.db.commit()


class _UserAPI(BaseDBAPI):
    ...


class _AdminAPI(BaseDBAPI):
    ...


class DatabaseAPI(BaseDBAPI):
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
        logger.info(f'Перезапись базы данных из файла {EXCELL_DATAFILE}')
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
        elif self._check_if_admin(login):
            logger.error(f'Пользователь {login} не является администратором, доступ запрещён')
        else:
            logger.info(f'Администратор {login} успешно подключился к базе данных {self.database.name}')
            return self._admin(self.database)

    def _check_if_admin(self, login: str):
        user = self._get_user_by_login(login)
        return user.is_admin

    def _check_user_data(self, login: str, password: str):
        user = self._get_user_by_login(login)
        return user.password_hash == hex(hash(password))


if __name__ == "__main__":
    import os
    from dotenv import load_dotenv

    load_dotenv()

    main_bd_password = os.getenv("MAIN_DB_PASSWORD")
    auth_db_password = os.getenv("AUTHORISATION_DB_PASSWORD")
