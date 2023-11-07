# 自习室相关服务
from ibooking.dao.Entity import db, ORMException
from ibooking.dao.models import BookingModel as bm
from datetime import datetime, timedelta
import typing as t
from geopy.distance import geodesic 
import logging
import json

def add_room(name:str, area:str, building:str, location_x:float, location_y:float, start_time:int=None, persist_time:int=None, is_hidden:bool=False) -> bool:
    """增加自习室
    :param name: 自习室的名称
    :param area: 自习室所在的校区
    :param building: 自习室所在楼栋
    :param location_x: 自习室的经度
    :param loaction_y: 自习室的纬度
    :param start_time: 自习室每天开放的时间，0-23的整数，默认为7
    :param persist_time: 自习室每天关门的时间，1-24的整数，默认为22
    :return 一个 bool 变量表示是否添加成功
    """
    is_hidden = True if is_hidden is not None and is_hidden == 'True' else False
    return db['rooms'].append(name=name, area=area, building=building, location_x=location_x, location_y=location_y, start_time=start_time, persist_time=persist_time, is_hidden=is_hidden)
    


def update_room(id:int, name:str=None, area:str=None, building:str=None, location_x:float=None, location_y:float=None, start_time:int=None, persist_time:int=None, is_hidden:bool=False) -> bool:
    """修改自习室
    :param id: 自习室的id 
    :param name: 自习室的名称
    :param area: 自习室所在的校区
    :param building: 自习室所在楼栋
    :param location_x: 自习室的经度
    :param loaction_y: 自习室的纬度
    :param start_time: 自习室每天开放的时间，0-23的整数，默认为7
    :param persist_time: 自习室每天关门的时间，1-24的整数，默认为22
    :param is_hidden: 自习室是否对用户隐藏
    :return 一个 bool 变量表示是否修改成功
    """
    room = db['rooms'][{'id':id}]
    if len(room) == 0:
        return False
    room = room[0]

    try:
        db['rooms'][{'id':id}] = { 
            'name': name if name is not None and name != "" else room.name, 
            'area': area if area is not None and area != "" else room.area, 
            'building': building if building is not None and building != "" else room.building, 
            'location_x': float(location_x) if location_x is not None and location_x != "" else room.location_x, 
            'location_y': float(location_y) if location_y is not None and location_y != "" else room.location_y, 
            'start_time': int(start_time) if start_time is not None and start_time != "" else room.start_time, 
            'persist_time': int(persist_time) if persist_time is not None and persist_time != "" else room.persist_time, 
            'is_hidden': bool(is_hidden) if is_hidden is not None and is_hidden != "" else room.is_hidden
        }
        # logging.info(start_time, persist_time)
        return True
    except ORMException as e:
        print(e.message)
        return False


def get_dist(user_location_x, user_location_y, room_location_x, room_location_y) -> float:
    # TODO: 计算两经纬度表示点之间的距离，单位 m
    return geodesic((user_location_y, user_location_x),(room_location_y, room_location_x)).m


def recommendation_basic(start_time:datetime=None, end_time:datetime=None, user_location_x:float=None, user_location_y:float=None):
    room_lst = db['rooms'][{'is_hidden': False}]
    # 1. 按距离近优先取前 200 个自习室
    for i in range(len(room_lst)):
        # 计算距离
        dis = get_dist(user_location_x, user_location_y, room_lst[i].location_x, room_lst[i].location_y)
        room_lst[i] = {
            **room_lst[i].get(),
            'count': 0,
            'distance': dis,
        }
    room_lst.sort(key=lambda item: item['distance'])
    room_lst = room_lst[:200] if len(room_lst)>=200 else room_lst
    
    # 2. 获取改时间段所有预约，并记录所有已经被占的座位id
    bookings = db['bookings']['or_(\
    and_(BookingModel.start_time >= "' + start_time.__str__() + '",\
            BookingModel.start_time <"' + end_time.__str__() + '"\
            ), \
    and_(BookingModel.end_time > "' + start_time.__str__() + '", \
            BookingModel.end_time <= "' + end_time.__str__() + '"\
            ) \
    )']
    occupy = dict([(item.seat_id, item) for item in bookings if not (item.process & (bm.PROCESS_CANCEL | bm.PROCESS_STOP | bm.PROCESS_MARK | bm.PROCESS_COMPLETE))])
    
    # 3. 统计每个房间剩余座位数
    for room in room_lst:
        # 获取自习室的所有座位
        seats = db['seats'][{'room_id':room['id'], 'is_hidden': False}]
        for seat in seats:
            if seat.id not in occupy:
                room['count'] += 1


    return dict([(item['id'], item) for item in room_lst 
                 if item['count'] !=0 
                 and datetime(start_time.year, start_time.month, start_time.day, item['start_time']) < end_time
                 and datetime(start_time.year, start_time.month, start_time.day, item['start_time']) + timedelta(hours=item['persist_time']) > start_time])


