import openpyxl
from TaskManager import TaskManager
from ExcelParser import ExcelParser
from data_types import *
import os
from dotenv import load_dotenv
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)



employees = EmployeeList(list())
points = PointList(list())
tasks = TaskList(list())
book = openpyxl.open("Data.xlsx", read_only=True)
parser = ExcelParser(book, points, employees)
parser.parse_employees()
parser.parse_points()
manager = TaskManager(points, employees, tasks)
manager.create_tasks()


