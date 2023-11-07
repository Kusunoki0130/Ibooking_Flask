import json
import logging
import rsa
import base64
import pytest
from .user_api_access import user_api
from .room_api_access import room_api
from .book_api_access import book_api
import typing as t
from datetime import datetime
from ibooking.dao import Process


# —————————————————————————————— Book 模块用例测试 —————————————————————————————— #

class Test_book:
    

    def setup_rooms(self, client):
        """ 运行每个用例前创建一批自习室和座位 """

        # 登录 admin 账号
        resp_json = user_api.user_login(client)
        assert resp_json['success'] == True

        # 添加 5 个自习室
        resp_json = room_api.room_add(client, room_dict={
            'name': 'A101', 
            'area': '江湾校区', 
            'building': '教学楼A', 
            'location_x': 121.51186, 
            'location_y': 31.34207
        }) # 默认自习室，每天开放时间 7:00 ~ 22:00
        assert resp_json['success'] != False
        resp_json = room_api.room_add(client, room_dict={
            'name': 'A102', 
            'area': '江湾校区', 
            'building': '教学楼A', 
            'location_x': 121.51186, 
            'location_y': 31.34207,
            'is_hidden': True
        }) # 被隐藏的自习室
        assert resp_json['success'] != False
        resp_json = room_api.room_add(client, room_dict={
            'name': 'A103', 
            'area': '江湾校区', 
            'building': '教学楼A', 
            'location_x': 121.51186, 
            'location_y': 31.34207,
            'start_time': 0,
            'persist_time': 24
        }) # 24 小时开放自习室
        assert resp_json['success'] != False
        resp_json = room_api.room_add(client, room_dict={
            'name': 'A104', 
            'area': '江湾校区', 
            'building': '教学楼A', 
            'location_x': 121.51186, 
            'location_y': 31.34207,
            'start_time': 16,
            'persist_time': 8
        }) # 开放到次日的自习室 16:00 ~ 02:00
        assert resp_json['success'] != False
        resp_json = room_api.room_add(client, room_dict={
            'name': '2001', 
            'area': '江湾校区', 
            'building': '图书馆', 
            'location_x': 121.51382, 
            'location_y': 31.34269
        }) # 在图书馆的自习室
        assert resp_json['success'] != False


        # 每个自习室添加 5 个座位
        for room_id in range(5):
            resp_json = room_api.seat_add(client, seat_list=[{'room_id': room_id+1, 'seat_id': str(room_id+1)+'_'+str(i+1), 'mark': i%2} for i in range(5)])
            assert resp_json['success'] != False

        # 登出
        resp_json = user_api.user_logout(client)

    @pytest.mark.book_app
    def test_book_get_self_unauthorized(self, client):
        """ 获取某用户所有相关的自习预约 case 1 : 未登录，HTTP 401 """
        
        book_api.book_get_self(client, is_login=False)

    
    @pytest.mark.book_app
    def test_book_admin_get_unauthorized(self, client):
        """ 获取全部预约 case 1 : 未登录或非管理员账号，HTTP 401 """
        
        # 1. 未登录
        book_api.book_admin_get(client, is_login=False)

        # 2. 使用普通用户账号 Alice 
        resp_json = user_api.user_login(client, user_dict={
            'name': 'Alice',
            'password': '111111'
        })
        assert resp_json['success'] == True
        book_api.book_admin_get(client, is_admin=False)


    @pytest.mark.book_app
    def test_book_add_unauthorized(self, client):
        """ 创建一个自习预约 case 1 : 未登录，HTTP 401 """
        
        book_api.book_add(client, is_login=False)


    @pytest.mark.book_app
    def test_book_add_booking_time(self, client):
        """ 创建一个自习预约 case 2 : 预约时间长度超过规定长度 """
        self.setup_rooms(client)

        # 1. 登录 Alice 账号
        resp_json = user_api.user_login(client, user_dict={
            'name': 'Alice',
            'password': '111111'
        })
        assert resp_json['success'] == True

        # 2. 创建预约
        resp_json = book_api.book_add(client, book_dict={
            'seat_id': 2,
            'start_time': datetime(2023, 4, 15, 16).__str__(),
            'end_time': datetime(2023, 4, 16, 16).__str__(),
        })
        assert resp_json['success'] == False


    @pytest.mark.book_app
    def test_book_add_room_time(self, client):
        """ 创建一个自习预约 case 3 : 预约时间长度不在自习室提供服务时间段内 """
        self.setup_rooms(client)

        # 1. 登录 Alice 账号
        resp_json = user_api.user_login(client, user_dict={
            'name': 'Alice',
            'password': '111111'
        })
        assert resp_json['success'] == True

        # 2. 创建预约
        resp_json = book_api.book_add(client, book_dict={
            'seat_id': 2,
            'start_time': datetime(2023, 4, 15, 21).__str__(),
            'end_time': datetime(2023, 4, 15, 23).__str__(),
        })
        assert resp_json['success'] == False


    
    @pytest.mark.book_app
    def test_book_add_user_process_wait(self, client):
        """ 创建一个自习预约 case 4 : 用户在该时间段内有其他预约正在等待签到 """
        self.setup_rooms(client)

        # 1. 登录 Alice 账号
        resp_json = user_api.user_login(client, user_dict={
            'name': 'Alice',
            'password': '111111'
        })
        assert resp_json['success'] == True

        # 2. 创建预约
        resp_json = book_api.book_add(client, book_dict={
            'seat_id': 2,
            'start_time': datetime(2023, 4, 15, 7).__str__(),
            'end_time': datetime(2023, 4, 15, 11).__str__(),
        })
        assert resp_json['success'] != False

        # 3. 再次创建预约
        resp_json = book_api.book_add(client, book_dict={
            'seat_id': 3,
            'start_time': datetime(2023, 4, 15, 10).__str__(),
            'end_time': datetime(2023, 4, 15, 12).__str__(),
        })
        assert resp_json['success'] == False


    @pytest.mark.book_app
    def test_book_add_user_process_sign(self, client):
        """ 创建一个自习预约 case 5 : 用户在该时间段内有其他预约正在等待开始 """
        self.setup_rooms(client)

        # 1. 登录 Alice 账号
        resp_json = user_api.user_login(client, user_dict={
            'name': 'Alice',
            'password': '111111'
        })
        assert resp_json['success'] == True

        # 2. 创建预约，并签到
        resp_json = book_api.book_add(client, book_dict={
            'seat_id': 2,
            'start_time': datetime(2023, 4, 15, 7).__str__(),
            'end_time': datetime(2023, 4, 15, 11).__str__(),
        })
        assert resp_json['success'] != False

        resp_json = book_api.book_sign(client, post_dict={
            'id': 1,
            'location_x': 121.51186, 
            'location_y': 31.34207
        })
        assert resp_json['success'] == True

        # 3. 再次创建预约
        resp_json = book_api.book_add(client, book_dict={
            'seat_id': 3,
            'start_time': datetime(2023, 4, 15, 10).__str__(),
            'end_time': datetime(2023, 4, 15, 12).__str__(),
        })
        assert resp_json['success'] == False

    
    @pytest.mark.book_app
    def test_book_add_user_process_run(self, client):
        """ 创建一个自习预约 case 6 : 用户在该时间段内有其他预约正在进行 """
        self.setup_rooms(client)

        # 1. 登录 Alice 账号
        resp_json = user_api.user_login(client, user_dict={
            'name': 'Alice',
            'password': '111111'
        })
        assert resp_json['success'] == True

        # 2. 创建预约，并签到，且系统轮询任务将其设置为正在进行
        resp_json = book_api.book_add(client, book_dict={
            'seat_id': 2,
            'start_time': datetime(2023, 4, 15, 7).__str__(),
            'end_time': datetime(2023, 4, 15, 11).__str__(),
        })
        assert resp_json['success'] != False

        resp_json = book_api.book_sign(client, post_dict={
            'id': 1,
            'location_x': 121.51186, 
            'location_y': 31.34207
        })
        assert resp_json['success'] == True
        
        book_api.book_start(datetime(2023, 4, 15, 7))
        # 检查是否启动成功
        resp_json = book_api.book_get_id(client, book_id=1)
        assert resp_json['booking']['booking']['process'] == Process.RUN

        # 3. 再次创建预约
        resp_json = book_api.book_add(client, book_dict={
            'seat_id': 3,
            'start_time': datetime(2023, 4, 15, 10).__str__(),
            'end_time': datetime(2023, 4, 15, 12).__str__(),
        })
        assert resp_json['success'] == False


    @pytest.mark.book_app
    def test_book_add_seat_process_wait(self, client):
        """ 创建一个自习预约 case 7 : 座位在该时间段内有其他用户的预约正在等待签到 """
        self.setup_rooms(client)

        # 1. 登录 admin 账号
        resp_json = user_api.user_login(client)
        assert resp_json['success'] == True

        # 2. admin 创建预约
        resp_json = book_api.book_add(client, book_dict={
            'seat_id': 2,
            'start_time': datetime(2023, 4, 15, 7).__str__(),
            'end_time': datetime(2023, 4, 15, 11).__str__(),
        })
        assert resp_json['success'] != False

        # 3. admin 登出换 Alice
        user_api.user_logout(client)
        resp_json = user_api.user_login(client, user_dict={
            'name': 'Alice',
            'password': '111111'
        })
        assert resp_json['success'] == True

        # 3. Alice 创建预约
        resp_json = book_api.book_add(client, book_dict={
            'seat_id': 2,
            'start_time': datetime(2023, 4, 15, 10).__str__(),
            'end_time': datetime(2023, 4, 15, 12).__str__(),
        })
        assert resp_json['success'] == False


    @pytest.mark.book_app
    def test_book_add_seat_process_sign(self, client):
        """ 创建一个自习预约 case 8 : 座位在该时间段内有其他用户的预约正在等待开始 """
        self.setup_rooms(client)

        # 1. 登录 admin 账号
        resp_json = user_api.user_login(client)
        assert resp_json['success'] == True

        # 2. admin 创建预约，并签到
        resp_json = book_api.book_add(client, book_dict={
            'seat_id': 2,
            'start_time': datetime(2023, 4, 15, 7).__str__(),
            'end_time': datetime(2023, 4, 15, 11).__str__(),
        })
        assert resp_json['success'] != False

        resp_json = book_api.book_sign(client, post_dict={
            'id': 1,
            'location_x': 121.51186, 
            'location_y': 31.34207
        })
        assert resp_json['success'] == True

        # 3. admin 登出换 Alice
        user_api.user_logout(client)
        resp_json = user_api.user_login(client, user_dict={
            'name': 'Alice',
            'password': '111111'
        })
        assert resp_json['success'] == True

        # 3. Alice 创建预约
        resp_json = book_api.book_add(client, book_dict={
            'seat_id': 2,
            'start_time': datetime(2023, 4, 15, 10).__str__(),
            'end_time': datetime(2023, 4, 15, 12).__str__(),
        })
        assert resp_json['success'] == False

    
    @pytest.mark.book_app
    def test_book_add_seat_process_run(self, client):
        """ 创建一个自习预约 case 9 : 座位在该时间段内有其他用户的预约正在进行 """
        self.setup_rooms(client)

        # 1. 登录 admin 账号
        resp_json = user_api.user_login(client)
        assert resp_json['success'] == True

        # 2. admin 创建预约，并签到，且系统轮询任务将其设置为正在进行
        resp_json = book_api.book_add(client, book_dict={
            'seat_id': 2,
            'start_time': datetime(2023, 4, 15, 7).__str__(),
            'end_time': datetime(2023, 4, 15, 11).__str__(),
        })
        assert resp_json['success'] != False

        resp_json = book_api.book_sign(client, post_dict={
            'id': 1,
            'location_x': 121.51186, 
            'location_y': 31.34207
        })
        assert resp_json['success'] == True

        book_api.book_start(datetime(2023, 4, 15, 7))
        # 检查是否启动成功
        resp_json = book_api.book_get_id(client, book_id=1)
        assert resp_json['booking']['booking']['process'] == Process.RUN

        # 3. admin 登出换 Alice
        user_api.user_logout(client)
        resp_json = user_api.user_login(client, user_dict={
            'name': 'Alice',
            'password': '111111'
        })
        assert resp_json['success'] == True

        # 3. Alice 创建预约
        resp_json = book_api.book_add(client, book_dict={
            'seat_id': 2,
            'start_time': datetime(2023, 4, 15, 10).__str__(),
            'end_time': datetime(2023, 4, 15, 12).__str__(),
        })
        assert resp_json['success'] == False


    @pytest.mark.book_app
    def test_book_get_id_unauthorized_1(self, client):
        """ 获取 id 对应自习预约的详细信息 case 1 : 未登录，HTTP 401 """
        
        book_api.book_get_id(client, is_login=False)
    

    @pytest.mark.book_app
    def test_book_get_id_unauthorized_2(self, client):
        """ 获取 id 对应自习预约的详细信息 case 2 : 非该预约创建者尝试获取该预约信息 """
        self.setup_rooms(client)

        # 1. 登录 admin 并创建预约
        resp_josn = user_api.user_login(client)
        assert resp_josn['success'] != False
        resp_josn = book_api.book_add(client)
        assert resp_josn['success'] != False

        # 2. 切换到 Alice 尝试获取 admin 的预约
        user_api.user_logout(client)
        resp_json = user_api.user_login(client, user_dict={
            'name': 'Alice',
            'password': '111111'
        })
        assert resp_json['success'] == True
        resp_josn = book_api.book_get_id(client)
        assert resp_josn['booking'] == False

    
    @pytest.mark.book_app
    def test_book_get_id_not_exist(self, client):
        """ 获取 id 对应自习预约的详细信息 case 3 : 该预约不存在 """

        # 1. 登录 Alice 
        resp_json = user_api.user_login(client, user_dict={
            'name': 'Alice',
            'password': '111111'
        })
        assert resp_json['success'] == True

        # 2. 尝试获取不存在预约
        resp_josn = book_api.book_get_id(client, book_id=114514)
        assert resp_josn['booking'] == False


    @pytest.mark.book_app
    def test_book_cancel_unauthorized_1(self, client):
        """ 取消一个自习预约 case 1 : 未登录，HTTP 401 """
        
        book_api.book_cancel(client, is_login=False)

    
    @pytest.mark.book_app
    def test_book_cancel_unauthorized_2(self, client):
        """ 取消一个自习预约 case 2 : 非该预约创建者尝试取消该预约 """
        self.setup_rooms(client)
        
        # 1. 登录 admin 账号
        resp_json = user_api.user_login(client)
        assert resp_json['success'] == True

        # 2. admin 创建预约
        resp_json = book_api.book_add(client, book_dict={
            'seat_id': 2,
            'start_time': datetime(2023, 4, 15, 7).__str__(),
            'end_time': datetime(2023, 4, 15, 11).__str__(),
        })
        assert resp_json['success'] != False

        # 3. admin 登出换 Alice
        user_api.user_logout(client)
        resp_json = user_api.user_login(client, user_dict={
            'name': 'Alice',
            'password': '111111'
        })
        assert resp_json['success'] == True

        # 4. Alice 尝试取消 admin 的预约
        resp_json = book_api.book_cancel(client, book_id=1)
        assert resp_json['success'] == False
    

    @pytest.mark.book_app
    def test_book_cancel_not_exist(self, client):
        """ 取消一个自习预约 case 3 : 预约不存在 """
        
        # 1. 登录 Alice
        resp_json = user_api.user_login(client, user_dict={
            'name': 'Alice',
            'password': '111111'
        })
        assert resp_json['success'] == True

        # 2. Alice 尝试取消不存在的预约
        resp_json = book_api.book_cancel(client, book_id=114514)
        assert resp_json['success'] == False


    @pytest.mark.book_app
    def test_book_cancel_process_wait(self, client):
        """ 取消一个自习预约 case 4 : 预约处于等待签到状态，预约创建者或管理员取消预约 """
        self.setup_rooms(client)

        # 1. 登录 Alice 账号
        resp_json = user_api.user_login(client, user_dict={
            'name': 'Alice',
            'password': '111111'
        })
        assert resp_json['success'] == True

        # 2. 创建预约
        resp_json = book_api.book_add(client, book_dict={
            'seat_id': 2,
            'start_time': datetime(2023, 4, 15, 7).__str__(),
            'end_time': datetime(2023, 4, 15, 11).__str__(),
        })
        assert resp_json['success'] != False

        # 3. 取消预约
        resp_json = book_api.book_cancel(client, book_id=1)
        assert resp_json['success'] == True

        # 4. 检查是否取消成功
        resp_json = book_api.book_get_id(client, book_id=1)
        assert resp_json['booking']['booking']['process'] == Process.CANCEL


    @pytest.mark.book_app
    def test_book_cancel_process_sign(self, client):
        """ 取消一个自习预约 case 5 : 预约处于等待开始状态，预约创建者或管理员取消预约 """
        self.setup_rooms(client)

        # 1. 登录 Alice 账号
        resp_json = user_api.user_login(client, user_dict={
            'name': 'Alice',
            'password': '111111'
        })
        assert resp_json['success'] == True

        # 2. 创建预约，并签到
        resp_json = book_api.book_add(client, book_dict={
            'seat_id': 2,
            'start_time': datetime(2023, 4, 15, 7).__str__(),
            'end_time': datetime(2023, 4, 15, 11).__str__(),
        })
        assert resp_json['success'] != False
        
        resp_json = book_api.book_sign(client, post_dict={
            'id': 1,
            'location_x': 121.51186, 
            'location_y': 31.34207
        })
        assert resp_json['success'] == True

        # 3. 取消预约
        resp_json = book_api.book_cancel(client, book_id=1)
        assert resp_json['success'] == True

        # 4. 检查是否取消成功
        resp_json = book_api.book_get_id(client, book_id=1)
        assert resp_json['booking']['booking']['process'] == Process.CANCEL


    @pytest.mark.book_app
    def test_book_cancel_process_sign(self, client):
        """ 取消一个自习预约 case 6 : 预约处于正在进行状态，预约创建者或管理员取消预约 """
        self.setup_rooms(client)

        # 1. 登录 Alice 账号
        resp_json = user_api.user_login(client, user_dict={
            'name': 'Alice',
            'password': '111111'
        })
        assert resp_json['success'] == True

        # 2. 创建预约，并签到，且系统轮询任务将其设置为正在进行
        resp_json = book_api.book_add(client, book_dict={
            'seat_id': 2,
            'start_time': datetime(2023, 4, 15, 7).__str__(),
            'end_time': datetime(2023, 4, 15, 11).__str__(),
        })
        assert resp_json['success'] != False
        
        resp_json = book_api.book_sign(client, post_dict={
            'id': 1,
            'location_x': 121.51186, 
            'location_y': 31.34207
        })
        assert resp_json['success'] == True

        book_api.book_start(datetime(2023, 4, 15, 7))
        # 检查是否启动成功
        resp_json = book_api.book_get_id(client, book_id=1)
        assert resp_json['booking']['booking']['process'] == Process.RUN

        # 3. 取消预约
        resp_json = book_api.book_cancel(client, book_id=1)
        assert resp_json['success'] == True

        # 4. 检查是否取消成功
        resp_json = book_api.book_get_id(client, book_id=1)
        assert resp_json['booking']['booking']['process'] == Process.STOP


    @pytest.mark.book_app
    def test_book_cancel_process_others(self, client):
        """ 取消一个自习预约 case 7 : 预约处于非 case 4,5,6 中的状态，预约创建者或管理员取消预约 """
        self.setup_rooms(client)

        # 1. 登录 Alice 账号
        resp_json = user_api.user_login(client, user_dict={
            'name': 'Alice',
            'password': '111111'
        })
        assert resp_json['success'] == True

        # 2. 创建预约，并签到，且系统轮询任务将其设置运行完成，尝试取消预约
        resp_json = book_api.book_add(client, book_dict={
            'seat_id': 2,
            'start_time': datetime(2023, 4, 15, 7).__str__(),
            'end_time': datetime(2023, 4, 15, 11).__str__(),
        })
        assert resp_json['success'] != False
        
        resp_json = book_api.book_sign(client, post_dict={
            'id': 1,
            'location_x': 121.51186, 
            'location_y': 31.34207
        })
        assert resp_json['success'] == True

        book_api.book_start(datetime(2023, 4, 15, 7))
        # 检查是否启动成功
        resp_json = book_api.book_get_id(client, book_id=1)
        assert resp_json['booking']['booking']['process'] == Process.RUN
        book_api.book_start(datetime(2023, 4, 15, 11))
        # 检查是否运行完成
        resp_json = book_api.book_get_id(client, book_id=1)
        assert resp_json['booking']['booking']['process'] == Process.COMPLETE

        resp_json = book_api.book_cancel(client, book_id=1)
        assert resp_json['success'] == False

    
    @pytest.mark.book_app
    def test_book_sign_unauthorized_1(self, client):
        """ 签到一个自习预约 case 1 : 未登录，HTTP 401 """
        
        book_api.book_sign(client, is_login=False)

    
    @pytest.mark.book_app
    def test_book_sign_unauthorized_2(self, client):
        """ 签到一个自习预约 case 2 : 非该预约创建者尝试签到该预约 """
        self.setup_rooms(client)
        
        # 1. 登录 admin 账号
        resp_json = user_api.user_login(client)
        assert resp_json['success'] == True

        # 2. admin 创建预约
        resp_json = book_api.book_add(client, book_dict={
            'seat_id': 2,
            'start_time': datetime(2023, 4, 15, 7).__str__(),
            'end_time': datetime(2023, 4, 15, 11).__str__(),
        })
        assert resp_json['success'] != False

        # 3. admin 登出换 Alice
        user_api.user_logout(client)
        resp_json = user_api.user_login(client, user_dict={
            'name': 'Alice',
            'password': '111111'
        })
        assert resp_json['success'] == True

        # 4. Alice 尝试签到该预约
        resp_json = book_api.book_sign(client, post_dict={
            'id': 1,
            'location_x': 121.51186, 
            'location_y': 31.34207
        })
        assert resp_json['success'] == False

    
    @pytest.mark.book_app
    def test_book_sign_not_exist(self, client):
        """ 签到一个自习预约 case 3 : 预约不存在 """
        self.setup_rooms(client)
        
        # 1. 登录 admin 账号
        resp_json = user_api.user_login(client)
        assert resp_json['success'] == True

        # 2. admin 尝试签到一个不存在的预约
        resp_json = book_api.book_sign(client, post_dict={
            'id': 114514,
            'location_x': 121.51186, 
            'location_y': 31.34207
        })
        assert resp_json['success'] == False

    
    @pytest.mark.book_app
    def test_book_sign_process_wait_far(self, client):
        """ 签到一个自习预约 case 4 : 预约处于等待签到状态，预约创建者进行签到，距离超过最大允许范围 """
        self.setup_rooms(client)
        
        # 1. 登录 admin 账号
        resp_json = user_api.user_login(client)
        assert resp_json['success'] == True

        # 2. admin 创建预约
        resp_json = book_api.book_add(client, book_dict={
            'seat_id': 2,
            'start_time': datetime(2023, 4, 15, 7).__str__(),
            'end_time': datetime(2023, 4, 15, 11).__str__(),
        })
        assert resp_json['success'] != False

        # 3. admin 离的很远进行签到
        resp_json = book_api.book_sign(client, post_dict={
            'id': 1,
            'location_x': 120.51186, 
            'location_y': 30.34207
        })
        assert resp_json['success'] == False

    
    @pytest.mark.book_app
    def test_book_sign_process_wait_success(self, client):
        """ 签到一个自习预约 case 5 : 预约处于等待签到状态，预约创建者进行签到，距离在最大允许范围内 """
        self.setup_rooms(client)
        
        # 1. 登录 admin 账号
        resp_json = user_api.user_login(client)
        assert resp_json['success'] == True

        # 2. admin 创建预约
        resp_json = book_api.book_add(client, book_dict={
            'seat_id': 2,
            'start_time': datetime(2023, 4, 15, 7).__str__(),
            'end_time': datetime(2023, 4, 15, 11).__str__(),
        })
        assert resp_json['success'] != False

        # 3. admin 在签到范围内进行签到
        resp_json = book_api.book_sign(client, post_dict={
            'id': 1,
            'location_x': 121.51186, 
            'location_y': 31.34207
        })
        assert resp_json['success'] == True

        # 4. 检查预约的状态
        resp_json = book_api.book_get_id(client, book_id=1)
        assert resp_json['booking']['booking']['process'] == Process.SIGN

    
    @pytest.mark.book_app
    def test_book_sign_not_process_wait(self, client):
        """ 签到一个自习预约 case 6 : 预约不处于等待签到状态，预约创建者进行签到 """
        self.setup_rooms(client)
        
        # 1. 登录 admin 账号
        resp_json = user_api.user_login(client)
        assert resp_json['success'] == True

        # 2. admin 创建预约，随后取消了
        resp_json = book_api.book_add(client, book_dict={
            'seat_id': 2,
            'start_time': datetime(2023, 4, 15, 7).__str__(),
            'end_time': datetime(2023, 4, 15, 11).__str__(),
        })
        assert resp_json['success'] != False

        resp_json = book_api.book_cancel(client, book_id=1)
        assert resp_json['success'] == True

        # 3. admin 尝试签到
        resp_json = book_api.book_sign(client, post_dict={
            'id': 1,
            'location_x': 121.51186, 
            'location_y': 31.34207
        })
        assert resp_json['success'] == False


    @pytest.mark.book_app
    def test_book_inform_sign_before_start(self, client):
        """ 向给定时间未签到预约的用户发送邮件提醒签到 """
        self.setup_rooms(client)

        # 1. 登录 Alice 账号
        resp_json = user_api.user_login(client, user_dict={
            'name': 'Alice',
            'password': '111111'
        })
        assert resp_json['success'] == True

        # 2. 创建预约
        resp_json = book_api.book_add(client, book_dict={
            'seat_id': 2,
            'start_time': datetime(2023, 4, 15, 7).__str__(),
            'end_time': datetime(2023, 4, 15, 11).__str__(),
        })
        assert resp_json['success'] != False

        # 3. 发送提醒
        book_api.book_inform_sign_before_start(datetime(2023, 4, 15, 7))
    

    @pytest.mark.book_app
    def test_book_start(self, client):
        """ 将给定时间已签到的预约更新为进行中 """
        self.setup_rooms(client)

        # 1. 登录 Alice 账号
        resp_json = user_api.user_login(client, user_dict={
            'name': 'Alice',
            'password': '111111'
        })
        assert resp_json['success'] == True

        # 2. 创建预约，并签到
        resp_json = book_api.book_add(client, book_dict={
            'seat_id': 2,
            'start_time': datetime(2023, 4, 15, 7).__str__(),
            'end_time': datetime(2023, 4, 15, 11).__str__(),
        })
        assert resp_json['success'] != False

        resp_json = book_api.book_sign(client, post_dict={
            'id': 1,
            'location_x': 121.51186, 
            'location_y': 31.34207
        })
        assert resp_json['success'] == True

        # 3. 预约切换到进行状态
        book_api.book_start(datetime(2023, 4, 15, 7))

        # 4. 检查
        resp_json = book_api.book_get_id(client, book_id=1)
        assert resp_json['booking']['booking']['process'] == Process.RUN
    

    @pytest.mark.book_app
    def test_book_inform_sign_after_start(self, client):
        """ 向给定时间未签到预约的用户发送邮件警告违约 """
        self.setup_rooms(client)

        # 1. 登录 Alice 账号
        resp_json = user_api.user_login(client, user_dict={
            'name': 'Alice',
            'password': '111111'
        })
        assert resp_json['success'] == True

        # 2. 创建预约
        resp_json = book_api.book_add(client, book_dict={
            'seat_id': 2,
            'start_time': datetime(2023, 4, 15, 7).__str__(),
            'end_time': datetime(2023, 4, 15, 11).__str__(),
        })
        assert resp_json['success'] != False

        # 3. 发出警告
        book_api.book_inform_sign_after_start(datetime(2023, 4, 15, 7))

    
    @pytest.mark.book_app
    def test_book_inform_mark_after_start(self, client):
        """ 向给定时间未签到预约的用户发送邮件通知违约 """
        self.setup_rooms(client)

        # 1. 登录 Alice 账号
        resp_json = user_api.user_login(client, user_dict={
            'name': 'Alice',
            'password': '111111'
        })
        assert resp_json['success'] == True

        # 2. 创建预约
        resp_json = book_api.book_add(client, book_dict={
            'seat_id': 2,
            'start_time': datetime(2023, 4, 15, 7).__str__(),
            'end_time': datetime(2023, 4, 15, 11).__str__(),
        })
        assert resp_json['success'] != False

        # 3. 标记违约
        book_api.book_inform_mark_after_start(datetime(2023, 4, 15, 7))

        # 4. 检查
        resp_json = book_api.book_get_id(client, book_id=1)
        assert resp_json['booking']['booking']['process'] == Process.MARK

        resp_json = user_api.user_get_self(client)
        assert resp_json['data']['mark'] == 1

    
    

        