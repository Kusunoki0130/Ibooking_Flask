# 预定相关服务
import ssl
from ibooking.dao.models import BookingModel as bm
from ibooking.dao.Entity import db, ORMException
from datetime import datetime, timedelta
import typing as t
from geopy.distance import geodesic
from ibooking.config import sign_distance, msg_minute_10, msg_minute_15, msg_minute_45, book_persist_time_max
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from email.message import EmailMessage
import logging


def add_book(user_id:int, seat_id:int, start_time:datetime, end_time:datetime)->bool:
    """创建一个预约
    :param user_id: 当前用户 id
    :param seat_id: 座位 id
    :param start_time: 预约开始时间
    :param persist_time: 预约持续时间
    :return 一个 bool 表示创建预约是否成功
    """
    if (end_time - start_time).total_seconds()/3600 > book_persist_time_max:
        return False

    user_id = int(user_id)
    seat_id = int(seat_id)
    
    seat = db['seats'][{'id':seat_id}][0]
    room = db['rooms'][{'id':seat.room_id}][0]
    now = datetime.now()
    if start_time.hour < room.start_time or end_time > datetime(start_time.year, start_time.month, start_time.day, room.start_time) + timedelta(hours=room.persist_time):
        return False

    bookings = db['bookings']['and_(\
        or_(\
            and_(BookingModel.start_time >= "' + start_time.__str__() + '", \
                BookingModel.start_time <"' + end_time.__str__() + '"\
                ), \
            and_(BookingModel.end_time > "' + start_time.__str__() + '", \
                BookingModel.end_time <= "' + end_time.__str__() + '"\
                ) \
            ), \
        or_(BookingModel.user_id == '+ str(user_id) +', \
            BookingModel.seat_id == ' + str(seat_id) + '\
            ), \
        )']
    for item in bookings:
        if item.process & (bm.PROCESS_WAIT | bm.PROCESS_SIGN | bm.PROCESS_RUN):
            return False
    return db['bookings'].append(user_id=user_id, seat_id=seat_id, start_time=start_time, end_time=end_time)


def delete_book(user_id, user_authority, id:int) -> bool:
    """取消预约 或 提前结束
    （只有当预约状态处于未开始的时候才能取消）
    （只有当预约状态处于进行中的时候才能取消）
    :param id: 预约 id
    :return 一个 bool 表示是否取消或提前结束成功
    """
    id = int(id)
    book = db['bookings'][{'id':id}]
    if len(book) == 0:
        return False
    book = book[0]

    # 取消预约前核对身份信息
    if user_id != book.user_id and user_authority == 0:
        return False

    if book.process & (bm.PROCESS_WAIT | bm.PROCESS_SIGN):
        # 自习未开始
        try:
            db['bookings'][{'id':id}] = {
                'process': bm.PROCESS_CANCEL
            }
            return True
        except ORMException as e:
            print(e.message)
            return False
        
    elif book.process & bm.PROCESS_RUN:
        # 自习进行中
        try:
            db['bookings'][{'id': id}] = {
                'process': bm.PROCESS_STOP
            }
            return True
        except ORMException as e:
            print(e.message)
            return False   

    return False     


def check_position(room_id:int, user_location_x:float, user_location_y:float) -> bool:
    # TODO: from config import sign_distance
    room = db['rooms'][{'id': room_id}][0]
    room_location_x = room.location_x
    room_location_y = room.location_y
    dis = geodesic((user_location_y, user_location_x),(room_location_y, room_location_x)).m
    # print(dis)
    return dis <= sign_distance


def sign_book(user_id:int, id:int, location_x:float, loaction_y:float) -> bool:
    """签到
    （核验自习室和用户的距离，小于 config 中的 sign_distance）
    :param id: 预约 id
    :param loaction_x: 用户所在经度
    :param location_y: 用户所在纬度
    :return 一个 bool 表示是否签到成功
    """
    id = int(id)
    location_x = float(location_x)
    loaction_y = float(loaction_y)
    book = db['bookings'][{'id': id}]
    if len(book) == 0:
        return False
    book = book[0]

    # 签到前核对身份信息
    if user_id != book.user_id:
        return False
    
    seat = db['seats'][{'id': book.seat_id}][0]
    if book.process == bm.PROCESS_WAIT and check_position(seat.room_id, location_x, loaction_y):
        try:
            db['bookings'][{'id': id}] = {
                'process': bm.PROCESS_SIGN
            }
            return True
        except ORMException as e:
            print(e.message)
            return False   
    return False


