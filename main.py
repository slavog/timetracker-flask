import sqlite3
import os
from flask import Flask, render_template, url_for, request, flash, session, redirect, abort, g
from werkzeug.security import generate_password_hash, check_password_hash
from FDataBase import FDataBase
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from UserLogin import UserLogin

# config
DATABASE = '/tmp/timetracker.db'
DEBUG = True
SECRET_KEY = 'aJDdpaocmHK642111SJfasn18u31'

app = Flask(__name__)
app.config.from_object(__name__)
app.config.update(dict(DATABASE=os.path.join(app.root_path, 'timetracker.db')))


def connect_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn


def create_db():
    db = connect_db()
    with app.open_resource('sq_db.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()
    db.close()


def get_db():
    if not hasattr(g, 'link_db'):
        g.link_db = connect_db()
    return g.link_db


dbase = None


@app.before_request
def before_request():
    global dbase
    db = get_db()
    dbase = FDataBase(db)


login_manager = LoginManager(app)
login_manager.login_view = 'index'
login_manager.login_message = 'Авторизуйтесь для доступа к закрытым страницам'
login_manager.login_message_category = 'success'
@login_manager.user_loader
def load_user(user_id):
    print('load_user')
    return UserLogin().fromDB(user_id, dbase)


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'link db'):
        g.link_db.close()


@app.route('/', methods=["POST", "GET"])
def index():
    if current_user.is_authenticated:
        return redirect(url_for('profile'))
    if request.method == "POST":
        user = dbase.getUserByUsername(request.form['username'])
        if user and check_password_hash(user['psw'], request.form['psw']):
            userlogin = UserLogin().create(user)
            login_user(userlogin)
            return redirect(url_for('profile'))

        flash('Неверная пара логин/пароль', 'error')

    return render_template('index.html', title="Трекер.Времени")


@app.route('/register', methods=["POST", "GET"])
def register():
    if request.method == "POST":
        if request.form['psw'] == request.form['psw2']:
            hash = generate_password_hash(request.form['psw'])
            res = dbase.addUser(request.form['username'], hash)
            if res:
                flash("Вы успешно зарегистрированы", "success")
                return redirect(url_for('register'))
            else:
                flash("Ошибка при добавлении в БД", "error")
        else:
            flash("Повтор пароля указан неверно", "error")
    return render_template('register.html', title="Регистрация")


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из аккаунта', 'success')
    return redirect(url_for('index'))


@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html')


if __name__ == '__main__':
    app.run(debug=True)
