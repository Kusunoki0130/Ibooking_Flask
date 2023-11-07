import base64
from .user_service import *
from flask import Blueprint, jsonify, request, session, render_template
from flask_login import login_required, current_user, logout_user, login_user
from ibooking.utils.security import authority_requried, User
from flask_login import LoginManager

login_manager = LoginManager()

user_app = Blueprint('user', __name__, static_url_path="/static")


@login_manager.user_loader
def load(user_id):
    return User.get(user_id)

# 登录
@user_app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        name = request.form.get("name")
        password = request.form.get("password")
        user_dict = get_user(name=name)
        if user_dict is None:
            return jsonify({
                'success': False,
                'msg': "username invalid"
            })
        user = User(user_dict)
        if not user.verify_password(rsa.decrypt(base64.b64decode(password.encode("utf-8")), rsa_key.private_key).decode('utf-8')):
            return jsonify({
                'success': False,
                'msg': "password invalid"
            })
        login_user(user)
        return jsonify({
            'success': True,
            'msg': "login success"
        })
    print(rsa_key.public_key.save_pkcs1())
    return jsonify({
        'public_key': rsa_key.public_key.save_pkcs1().decode('utf-8'),
        'msg': 'login page'
    })


# 注册
@user_app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get("name")
        password = request.form.get("password")
        email = request.form.get("email")
        password = rsa.decrypt(base64.b64decode(password.encode("utf-8")), rsa_key.private_key).decode('utf-8')
        res = create_user(name, password, email)
        return jsonify({
            'success': res
        })
    return jsonify({
        'public_key': rsa_key.public_key.save_pkcs1().decode('utf-8'),
        'msg': 'register page'
    })


# 登出
@user_app.route("/logout", methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({
        'msg': "logout"
    })


# 用户更新个人信息
@user_app.route("/update", methods=['POST', 'GET'])
@login_required
def update():
    if request.method == 'POST':
        id = current_user.id
        name = request.form.get("name")
        password = request.form.get("password")
        email = request.form.get("email")
        password = rsa.decrypt(base64.b64decode(password.encode("utf-8")), rsa_key.private_key).decode('utf-8') if password is not None and password != '' else password
        res = update_user(id=id, name=name, password=password, email=email)
        return jsonify({
            'success' : res,
        })
    return jsonify({
        'public_key': rsa_key.public_key.save_pkcs1().decode('utf-8'),
        'msg': 'update page'
    }) 


# 用户获取个人信息
@user_app.route("/get_self", methods=['GET'])
@login_required
def get():
    user_dict = get_user(id=current_user.id)
    return jsonify({
        'data': user_dict
    })


# 管理端获取 rsa 公钥
@user_app.route("/admin/public_key", methods=['GET'])
def admin_login_key():
    return jsonify({
        'public_key':" ".join(line.strip() for line in rsa_key.public_key.save_pkcs1().decode('utf-8').splitlines())
    })


# 管理员更新某用户信息
@user_app.route("/admin/update_user", methods=['POST'])
@login_required
@authority_requried(authority_group=[1])
def admin_update_user():
    id = request.form.get("id")
    name = request.form.get("name")
    password = request.form.get("password")
    authority = request.form.get("authority")
    mark = request.form.get("mark")
    email = request.form.get("email")
    res = update_user(id=id, name=name, password=password, authority=authority, mark=mark, email=email)
    return jsonify({
        'success' : res,
    })   


# 管理员获取所有用户的信息
@user_app.route("/admin/get_all", methods=['GET'])
@login_required
@authority_requried(authority_group=[1])
def get_all():
    user_id = request.args.get('id')
    ret = get_user(id=user_id)
    return jsonify({
        'data': ret
    })


@user_app.route("/admin/get_test", methods=['GET'])
def test_test():
    return jsonify({
        "msg": "this is a message"
    })


# 管理端登录页面
@user_app.route("/admin/login", methods=['GET'])
def admin_login():
    return render_template('login.html')


# 管理端注册页面
@user_app.route("/admin/register", methods=['GET'])
def admin_register():
    return render_template('register.html')


# 管理端总览界面
@user_app.route("/admin/page", methods=['GET'])
def admin_page():
    return render_template('user_manager.html')