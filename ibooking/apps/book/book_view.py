# 预定相关视图
import base64
from .book_service import *
from flask import Blueprint, jsonify, request, render_template
from flask_login import login_required, current_user
from ibooking.utils.security import authority_requried
from datetime import datetime
from ibooking.utils.auto import Auto
from ibooking.config import sign_allowed_after_start, inform_after_start, inform_before_start

book_app = Blueprint("book", __name__)


@book_app.route("/admin/page", methods=['GET'])
@login_required
@authority_requried(authority_group=[1])
def room_page():
    print(request.referrer)
    return render_template('book_manager.html')


@book_app.route("/submit", methods=['POST'])
@login_required
def add_book_view():
    """
    创建一个预约
    """
    # get params from request.form
    seat_id = request.form.get('seat_id')
    start_time = datetime.strptime(request.form.get('start_time'), '%Y-%m-%d %H:%M:%S')
    end_time = datetime.strptime(request.form.get('end_time'), '%Y-%m-%d %H:%M:%S')
    # current_user
    user_id = current_user.id
    # call add_book(...)
    res = add_book(user_id, seat_id, start_time, end_time)
    # return jsonify(...) or response(...)
    return jsonify({
        'success': res
    })


@book_app.route("/cancel", methods=['POST'])
@login_required
def delete_book_view():
    """
    取消一个预约
    """
    user_id = current_user.id
    user_authority = current_user.authority
    # get params from request.form
    booking_id = request.form.get('id')
    # call delete_book(...)
    res = delete_book(user_id, user_authority, booking_id)
    # return jsonify(...) or response(...)
    return jsonify({
        'success': res
    })


@book_app.route("/sign", methods=['POST'])
@login_required
def sign_book_view():
    """
    签到
    """
    # get params from request.form
    user_id = current_user.id
    booking_id = request.form.get('id')
    location_x = request.form.get('location_x')
    location_y = request.form.get('location_y')
    # call sign_book(...)
    res = sign_book(user_id, booking_id, location_x, location_y)
    # return jsonify(...) or response(...)
    return jsonify({
        'success': res
    })


@book_app.route("/get", methods=['GET'])
@login_required
def get_book_list_view():
    """
    获取某用户所有预约
    """
    # current_user
    id = current_user.id
    # call get_book_list(...)
    res = get_book_list(id)
    # return jsonify(...) or response(...)
    return jsonify({
        'bookings': res
    })


@book_app.route("/id", methods=['GET'])
@login_required
def get_book_by_id_view():
    """
    根据预约id获取预约所有信息
    """
    user_id = current_user.id
    user_authority = current_user.authority
    # get params from request.args
    id = request.args.get('id')
    # call get_book_by_id(...)
    res = get_book_by_id(user_id, user_authority, id)
    # return jsonify(...) or response(...)
    return jsonify({
        'booking': res
    })


@book_app.route("/admin/get_all", methods=['GET'])
@login_required
@authority_requried(authority_group=[1])
def get_book_list_admin_view():
    """
    获取全部预约
    """
    # get params from request.args
    # call get_book_list(...)
    res = get_book_list()
    # return jsonify(...) or response(...)
    return jsonify({
        'bookings': res
    })


auto_00 = Auto(0, minute_00)
auto_10 = Auto(inform_after_start, minute_10)
auto_15 = Auto(sign_allowed_after_start, minute_15)
auto_45 = Auto(60-inform_before_start, minute_45)