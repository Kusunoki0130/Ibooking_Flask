import sys
sys.path.append("..")
from ibooking.dao.Entity import db
from app import create_app, auto_task
from werkzeug.security import generate_password_hash


if __name__ == "__main__":
    lst = db['users'].all()
    if len(lst) == 0:
        db['users'].append(id=1, name="admin", password=generate_password_hash("111111"), email="1505979366@qq.com", authority=1)
    app = create_app()
    auto_task()
    print(app.url_map)
    app.run(host='0.0.0.0')
    