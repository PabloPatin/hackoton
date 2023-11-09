import os
import sqlite3
from sqlite3 import Connection
from os import getenv
from dotenv import load_dotenv
from settings import DATABASE_FILE
from abc import ABC, abstractmethod
from data_types import *
from datetime import datetime


class BaseDBAPI(ABC):
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


class DatabaseAPI:
    class _SetupAPI(BaseDBAPI):
        @staticmethod
        def _hash_password(password):
            return str(hex(hash(password)))

        # def _load_employees(self) -> EmployeeList:
        #     cursor = self.db.cursor()
        #     employees = EmployeeList()
        #     cursor.execute('SELECT full_name, address, latitude, longitude, location_id, grade, id WHERE')

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
            for i, employee in enumerate(employees):
                cursor.execute(f"SELECT id FROM Locations WHERE address=='{employee.location.address}'")
                employees[i].location.id = cursor.fetchone()[0]
            cursor.execute('SELECT uid, full_name FROM Users WHERE is_admin==0')
            for uid, full_name in cursor.fetchall():
                employee = self._find_value_in_datalist(employees, 'full_name', full_name)
                employee.id = uid
                print(employee)
                cursor.execute('INSERT INTO Employees (id, location_id, grade) VALUES (?, ?, ?)',
                               (employee.id, employee.location.id, employee.grade))
            self.db.commit()

        def set_locations(self, locations: LocationList):
            cursor = self.db.cursor()
            cursor.execute("""
                        CREATE TABLE IF NOT EXISTS Locations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        address TEXT UNIQUE,
                        latitude REAL,
                        longitude REAL
                        )
                        """)
            for location in locations:
                cursor.execute('INSERT INTO Locations (id, address, latitude, longitude) VALUES (?, ?, ?, ?)',
                               (location.id, location.address, location.latitude, location.longitude))
            self.db.commit()

        def set_points(self, points: PointList):
            cursor = self.db.cursor()
            cursor.execute("""
                        CREATE TABLE IF NOT EXISTS Points (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        location_id INTEGER NOT NULL,
                        is_connected_yesterday INTEGER,
                        have_cards_and_materials INTEGER,
                        issued_cards INTEGER,
                        accepted_requests INTEGER,
                        days_from_last_card INTEGER
                        )
                        """)
            for i, point in enumerate(points):
                cursor.execute(f"SELECT id FROM Locations WHERE address=='{point.location.address}'")
                points[i].location.id = cursor.fetchone()[0]
            for point in points:
                cursor.execute(
                    'INSERT INTO Points (location_id, is_connected_yesterday, have_cards_and_materials, issued_cards, '
                    'accepted_requests, days_from_last_card) VALUES (?, ?, ?, ?, ?, ?)',
                    (point.location.id, point.is_connected_yesterday, point.have_cards_and_materials,
                     point.issued_cards, point.accepted_requests, point.days_from_last_card))
            self.db.commit()

        def set_tasks(self, tasks: TaskList):
            cursor = self.db.cursor()
            cursor.execute("""
                        CREATE TABLE IF NOT EXISTS Tasks (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        route_id INTEGER DEFAULT NULL,
                        sequence_number INTEGER DEFAULT NULL,
                        point_id INTEGER NOT NULL,
                        time INTEGER NOT NULL,
                        priority INTEGER NOT NULL,
                        task_name TEXT,
                        required_grade TEXT
                        )
                        """)
            for i, task in enumerate(tasks):
                cursor.execute(f"SELECT id FROM Points WHERE location_id=={task.point.location.id}")
                tasks[i].point.id = cursor.fetchone()[0]
            for task in tasks:
                cursor.execute(
                    'INSERT INTO Tasks (point_id, time, priority, task_name, required_grade) VALUES (?, ?, ?, ?, ?)',
                    (task.point.id, task.duration, task.priority, task.task_name, task.required_grade))
            self.db.commit()

        def set_routes(self, employees: EmployeeList):
            cursor = self.db.cursor()
            cursor.execute("""
                        CREATE TABLE IF NOT EXISTS Routes (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        employee_id INTEGER NOT NULL,
                        sequence_len INTEGER NOT NULL,
                        date TEXT
                        )
                        """)
            date = datetime.now().strftime('%d-%m-%Y')
            if employees[0].id is None:
                for i, employee in enumerate(employees):
                    cursor.execute(
                        f'SELECT id FROM Employees, Users WHERE Employees.id=Users.uid AND Users.full_name=="{employee.full_name}"')
                    employees[i].id = cursor.fetchone()[0]
            for employee in employees:
                if len(employee.daily_route) > 0:
                    print(employee.id, len(employee.daily_route), date)
                    cursor.execute('INSERT INTO Routes (employee_id, sequence_len, date) VALUES (?, ?, ?)',
                                   (employee.id, len(employee.daily_route), date))
                    cursor.execute(f'SELECT id FROM Routes WHERE employee_id=={employee.id} AND date=="{date}"')
                    route_id = cursor.fetchone()[0]
                    cursor.execute(f"UPDATE Employees SET daily_route_id={route_id} WHERE id=={employee.id}")
                    for i, task in enumerate(employee.daily_route):
                        cursor.execute(f'UPDATE Tasks SET route_id={route_id}, sequence_number={i} WHERE id=={task.id}')
            self.db.commit()

        def set_finished_tasks(self):
            cursor = self.db.cursor()
            cursor.execute("""
                        CREATE TABLE IF NOT EXISTS FinishedTasks (
                        task_id INTEGER PRIMARY KEY,
                        implementor_id INTEGER NOT NULL,
                        date TEXT
                        )
                        """)
            self.db.commit()

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
