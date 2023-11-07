from flask import Blueprint, Flask, redirect, render_template
from flask_login import current_user
from ibooking.apps.user.user_view import user_app, login_manager
from ibooking.apps.room.room_view import room_app
from ibooking.apps.book.book_view import book_app, auto_00, auto_10, auto_15, auto_45, minute_00, minute_10, minute_15, minute_45
from ibooking.dao.Entity import db
from werkzeug.security import generate_password_hash
import logging

def create_app(is_testing:bool=False):

    app = Flask(__name__, static_folder="static", static_url_path="/static",template_folder="template")
    app.config["SECRET_KEY"] = "1145141919810"

    app.register_blueprint(user_app, url_prefix="/user")
    app.register_blueprint(room_app, url_prefix="/room")
    app.register_blueprint(book_app, url_prefix="/book")


    db.testing = is_testing
    app.testing = is_testing

    lst = db['users'].all()
    if len(lst) == 0:
        db['users'].append(id=1, name="admin", password=generate_password_hash("111111"), email="1505979366@qq.com", authority=1)
        db['users'].append(id=2, name="Alice", password=generate_password_hash("111111"), email="22210240132@m.fudan.edu.cn", authority=0)

    login_manager.init_app(app)


    @app.route("/", methods=['GET'])
    def index():
        if current_user.is_authenticated:
            return redirect("/room/admin/page")
        else:
            return redirect("/user/admin/login")

    @app.route("/map", methods=['GET'])
    def map():
        return render_template('map.html')

    return app 


def auto_task():
    auto_00.start()
    auto_10.start()
    auto_15.start()
    auto_45.start()