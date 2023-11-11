from peewee import *
from settings import DATABASE_FILE, DATA_PATH


class DataBase(Model):
    name = DATABASE_FILE

    class Meta:
        database = SqliteDatabase(f'{DATA_PATH}/{DATABASE_FILE}')

    @classmethod
    def set_tables(cls):
        cls._meta.database.create_tables(cls.__subclasses__())

    # @classmethod
    # def renew_tables(cls):
    #     cls._meta.database.create_tables(cls.__subclasses__(), safe=True)

    @classmethod
    def clear_tables(cls):
        cls._meta.database.drop_tables(cls.__subclasses__())

    @classmethod
    def exit(cls):
        cls._meta.database.close()

    @classmethod
    def open(cls):
        cls._meta.database.connect()


class Route(DataBase):
    id = AutoField(primary_key=True)
    length = IntegerField(null=False)
    date = DateField(formats='%Y-%m-%d')
    is_completed = BooleanField(default=False)


class Location(DataBase):
    id = AutoField(primary_key=True)
    address = TextField(null=False, unique=True)
    latitude = DoubleField(null=True)
    longitude = DoubleField(null=True)


class Point(DataBase):
    id = AutoField(primary_key=True)
    location = ForeignKeyField(Location, null=False, on_update='CASCADE')
    is_connected_yesterday = BooleanField()
    have_cards_and_materials = BooleanField()
    days_from_last_card = IntegerField()
    accepted_requests = IntegerField()
    issued_cards = IntegerField()


class Employee(DataBase):
    id = AutoField(primary_key=True)
    route = ForeignKeyField(Route, backref='implementor', unique=True, on_update='CASCADE', null=True)
    grade = CharField(10)
    location = ForeignKeyField(Location, null=False)
    full_name = CharField(100, null=False, unique=True)


class User(DataBase):
    uid = AutoField(primary_key=True)
    full_name = ForeignKeyField(Employee.full_name, null=True, on_update='CASCADE')
    login = CharField(64, unique=True)
    password_hash = TextField(null=False)
    employee = ForeignKeyField(Employee, null=True, backref='user', on_update='CASCADE')
    is_admin = BooleanField(null=False)


class Task(DataBase):
    id = AutoField(primary_key=True)
    route = ForeignKeyField(Route, on_update='CASCADE', backref='tasks', null=True)
    sequence_number = IntegerField(null=True)
    point = ForeignKeyField(Point, on_update='CASCADE', unique=False)
    task_name = CharField(100)
    duration = IntegerField()
    priority = CharField(10)
    required_grade = CharField(10)
    finish_time = DateTimeField(formats='%Y-%m-%d %M:%s', null=True)
