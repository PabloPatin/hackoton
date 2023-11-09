from abc import ABC

from peewee import *
from settings import DATABASE_FILE


class BaseDataTable(Model):
    class Meta:
        database = SqliteDatabase(DATABASE_FILE)

    @classmethod
    def set_tables(cls):
        cls._meta.database.create_tables(cls.__subclasses__())


class Route(BaseDataTable):
    id = AutoField(primary_key=True)
    length = IntegerField(null=False)
    date = DateField(formats='%Y-%m-%d')
    is_completed = BooleanField(default=False)


class Location(BaseDataTable):
    id = AutoField(primary_key=True)
    address = TextField(null=False, unique=True)
    latitude = DoubleField(null=True)
    longitude = DoubleField(null=True)


class Point(BaseDataTable):
    id = AutoField(primary_key=True)
    location = ForeignKeyField(Location, null=False, on_update='CASCADE')
    is_connected_yesterday = BooleanField()
    have_cards_and_materials = BooleanField()
    days_from_last_card = IntegerField()
    accepted_requests = IntegerField()
    issued_cards = IntegerField()


class Employee(BaseDataTable):
    id = AutoField(primary_key=True)
    route = ForeignKeyField(Route, backref='implementor', unique=True, on_update='CASCADE', null=True)
    grade = CharField(10)
    location = ForeignKeyField(Location, null=False)
    full_name = CharField(100, null=False)


class User(BaseDataTable):
    uid = AutoField(primary_key=True)
    full_name = ForeignKeyField(Employee.full_name, null=True, on_update='CASCADE')
    login = CharField(64, unique=True)
    password_hash = TextField(null=False)
    employee = ForeignKeyField(Employee, null=True, backref='user', on_update='CASCADE')
    is_admin = BooleanField(null=False)


class Task(BaseDataTable):
    id = AutoField(primary_key=True)
    route = ForeignKeyField(Route, on_update='CASCADE', backref='tasks', null=True)
    sequence_number = IntegerField(null=True)
    point = ForeignKeyField(Point, on_update='CASCADE')
    task_name = CharField(100)
    duration = IntegerField()
    priority = CharField(10)
    required_grade = CharField(10)
    finish_time = DateTimeField(formats='%Y-%m-%d %M:%s', null=True)



def set_database(db: SqliteDatabase):
    db.connect()
    db.create_tables([Location, Task, User, Point, Employee, Route])
    db.close()
