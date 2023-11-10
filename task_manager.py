from data_classes import Grade
from abc import ABC, abstractmethod
from yandex_API import ask_yandex_for_time_matrix
from settings import DATA_PATH, LOCATION_MATRIX_FILE
import json
import os
from logger import logger


class TaskHandler(ABC):
    @staticmethod
    @abstractmethod
    def condition(point):
        ...

    params = None


class MotivationTaskHandler(TaskHandler):
    @staticmethod
    def condition(point):
        return point.days_from_last_card > 7 and point.accepted_requests > 0 or point.days_from_last_card > 14

    params = {
        'priority': 3,
        'task_name': 'Выезд на точку для стимулирования выдач',
        'required_grade': Grade.senior,
        'duration': 240
    }


class InstructTaskHandler(TaskHandler):
    @staticmethod
    def condition(point):
        return point.issued_cards > 0 and point.issued_cards / point.accepted_requests < 0.5

    params = {
        'priority': 2,
        'task_name': 'Обучение агента',
        'required_grade': Grade.middle,
        'duration': 120
    }


class DeliveryTaskHandler(TaskHandler):
    @staticmethod
    def condition(point):
        return point.is_connected_yesterday or not point.have_cards_and_materials

    params = {
        'priority': 1,
        'task_name': 'Доставка карт и материалов',
        'required_grade': Grade.junior,
        'duration': 90
    }


class PointMatrix:
    def __init__(self, **data):
        for key, value in data.items():
            self.__setattr__(key, value)


class TaskManager:
    def __init__(self, db_api):
        self.db_api = db_api

    def create_tasks(self):
        """Перебирает список точек в поисках проблемных,
        создаёт на их основе Task"""
        logger.info('Анализ точек на предмет задач')
        points = self.db_api.Point
        for point in points:
            for task_handler in TaskHandler.__subclasses__():
                if task_handler.condition(point):
                    self.db_api.try_to_set_table_row(self.db_api.Task, **task_handler.params, point=point)

    def _set_location_matrix(self):
        location_matrix_file = f'{DATA_PATH}/{LOCATION_MATRIX_FILE}'
        if not os.path.exists(location_matrix_file):
            logger.info('Запрос матрицы путей у яндекс карт...')
            locations = [location.__data__.copy() for location in self.db_api.Location]
            print(locations)
            matrix_data = ask_yandex_for_time_matrix(locations)
            logger.info('Успешно!')
            with open(location_matrix_file, 'w', encoding='utf-8') as file:
                json.dump(matrix_data, file, indent=4, ensure_ascii=False)
            self.location_matrix = PointMatrix(**matrix_data)
        else:
            with open(location_matrix_file, 'r') as file:
                self.location_matrix = PointMatrix(**json.load(file))
        logger.info('Построение маршрутов работникам')

    def create_routes(self):
        """Главный метод, отвечающий за построение маршрутов"""
        self._set_location_matrix()
        for grade in Grade.__dict__.values():
            tasks = self.db_api.Task.select().where
