from abc import ABC, abstractmethod
from database_ORM import Task
from data_types import Grade

class TaskHandler(ABC):
    def __new__(cls, *args, **kwargs):
        task = Task.create(**cls._params())
        return task

    @staticmethod
    @abstractmethod
    def _params():
        ...


class MotivationTaskHandler(TaskHandler):
    @staticmethod
    def condition(point):
        return point.days_from_last_card > 7 and point.accepted_requests > 0 or point.days_from_last_card > 14

    @staticmethod
    def _params():
        return
        priority = 3
        task.task_name = 'Выезд на точку для стимулирования выдач'
        task.required_grade = Grade.senior
        task.duration = 240


class InstructTaskHandler(TaskHandler):
    @staticmethod
    def condition(point):
        return point.issued_cards > 0 and point.issued_cards / point.accepted_requests < 0.5

    @staticmethod
    def _params():
        task.priority = 2
        task.task_name = 'Обучение агента'
        task.required_grade = Grade.middle
        task.duration = 120


class DeliveryTaskHandler(TaskHandler):
    @staticmethod
    def condition(point):
        return point.is_connected_yesterday or not point.have_cards_and_materials

    @staticmethod
    def _params():
        task.priority = 1
        task.task_name = 'Доставка карт и материалов'
        task.required_grade = Grade.junior
        task.duration = 90


task_handlers = [MotivationTaskHandler, InstructTaskHandler, DeliveryTaskHandler]