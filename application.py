from flask import Flask, render_template, redirect, url_for, request
from flask_restful import Api, Resource

from database_ORM import DataBase
from database_API import DatabaseAPI, _UserAPI, _AdminAPI

app = Flask(__name__)
api = Api(app)


@app.route('/')
def redirect_to_login():
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        print(username, password)
        api = DatabaseAPI(DataBase).admin(username, password)
        if isinstance(api, str):
            return 'Доступ запрещён'
        else:
            return redirect(url_for('main'))

    return render_template('auth.html')


@app.route('/main')
def main():
    return render_template('main.html', page_title='Главная')


@app.route('/employees', methods=['GET'])
def employees():
    return render_template('employees.html', page_title='Сотрудники')


@app.route('/admins', methods=['GET'])
def admins():
    return render_template('admins.html', page_title='Администраторы')


@app.route('/points', methods=['GET'])
def points():
    return render_template('points.html', page_title='Точки')


@app.route('/task', methods=['GET'])
def task():
    return render_template('task.html', page_title='Задачи')


if __name__ == '__main__':
    app.run(debug=True)
