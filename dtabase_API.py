import os
import sqlite3
from sqlite3 import Connection
from os import getenv
from dotenv import load_dotenv
from settings import MAIN_DATABASE
from abc import ABC, abstractmethod
from data_types import *


class BaseDBAPI:
    def __init__(self, db_connection):
        self.db = db_connection

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.db.close()

    @staticmethod
    def _find_value_in_datalist(datalist: list[Dataclass], field, value):
        for data in datalist:
            if data.__dict__[field] == value:
                return data


# class


class DatabaseAPI:
    class _SetupAPI(BaseDBAPI):
        @staticmethod
        def _hash_password(password):
            return str(hex(hash(password)))

        def set_users(self, users: UserList):
            cursor = self.db.cursor()
            cursor.execute("""
                        CREATE TABLE IF NOT EXISTS Users (
                        uid INTEGER PRIMARY KEY AUTOINCREMENT,
                        full_name TEXT NOT NULL UNIQUE,
                        login TEXT UNIQUE,
                        password_hash TEXT,
                        is_admin INTEGER NOT NULL
                        )
                        """)
            for user in users:
                cursor.execute('INSERT INTO Users (full_name, login, password_hash, is_admin) VALUES (?, ?, ?, ?)',
                               (user.full_name, user.login, self._hash_password(user.password), int(user.is_admin)))
            self.db.commit()

        def set_employees(self, employees: EmployeeList):
            cursor = self.db.cursor()
            cursor.execute("""
                        CREATE TABLE IF NOT EXISTS Employees (
                        id INTEGER PRIMARY KEY,
                        location_id INTEGER,
                        daily_route_id INTEGER DEFAULT NULL,
                        grade TEXT
                        )
                        """)
            cursor.execute('SELECT uid, full_name FROM Users WHERE is_admin==0')
            for uid, full_name in cursor.fetchall():
                employee = self._find_value_in_datalist(employees, 'full_name', full_name)
                employee.id = uid
                print(employee)
                cursor.execute('INSERT INTO Employees (id, location_id, grade) VALUES (?, ?, ?)',
                               (employee.id, employee.location.id, employee.grade))
            self.db.commit()

            # for employee in employees:
            #     cursor.execute('INSERT INTO Employees (id, login, password_hash, is_admin) VALUES (?, ?, ?, ?)',
            #                    (user.full_name, user.login, self._hash_password(user.password), int(user.is_admin)))
            # self.db.commit()

    class _UserAPI(BaseDBAPI):
        ...

    class _AdminAPI(BaseDBAPI):
        ...

    def __new__(cls, login='', password='', is_setup=False) -> BaseDBAPI:
        db_connection = sqlite3.connect(MAIN_DATABASE)
        if is_setup:
            return cls._SetupAPI(db_connection)
        elif cls._check_if_admin(db_connection, login, password):
            return cls._AdminAPI(db_connection)
        else:
            return cls._UserAPI(db_connection)

    @staticmethod
    def _check_if_admin(auth_db, login, password):
        ...


if __name__ == "__main__":
    import os
    from dotenv import load_dotenv

    load_dotenv()

    main_bd_password = os.getenv("MAIN_DB_PASSWORD")
    auth_db_password = os.getenv("AUTHORISATION_DB_PASSWORD")
