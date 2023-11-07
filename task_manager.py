from data_types import *


class PointMatrix:
    ...


class TaskManager:
    def __init__(self, points, employees, tasks):
        self.points = points
        self.employees = employees
        self.tasks = tasks

    def create_tasks(self):
        """Перебирает список точек в поисках проблемных,
        создаёт на их основе Task и заполняет список tasks"""
        for point in self.points:
            for task_handler in task_handlers:
                if task_handler.condition(point):
                    self.tasks.append(task_handler(point))

    def create_routes(self):
        """Главный метод, отвечающий за построение маршрутов"""