def get_book_list(user_id:int=None) -> list:
    """获取预约列表 
    :param user_id: 当前用户的 id
    :return 一个 list，其中包含每行预约的详细信息
    """
    # if user_id is None:
    #   return all
    # else:
    #   return ...
    if user_id is None:
        lst = db['bookings'].all()
        lst = [item.get() for item in lst]
    else:
        user_id = int(user_id)
        lst = db['bookings'][{'user_id': user_id}]
        seat_map = {}
        room_map = {}
        for i in range(len(lst)):
            lst[i] = {
                'booking': lst[i].get()
            }
            
            if lst[i]['booking']['seat_id'] not in seat_map:
                seat_map[lst[i]['booking']['seat_id']] = db['seats'][{'id': lst[i]['booking']['seat_id']}][0].get()
            lst[i]['seat'] = seat_map[lst[i]['booking']['seat_id']]
            
            if lst[i]['seat']['room_id'] not in room_map:
                room_map[lst[i]['seat']['room_id']] = db['rooms'][{'id': lst[i]['seat']['room_id']}][0].get()
            
    return lst


def get_book_by_id(user_id:int, user_authority:int, id:int) -> t.Union[tuple, dict]:
    """根据预约 id 返回预约信息
    :param id: 预约 id
    :return ...
    """
    id = int(id)
    booking = db['bookings'][{'id':id}]
    if len(booking) == 0:
        return False
    booking = booking[0]

    if user_id != booking.user_id and user_authority == 0:
        return False

    seat = db['seats'][{'id': booking.seat_id}][0]
    room = db['rooms'][{'id': seat.room_id}][0]
    return {
        'booking': booking.get(),
        'seat': seat.get(),
        'room': room.get()
    }


def send_email(user_emails:t.List[str], message_body:str):

    if len(user_emails) == 0:
        return

    EMAIL_ADDRESS = '1505979366@qq.com'
    EMAIL_PASSWORD = 'xooobpwzljgvjife'
    smtp = smtplib.SMTP('smtp.qq.com', 25)
    context = ssl.create_default_context()

    msg = EmailMessage()
    msg['subject'] = "Ibooking 提醒服务"
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = user_emails
    msg.set_content(message_body)
 
    with smtplib.SMTP_SSL("smtp.qq.com", 465, context=context) as smtp:
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.send_message(msg)




def datetime__rstr__(_datetime: datetime):
    return "datetime(" + str(_datetime.year) + ", " + str(_datetime.month) + ", " + str(_datetime.day) + ", " + str(_datetime.hour) + ")"


def minute_00(_datetime: datetime=None):
    """ 修改已签到和已完成的预约状态 """
    now = datetime.now()
    start_time = datetime(now.year, now.month, now.day, now.hour) if _datetime is None else _datetime
    bookings = db['bookings']['BookingModel.start_time == ' + datetime__rstr__(start_time) + '']
    for item in bookings:
        if item.process & bm.PROCESS_SIGN:
            db['bookings'][{'id': item.id}] = {
                'process': bm.PROCESS_RUN
            }

    bookings = db['bookings']['BookingModel.end_time == ' + datetime__rstr__(start_time) + '']
    for item in bookings:
        if item.process & bm.PROCESS_RUN:
            db['bookings'][{'id': item.id}] = {
                'process': bm.PROCESS_COMPLETE
            }


def minute_10(_datetime: datetime=None):
    """ 给未签到的用户发送一次提醒 """
    now = datetime.now()
    start_time = datetime(now.year, now.month, now.day, now.hour) if _datetime is None else _datetime
    bookings = db['bookings']['BookingModel.start_time == ' + datetime__rstr__(start_time) + '']
    user_emails = []
    for item in bookings:
        if item.process & (bm.PROCESS_WAIT):
            user_email = db['users'][{'id':item.user_id}][0].email
            user_emails.append(user_email)
    send_email(user_emails, msg_minute_10)


def minute_15(_datetime: datetime=None):
    """ 给未签到的用户记录违约 """
    now = datetime.now()
    start_time = datetime(now.year, now.month, now.day, now.hour) if _datetime is None else _datetime
    bookings = db['bookings']['BookingModel.start_time == ' + datetime__rstr__(start_time) + '']
    user_emails = []
    for item in bookings:
        if item.process & bm.PROCESS_WAIT:
            user = db['users'][{'id':item.user_id}][0]
            user_emails.append(user.email)
            db['bookings'][{'id': item.id}] = {
                'process': bm.PROCESS_MARK
            }
            db['users'][{'id': user.id}] = {
                'mark': user.mark + 1
            }
        elif item.process & bm.PROCESS_SIGN:
            db['bookings'][{'id': item.id}] = {
                'process': bm.PROCESS_RUN
            }
    send_email(user_emails, msg_minute_15)


def minute_45(_datetime: datetime=None):
    """ 预约开始前给未签到的用户发送一次提醒 """
    now = datetime.now()
    start_time = datetime(now.year, now.month, now.day, now.hour + 1) if _datetime is None else _datetime
    bookings = db['bookings']['BookingModel.start_time == ' + datetime__rstr__(start_time) + '']
    user_emails = []
    for item in bookings:
        if item.process & (bm.PROCESS_WAIT):
            user_email = db['users'][{'id':item.user_id}][0].email
            user_emails.append(user_email)
    send_email(user_emails, msg_minute_45)