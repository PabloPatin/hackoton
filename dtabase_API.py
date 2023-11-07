import os
import sqlite3
from sqlite3 import Connection
from os import getenv
from dotenv import load_dotenv
from settings import MAIN_DATABASE, AUTH_DATABASE
from abc import ABC, abstractmethod
from data_types import *


class BaseDBAPI:
    def __init__(self, *connections):
        self._connections = connections

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        for connection in self._connections:
            connection.close()


class DatabaseAPI:
    class _SetupAPI(BaseDBAPI):
        def __init__(self, main_db_connection, auth_db_connection):
            super().__init__(main_db_connection, auth_db_connection)
            self.main: Connection = main_db_connection
            self.auth: Connection = auth_db_connection

        @staticmethod
        def _hash_password(password):
            return str(hex(hash(password)))

        def set_users(self, users: list[User]):
            cursor = self.auth.cursor()
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS Users (
            uid INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            login TEXT UNIQUE,
            password_hash TEXT,
            is_admin INTEGER NOT NULL
            )
            """)
            for user in users:
                cursor.execute('INSERT INTO Users (full_name, login, password_hash, is_admin) VALUES (?, ?, ?)',
                               (user.full_name, user.login, self._hash_password(user.password), int(user.is_admin)))
            self.auth.commit()

    class _UserAPI(BaseDBAPI):
        def __init__(self, main_db_connection):
            super().__init__(main_db_connection)
            self.main = main_db_connection

    class _AdminAPI(BaseDBAPI):
        def __init__(self, main_db_connection, auth_db_connection):
            super().__init__(main_db_connection, auth_db_connection)
            self.main = main_db_connection
            self.auth = auth_db_connection

    def __new__(cls, login='', password='', is_setup=False):
        auth_db_connection = sqlite3.connect(AUTH_DATABASE)
        main_db_connection = sqlite3.connect(MAIN_DATABASE)
        if is_setup:
            return cls._SetupAPI(main_db_connection, auth_db_connection)
        else:
            if cls._check_if_admin(auth_db_connection, login, password):
                return cls._AdminAPI(main_db_connection, auth_db_connection)
            else:
                auth_db_connection.close()
                return cls._UserAPI(main_db_connection)

    @staticmethod
    def _check_if_admin(auth_db, login, password):
        ...


if __name__ == "__main__":
    import os
    from dotenv import load_dotenv

    load_dotenv()

    main_bd_password = os.getenv("MAIN_DB_PASSWORD")
    auth_db_password = os.getenv("AUTHORISATION_DB_PASSWORD")
