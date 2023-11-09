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
