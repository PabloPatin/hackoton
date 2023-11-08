from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import Protocol


class Dataclass(Protocol):
    __dict__ = ...


class Grade:
    senior = "Синьор"
    middle = "Мидл"
    junior = "Джун"


@dataclass
class Location:
    address: str
    latitude: float = None
    longitude: float = None
    id: int = None


@dataclass
class Point:
    location: Location
    is_connected_yesterday: bool
    have_cards_and_materials: bool
    days_from_last_card: int
    accepted_requests: int
    issued_cards: int
    id: int = None


@dataclass
class Task:
    point: Point
    priority: int = None
    time: int = None
    task_name: str = None
    is_finished: bool = False
    route: 'Route' = None
    required_grade: Grade = None
    id: int = None


class TaskHandler(ABC):
    def __new__(cls, *args, **kwargs):
        task = Task(*args, **kwargs)
        cls._set_params(task)
        return task

    @staticmethod
    @abstractmethod
    def _set_params(task):
        ...


class MotivationTaskHandler(TaskHandler):
    @staticmethod
    def condition(point):
        return point.days_from_last_card > 7 and point.accepted_requests > 0 or point.days_from_last_card > 14

    @staticmethod
    def _set_params(task):
        task.priority = 3
        task.task_name = 'Выезд на точку для стимулирования выдач'
        task.required_grade = Grade.senior
        task.time = 240


class InstructTaskHandler(TaskHandler):
    @staticmethod
    def condition(point):
        return point.issued_cards > 0 and point.issued_cards / point.accepted_requests < 0.5

    @staticmethod
    def _set_params(task):
        task.priority = 2
        task.task_name = 'Обучение агента'
        task.required_grade = Grade.middle
        task.time = 120


class DeliveryTaskHandler(TaskHandler):
    @staticmethod
    def condition(point):
        return point.is_connected_yesterday or not point.have_cards_and_materials

    @staticmethod
    def _set_params(task):
        task.priority = 1
        task.task_name = 'Доставка карт и материалов'
        task.required_grade = Grade.junior
        task.time = 90


task_handlers = [MotivationTaskHandler, InstructTaskHandler, DeliveryTaskHandler]


@dataclass
class Employee:
    full_name: str
    location: Location
    grade: str
    daily_route: 'Route'
    id: int = None


@dataclass
class User:
    full_name: str
    login: str
    password: str
    is_admin: bool
    uid: int = None


TaskList = Route = list[Task]
EmployeeList = list[Employee]
PointList = list[Point]
UserList = list[User]
LocationList = list[Location]

if __name__ == '__main__':
    vasa = Employee('Василий', None, None, None)
    print(vasa.__dict__)