def get_room_list(for_user:bool=False, method:str=None, **kw) -> t.Union[None, list]:
    """返回自习室列表
    :param for_user: 表示是否从用户端调用
    :param start_time: 期望开始自习的时间
    :param persist_time: 期望持续自习的时间
    :return 一个 list，包含所有符合条件的自习室记录
    """
    # if not for_user:
    #   return all room records
    # else:
    #   return the room records by recommendation
    if not for_user:
        room_lst = db['rooms'].all()
        ret = {}
        for room in room_lst:
            ret[room.id] = {**room.get()}
            ret[room.id]['count'] = len(db['seats'][{'room_id':room.id}])
    
    else:
        if method == 'recommendation_basic':
            # 'recommendation_basic' gives the basic algorithm to get rooms for current user by distance calculation
            # '**kw' includes other parameters for the algorithm replacing 'recommendation_basic'
            start_time = kw['start_time']
            end_time = kw['end_time']
            user_location_x = kw['user_location_x']
            user_location_y = kw['user_location_y']
            ret = recommendation_basic(start_time, end_time, user_location_x, user_location_y)
        
    return ret


def add_seat_one_by_one(seat_id:str, room_id:int, mark:int=0, is_hidden:bool=False) -> bool:
    room_id = int(room_id)
    if len(db['rooms'][{'id': room_id}]) == 0:
        return False
    mark = int(mark)
    return True if db['seats'].append(seat_id=seat_id, room_id=room_id, mark=mark, is_hidden=is_hidden) is not False else False


def add_seat(lst:t.List[dict]) -> bool:
    success = True
    for item in lst:
        success = success & add_seat_one_by_one(**item)
    return success


def update_seat(id:int, seat_id:str=None, room_id:int=None, mark:int=None, is_occupy:bool=None, is_hidden:bool=None) -> bool:
    seat = db['seats'][{'id': id}]
    if len(seat) == 0:
        return False
    seat = seat[0]

    try:
        db['seats'][{'id': id}] = {
            'seat_id': seat_id if seat_id is not None and seat_id != "" else seat.seat_id,
            'room_id': int(room_id) if room_id is not None and room_id != "" else seat.room_id,
            'mark': mark if mark is not None and mark != "" else seat.mark,
            'is_occupy': bool(is_occupy) if is_occupy is not None and is_occupy != "" else seat.is_occupy,
            'is_hidden': bool(is_hidden) if is_hidden is not None and is_hidden != "" else seat.is_hidden
        }
        return True
    except ORMException as e:
        print(e.message)
        return False
    

def get_seat_list(room_id:int=None, for_user:bool=False, start_time:datetime=None, end_time:datetime=None):
    
    # TODO: 如果硬要按照 mark 搜索座位，那就不能把 room_id 座位关键词了
    if not for_user:
        lst = db['seats'][{'room_id': room_id}]      
    else:
        lst = db['seats'][{'room_id': room_id, 'is_hidden': False}]

        bookings = db['bookings']['or_(\
            and_(BookingModel.start_time >= "' + start_time.__str__() + '",\
                BookingModel.start_time <"' + end_time.__str__() + '"\
                ), \
            and_(BookingModel.end_time > "' + start_time.__str__() + '", \
                BookingModel.end_time <= "' + end_time.__str__() + '"\
                ) \
            )']
        occupy = dict([(item.seat_id, item) for item in bookings if not (item.process & (bm.PROCESS_CANCEL | bm.PROCESS_STOP | bm.PROCESS_MARK | bm.PROCESS_COMPLETE))])

        lst = [item for item in lst if item.id not in occupy]
    
    room = db['rooms'][{'id':room_id}][0].get()
    room.pop('is_hidden')
    room.pop('id')
    return [{**item.get(), **room} for item in lst]    
        

