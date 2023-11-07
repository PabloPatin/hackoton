from data_types import Point, Employee, PointList, EmployeeList, Route, Location
from openpyxl import Workbook


class ExcelParser:
    def __init__(self, book: Workbook, points: PointList, employees: EmployeeList):
        self.employees = employees
        self.points = points
        self.book = book
        self.point_sheet = book.worksheets[0]
        self.employee_sheet = book.worksheets[2]

    @staticmethod
    def _validate(cls):
        if None in cls.__dict__.values():
            return False
        else:
            return True

    def parse_employees(self):
        for index_row in range(1, self.employee_sheet.max_row + 1):
            employee = Employee(
                self.employee_sheet[index_row][0].value,
                Location(self.employee_sheet[index_row][1].value),
                self.employee_sheet[index_row][2].value,
                Route(list())
            )
            if self._validate(employee):
                self.employees.append(employee)

    def parse_points(self):
        for index_row in range(2, self.point_sheet.max_row + 1):
            point = Point(
                        self.point_sheet[index_row][1].value,
                        True if self.point_sheet[index_row][2].value == 'вчера' else False,
                        True if self.point_sheet[index_row][3].value == 'да' else False,
                        self.point_sheet[index_row][4].value,
                        self.point_sheet[index_row][5].value,
                        self.point_sheet[index_row][6].value
            )

            if self._validate(point):
                self.points.append(point)
