import os
import sqlite3
from os import getenv


class BaseAPI:
    ...


class DatabaseAPI:
    def __new__(cls, login='', password='', is_setup=False):
        ...
    class _SetupAPI:
        ...

    class _UserAPI:
        ...

    class _AdminAPI:
        ...
