import openpyxl
from task_manager import TaskManager
from excel_parser import ExcelParser
from data_types import *
import os
from dotenv import load_dotenv
from dtabase_API import DatabaseAPI

load_dotenv()

main_bd_password = os.getenv("MAIN_DB_PASSWORD")
auth_db_password = os.getenv("AUTHORISATION_DB_PASSWORD")




employees = EmployeeList(list())
points = PointList(list())
tasks = TaskList(list())
book = openpyxl.open("data.xlsx", read_only=True)
parser = ExcelParser(book, points, employees)
parser.parse_employees()
parser.parse_points()
manager = TaskManager(points, employees, tasks)
manager.create_tasks()
with DatabaseAPI(is_setup=True) as db:
    db.set_users([User('vasa777', '12345', 'Василий', False)])
