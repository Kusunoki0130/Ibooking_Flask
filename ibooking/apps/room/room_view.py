# 自习室相关视图
import base64
from .room_service import *
from flask import Blueprint, jsonify, request, render_template
from flask_login import login_required
from ibooking.utils.security import authority_requried
from datetime import datetime

room_app = Blueprint("room", __name__, static_folder="../static")


@room_app.route("/admin/page", methods=['GET'])
@login_required
@authority_requried(authority_group=[1])
def room_page():
    print(request.referrer)
    return render_template('room_manager.html')


@room_app.route("/admin/add_room", methods=["POST"])
@login_required
@authority_requried(authority_group=[1])
def add_room_view():
    """
    创建一个空自习室
    """
    # get params from request.form
    name = request.form.get('name')
    area = request.form.get('area')
    building = request.form.get('building')
    location_x = float(request.form.get('location_x'))
    location_y = float(request.form.get('location_y'))
    start_time = request.form.get('start_time')
    persist_time = request.form.get('persist_time')
    is_hidden = request.form.get('is_hidden')
    print(request.form.to_dict())
    # call add_room(...)
    res = add_room(name, area, building, location_x, location_y, start_time, persist_time, is_hidden)
    # return jsonify(...) or response(...)
    return jsonify({
        'success': res
    })
    


@room_app.route("/admin/rev_room", methods=["POST"])
@login_required
@authority_requried(authority_group=[1])
def update_room_view():
    """
    修改自习室基本信息，隐藏自习室（不包括座位相关信息）
    """
    # get params from request.form
    id = request.form.get('id')
    name = request.form.get('name')
    area = request.form.get('area')
    building = request.form.get('building')
    location_x = request.form.get('location_x')
    location_y = request.form.get('location_y')
    start_time = request.form.get('start_time')
    persist_time = request.form.get('persist_time')
    is_hidden = request.form.get('is_hidden')
    # call update_room(...)
    res = update_room(id, name, area, building, location_x, location_y, start_time, persist_time, is_hidden)
    # return jsonify(...) or response(...)
    return jsonify({
        'success': res
    })



@room_app.route("/admin/list_room", methods=["GET"])
@login_required
@authority_requried(authority_group=[1])
def get_room_list_view():
    """
    返回所有自习室
    """
    # get params from request.args
    # call get_room_list()
    rooms = get_room_list()
    # return jsonify(...) or response(...)
    return jsonify({
        'rooms': rooms
    })



@room_app.route("/admin/add_seat", methods=["POST"])
@login_required
@authority_requried(authority_group=[1])
def add_seat_view():
    """
    批量增加某自习室中的座位
    """
    # get params from request.form
    lst = request.json
    # call add_seat(...)
    res = add_seat(lst)
    # return jsonify(...) or response(...)
    return jsonify({
        'success': res
    })



@room_app.route("/admin/rev_seat", methods=["POST"])
@login_required
@authority_requried(authority_group=[1])
def update_seat_view():
    """
    修改某自习室中的某个座位，隐藏座位
    """
    # get params from request.form
    id = int(request.form.get('id'))
    seat_id = request.form.get('seat_id')
    room_id = request.form.get('room_id')
    mark = request.form.get('mark')
    is_occupy = request.form.get('is_occupy')
    is_hidden = request.form.get('is_hidden')
    # call update_seat(...)
    res = update_seat(id, seat_id, room_id, mark, is_occupy, is_hidden)
    # return jsonify(...) or response(...)
    return jsonify({
        'success': res
    })



@room_app.route("/admin/list_seat", methods=["GET"])
@login_required
@authority_requried(authority_group=[1])
def get_seat_list_view():
    """
    返回所有自习室的所有座位 或 指定自习室id的所有座位
    """
    # get params from request.args
    room_id = int(request.args.get('room_id'))
    # call get_seat_list(...)
    res = get_seat_list(room_id=room_id)
    # return jsonify(...) or response(...)
    return jsonify({
        'seats': res
    })



@room_app.route("/list_room", methods=["GET"])
@login_required
def get_room_list_visable_view():
    """
    返回所有普通用户可见自习室
    1. 按 返回距离近 or 用户预约频繁 等方式调整好排序
    """
    # get params from request.args
    _method = request.args.get('sort_method')
    if _method == "recommendation_basic":
        start_time = datetime.strptime(request.args.get('start_time'), '%Y-%m-%d %H:%M:%S')
        end_time = datetime.strptime(request.args.get('end_time'), '%Y-%m-%d %H:%M:%S')
        user_location_x = float(request.args.get('user_location_x'))
        user_location_y = float(request.args.get('user_location_y'))
        res = get_room_list(for_user=True, method=_method, start_time=start_time, end_time=end_time, user_location_x=user_location_x, user_location_y=user_location_y)
    elif _method == "no_recommendation":
        pass

    return jsonify({
        'rooms': res
    })



@room_app.route("/list_seat", methods=["GET"])
@login_required
def get_seat_list_visable_view():
    """
    返回所有自习室的可见座位 或 指定自习室id的可见座位
    """
    # get params from request.args
    room_id = int(request.args.get('room_id'))
    start_time = datetime.strptime(request.args.get('start_time'), '%Y-%m-%d %H:%M:%S')
    end_time = datetime.strptime(request.args.get('end_time'), '%Y-%m-%d %H:%M:%S')
    # call get_seat_list(...)
    res = get_seat_list(room_id, True, start_time, end_time)
    # return jsonify(...) or response(...)
    return jsonify({
        'seats': res
    })

