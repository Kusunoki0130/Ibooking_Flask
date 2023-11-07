import typing as t
from datetime import datetime
import logging

# —————————————————————————————— Room 模块接口访问 —————————————————————————————— #

class Room_api:

    
    def room_add(self, client, is_login: bool=True, is_admin: bool=True, room_dict: dict=None) -> dict:
        """ 管理端添加一个空自习室 """

        room_dict = {
            'name': '101',
            'area': 'xx校区',
            'building': 'xx楼',
            'location_x': 121.51186,
            'location_y': 31.34207,
        } if room_dict is None else room_dict

        resp = client.post("/room/admin/add_room", data=room_dict)
        assert resp.status_code == 200 if is_login and is_admin else resp.status_code == 401
        return resp.json

    
    def room_update(self, client, is_login: bool=True, is_admin: bool=True, room_dict: dict=None) -> dict:
        """ 管理端更新某自习室信息 """

        room_dict = {
            'id': 1,
            'start_time': 8,
            'persist_time': 20 
        } if room_dict is None else room_dict

        resp = client.post("/room/admin/rev_room", data=room_dict)
        assert resp.status_code == 200 if is_login and is_admin else resp.status_code == 401
        return resp.json


    def room_admin_get(self, client, is_login: bool=True, is_admin: bool=True) -> dict:
        """ 管理端获取所有自习室信息 """

        resp = client.get("/room/admin/list_room")
        assert resp.status_code == 200 if is_login and is_admin else resp.status_code == 401
        return resp.json


    def room_get(self, client, is_login: bool=True, query_dict: dict=None) -> dict:
        """ 客户端获取推荐自习室信息 """
        
        query_dict = {
            'start_time': datetime(2023, 4, 15, 7).__str__(),
            'end_time': datetime(2023, 4, 15, 23).__str__(),
            'user_location_x': 121.51372,
            'user_location_y': 31.34273,
            'sort_method': 'recommendation_basic'
        } if query_dict is None else query_dict

        resp = client.get("/room/list_room", query_string=query_dict)
        assert resp.status_code == 200 if is_login else resp.status_code == 401
        return resp.json        

    
    def seat_add(self, client, is_login: bool=True, is_admin: bool=True, seat_list: t.List[dict]=None) -> dict:
        """ 管理端创建一批座位 """

        seat_list = [{
            'room_id': 1, 
            'seat_id': '1_'+str(i), 
            'mark': i%2
        } for i in range(3)] if seat_list is None else seat_list

        resp = client.post("/room/admin/add_seat", json=seat_list)
        assert resp.status_code == 200 if is_login and is_admin else resp.status_code == 401
        return resp.json

    
    def seat_update(self, client, is_login: bool=True, is_admin: bool=True, seat_dict: dict=None) -> dict:
        """ 管理端更新某座位信息 """

        seat_dict = {
            'id': 1,
            'mark': 1
        } if seat_dict is None else seat_dict

        resp = client.post("/room/admin/rev_seat", data=seat_dict)
        assert resp.status_code == 200 if is_login and is_admin else resp.status_code == 401
        return resp.json


    def seat_admin_get(self, client, is_login: bool=True, is_admin: bool=True, room_id: int=1) -> dict:
        """ 管理端获取某自习室所有座位信息 """

        resp = client.get("/room/admin/list_seat", query_string={
            'room_id': room_id
        })
        assert resp.status_code == 200 if is_login and is_admin else resp.status_code == 401
        return resp.json
        


    def seat_get(self, client, is_login: bool=True, query_dict: dict=None) -> dict:
        """ 客户端获取某自习室可预约座位 """

        query_dict={
            'room_id': 1,
            'start_time': datetime(2023, 4, 15, 7).__str__(),
            'end_time': datetime(2023, 4, 15, 23).__str__(),
        } if query_dict is None else query_dict

        resp = client.get("/room/list_seat", query_string=query_dict)
        assert resp.status_code == 200 if is_login else resp.status_code == 401
        return resp.json


room_api = Room_api()
