from abc import ABC
from database_ORM import Task
from unused_modules.data_types import Grade


class TaskHandler(ABC):
    def __new__(cls, point):
        task = Task.create(**cls._params, point=point)
        return task

    _params = None


class MotivationTaskHandler(TaskHandler):
    @staticmethod
    def condition(point):
        return point.days_from_last_card > 7 and point.accepted_requests > 0 or point.days_from_last_card > 14

    _params = {
        'priority': 3,
        'task_name': 'Выезд на точку для стимулирования выдач',
        'required_grade': Grade.senior,
        'duration': 240
    }


class InstructTaskHandler(TaskHandler):
    @staticmethod
    def condition(point):
        return point.issued_cards > 0 and point.issued_cards / point.accepted_requests < 0.5

    _params = {
        'priority': 2,
        'task_name': 'Обучение агента',
        'required_grade': Grade.middle,
        'duration': 120
    }


class DeliveryTaskHandler(TaskHandler):
    @staticmethod
    def condition(point):
        return point.is_connected_yesterday or not point.have_cards_and_materials

    _params = {
        'priority': 1,
        'task_name': 'Доставка карт и материалов',
        'required_grade': Grade.junior,
        'duration': 90
    }


task_handlers = [MotivationTaskHandler, InstructTaskHandler, DeliveryTaskHandler]
