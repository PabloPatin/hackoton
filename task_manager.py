from unused_modules.data_types import *
from database_ORM import *
from task_handlers import task_handlers


class PointMatrix:
    ...


class TaskManager:
    def create_tasks(self):
        """Перебирает список точек в поисках проблемных,
        создаёт на их основе Task"""
        points = Point.select()
        for point in points:
            for task_handler in task_handlers:
                if task_handler.condition(point):
                    task_handler(point)

    def create_routes(self):
        """Главный метод, отвечающий за построение маршрутов"""
