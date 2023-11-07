from ibooking.app import minute_00, minute_10, minute_15, minute_45
from datetime import datetime

class Book_api:

    def book_add(self, client, is_login: bool=True, book_dict: dict=None) -> dict:
        """ 创建一个自习预约，处于等待签到状态 """

        book_dict = {
            'seat_id': 2,
            'start_time': datetime(2023, 4, 15, 16).__str__(),
            'end_time': datetime(2023, 4, 15, 19).__str__()
        } if book_dict is None else book_dict

        resp = client.post("/book/submit", data=book_dict)
        assert resp.status_code == 200 if is_login else resp.status_code == 401
        return resp.json


    def book_cancel(self, client, is_login: bool=True, book_id: int=1) -> dict: 
        """ 取消一个自习预约，只对处于等待签到、等待开始、正在进行的自习预约有效"""
        
        resp = client.post("/book/cancel", data={
            'id': book_id
        })
        assert resp.status_code == 200 if is_login else resp.status_code == 401
        return resp.json
    

    def book_sign(self, client, is_login: bool=True, post_dict: dict=None) -> dict: 
        """ 签到一个自习预约，只对处于等待签到自习预约有效"""
        
        post_dict = {
            'id': 1,
            'location_x': 121.51372,
            'location_y': 31.34273
        } if post_dict is None else post_dict

        resp = client.post("/book/sign", data=post_dict)
        assert resp.status_code == 200 if is_login else resp.status_code == 401
        return resp.json        


    def book_get_self(self, client, is_login: bool=True) -> dict:
        """ 获取某用户所有相关的自习预约 """
        
        resp = client.get("/book/get")
        assert resp.status_code == 200 if is_login else resp.status_code == 401
        return resp.json


    def book_get_id(self, client, is_login: bool=True, book_id: int=1) -> dict:
        """ 获取 id 对应自习预约的详细信息 """
        
        resp = client.get("/book/id", query_string={
            'id': book_id
        })
        assert resp.status_code == 200 if is_login else resp.status_code == 401
        return resp.json

    
    def book_admin_get(self, client, is_login: bool=True, is_admin: bool=True) -> dict:
        """ 获取全部预约 """
        
        resp = client.get("/book/admin/get_all")
        assert resp.status_code == 200 if is_login and is_admin else resp.status_code == 401
        return resp.json


    def book_inform_sign_before_start(self, start_time:datetime=datetime(2023, 4, 15, 7)):
        """ 向给定时间未签到预约的用户发送邮件提醒签到 """
        minute_45(start_time)


    def book_start(self, start_time:datetime=datetime(2023, 4, 15, 7)):
        """ 将给定时间已签到的预约更新为进行中 """
        minute_00(start_time)


    def book_inform_sign_after_start(self, start_time:datetime=datetime(2023, 4, 15, 7)):
        """ 向给定时间未签到预约的用户发送邮件警告违约 """
        minute_10(start_time)


    def book_inform_mark_after_start(self, start_time:datetime=datetime(2023, 4, 15, 7)):
        """ 向给定时间未签到预约的用户发送邮件通知违约 """
        minute_15(start_time)


book_api = Book_api()