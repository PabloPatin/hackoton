from data_types import Point, Employee, PointList, EmployeeList, Route, Location
from openpyxl import Workbook


class ExcelParser:
    def __init__(self, book: Workbook, points: PointList, employees: EmployeeList):
        self.employees = employees
        self.points = points
        self.book = book
        self.point_sheet = book.worksheets[book.sheetnames.index('Входные данные для анализа')]
        self.employee_sheet = book.worksheets[book.sheetnames.index('Справочник сотрудников')]

    @staticmethod
    def _validate(cls):
        fields = cls.__dict__.copy()
        fields.pop('id')
        if None in fields.values():
            return False
        else:
            return True

    def parse_employees(self):
        for index_row in range(2, self.employee_sheet.max_row + 1):
            employee = Employee(
                self.employee_sheet[index_row][0].value,
                Location(self.employee_sheet[index_row][1].value),
                self.employee_sheet[index_row][2].value,
                Route()
            )
            if self._validate(employee):
                self.employees.append(employee)

    def parse_points(self):
        for index_row in range(2, self.point_sheet.max_row + 1):
            point = Point(
                Location(self.point_sheet[index_row][1].value),
                True if self.point_sheet[index_row][2].value == 'вчера' else False,
                True if self.point_sheet[index_row][3].value == 'да' else False,
                self.point_sheet[index_row][4].value,
                self.point_sheet[index_row][5].value,
                self.point_sheet[index_row][6].value
            )

            if self._validate(point):
                self.points.append(point)
