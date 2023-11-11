from data_classes import Grade
from abc import ABC, abstractmethod
from yandex_API import ask_yandex_for_time_matrix
from settings import DATA_PATH, LOCATION_MATRIX_FILE, WORK_TIME_MIN
import json
import os
from logger import logger
from datetime import date


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
        self.location_ids: list = None
        self.time_matrix: list[list] = None
        for key, value in data.items():
            self.__setattr__(key, value)

    def find_location(self, location_id):
        return self.location_ids.index(location_id)

    def delete(self, location_id):
        index = self.location_ids.index(location_id)
        self.location_ids.pop(index)
        self.time_matrix.pop(index)
        for i in self.time_matrix:
            i.pop(index)

    def __repr__(self):
        string = ''
        for i in self.location_ids:
            string += str(i) + '\t'
        string += '\n'
        for i in self.time_matrix:
            for j in i:
                string += str(j) + '\t'
            string += '\n'
        return string


class TaskManager:
    def __init__(self, db_api):
        self.db_api = db_api
        self.tasks = self.db_api.Task

    class Worker:
        def __init__(self, id, location_id, is_active=True):
            self.id = id
            self.woorktime = WORK_TIME_MIN
            self.location_id = location_id
            self.is_active = is_active
            self.route = list()

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
            matrix_data = ask_yandex_for_time_matrix(locations)
            logger.info('Успешно!')
            with open(location_matrix_file, 'w', encoding='utf-8') as file:
                json.dump(matrix_data, file, indent=4, ensure_ascii=False)
            self.location_matrix = PointMatrix(**matrix_data)
        else:
            with open(location_matrix_file, 'r') as file:
                self.location_matrix = PointMatrix(**json.load(file))
        logger.info('Построение маршрутов работникам')

    def _count_worker(self, worker: Worker, locations: list[int]):
        worker_location = self.location_matrix.find_location(worker.location_id)
        min_time = float('inf')
        best_location = None
        for location in locations:
            task_location = self.location_matrix.find_location(location)
            boof_time = self.location_matrix.time_matrix[worker_location][task_location]
            if boof_time < min_time:
                min_time = boof_time
                best_location = location
        return best_location

    def _count_routes(self, workers: list[Worker], locations: list[int], task_time):
        # Пока хоть одини рабочей может куда-то поехать и есть задачи на этой итерации
        while any((worker.is_active for worker in workers)) and len(locations) > 0:
            best_time = float('inf')
            best_point = None
            worker_step = None
            # находим рабочего,которому ближе всего ехать
            for worker in workers:
                if worker.is_active:
                    best_point = self._count_worker(worker, locations)
                    worker_location = self.location_matrix.find_location(worker.location_id)
                    task_location = self.location_matrix.find_location(best_point)
                    new_best_time = self.location_matrix.time_matrix[worker_location][task_location]
                    if new_best_time < best_time:
                        best_time = new_best_time
                        worker_step = worker
            worker_step.woorktime -= best_time
            worker_step.woorktime -= task_time
            if worker_step.woorktime < 0:
                worker_step.is_active = False
            # print(best_time, worker_step.location_id, best_point)
            worker_step.location_id = best_point
            worker_step.route.append(best_point)
            locations.remove(best_point)
            # for i in workers:
            #     print(i.woorktime, end=' ')
            # print()
        return workers

    def create_routes(self):
        """Главный метод, отвечающий за построение маршрутов"""
        logger.info('Построение маршрутов сотрудников')
        self._set_location_matrix()
        task_points = dict()
        task_time = dict()
        for grade in Grade.grades:
            task_points[grade] = []
            tasks = self.tasks.select().where(self.tasks.required_grade == grade)
            for task in tasks:
                task_time[grade] = task.duration
                task_points[grade].append(task.point.location.id)

        for grade in Grade.grades[::-1]:
            grades = Grade.grades[Grade.grades.index(grade):]
            employees = self.db_api.Employee.select().where(self.db_api.Employee.grade == grade)
            workers = [self.Worker(employee.id, employee.location.id, is_active=True) for employee in employees]
            for task_grade in grades:
                workers = self._count_routes(workers, task_points[task_grade], task_time[task_grade])
            for worker in workers:
                route = self.db_api.Route.create(length=len(worker.route), date=date.today())
                employee = self.db_api.Employee.get(self.db_api.Employee.id == worker.id)
                employee.route = route
                employee.save()
                i = 1
                for point in worker.route:
                    tasks = self.tasks.select().join(self.db_api.Point).join(self.db_api.Location).where(
                        self.db_api.Location.id == point)
                    for task in tasks:
                        task.route = route
                        task.sequence_number = i
                        i += 1
                        task.save()
