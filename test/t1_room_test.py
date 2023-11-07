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

# —————————————————————————————— Room 模块用例测试 —————————————————————————————— #


class Test_room:

    @pytest.mark.room_app
    def test_room_admin_get_unauthorized(self, client):
        """ 管理端获取所有自习室信息 case 1 : 未登录，或未用管理员登录，HTTP 401 """
        
        # 1. 未登录
        room_api.room_admin_get(client, is_login=False)
        
        # 2. 登录普通用户 Alice 并尝试获取所有自习室信息
        resp_json = user_api.user_login(client, user_dict={
            'name': 'Alice',
            'password': '111111'
        })
        assert resp_json['success'] == True
        room_api.room_admin_get(client, is_admin=False)


    @pytest.mark.room_app
    def test_room_add_unauthorized(self, client):
        """ 创建一个空自习室 case 1 : 未登录，或未用管理员登录，HTTP 401"""
        
        # 1. 未登录
        room_api.room_add(client, is_login=False)

        # 2. 使用普通用户 Alice 登录，并尝试创建空自习室
        resp_json = user_api.user_login(client, user_dict={
            'name': 'Alice',
            'password': '111111'
        })
        assert resp_json['success'] == True
        room_api.room_add(client, is_admin=False)


    @pytest.mark.room_app
    def test_room_add_success(self, client):
        """ 创建一个空自习室 case 2 : 添加成功"""
        
        # 1. 登录 admin 账号
        resp_json = user_api.user_login(client)
        assert resp_json['success'] == True
        
        # 2. 创建空自习室
        room_api.room_add(client)
        assert resp_json['success'] != False

        # 3. 确认是否添加成功
        resp_json = room_api.room_admin_get(client)
        assert len(resp_json['rooms']) == 1


    @pytest.mark.room_app
    def test_room_update_unauthorized(self, client):
        """ 管理端更新某自习室信息 case 1 : 未登录，或未用管理员登录，HTTP 401 """
        
        # 1. 未登录
        room_api.room_update(client, is_login=False)

        # 2. 使用普通用户 Alice 登录，并尝试修改自习室信息
        resp_json = user_api.user_login(client, user_dict={
            'name': 'Alice',
            'password': '111111'
        })
        assert resp_json['success'] == True
        room_api.room_update(client, is_admin=False)
    

    @pytest.mark.room_app
    def test_room_update_room_not_exist(self, client):
        """ 管理端更新某自习室信息 case 3 : 修改成功 """
        
        # 1. 登录 admin 账号，并添加一个自习室
        resp_json = user_api.user_login(client)
        assert resp_json['success'] == True

        # 2. 修改自习室信息
        resp_json = room_api.room_update(client)
        assert resp_json['success'] == False


    @pytest.mark.room_app
    def test_room_update_success(self, client):
        """ 管理端更新某自习室信息 case 4 : 修改成功 """
        
        # 1. 登录 admin 账号，并添加一个自习室
        resp_json = user_api.user_login(client)
        assert resp_json['success'] == True
        resp_json = room_api.room_add(client)
        assert resp_json['success'] != False

        # 2. 修改自习室信息
        room_api.room_update(client)
        assert resp_json['success'] != False

        # 3. 确认是否修改
        resp_json = room_api.room_admin_get(client)
        assert resp_json['rooms']['1'] == {
            'id': 1, 
            'name': '101',
            'area': 'xx校区', 
            'building': 'xx楼', 
            'location_x': 121.51186, 
            'location_y': 31.34207, 
            'start_time': 8,
            'persist_time': 20, 
            'count': 0, 
            'is_hidden': False, 
        }

    
    @pytest.mark.room_app
    def test_seat_admin_get_unauthorized(self, client):
        """ 管理端获取某自习室所有座位信息 case 1 : 未登录，或未用管理员登录，HTTP 401 """
        
        # 1. 未登录
        room_api.seat_admin_get(client, is_login=False)
        
        # 2. 登录普通用户 Alice 并尝试获取所有自习室信息
        resp_json = user_api.user_login(client, user_dict={
            'name': 'Alice',
            'password': '111111'
        })
        assert resp_json['success'] == True
        room_api.seat_admin_get(client, is_admin=False)


    @pytest.mark.room_app
    def test_seat_add_unauthorized(self, client):
        """ 创建 N 个空座位 case 1 : 未登录，或未用管理员登录，HTTP 401 """
        
        # 1. 未登录
        room_api.seat_add(client, is_login=False)

        # 2. 使用普通用户 Alice 登录，并尝试创建座位
        resp_json = user_api.user_login(client, user_dict={
            'name': 'Alice',
            'password': '111111'
        })
        assert resp_json['success'] == True
        room_api.seat_add(client, is_admin=False)


    @pytest.mark.room_app
    def test_seat_add_room_not_exist(self, client):
        """ 创建 N 个空座位 case 2 : 房间不存在 """
        
        # 1. 登录 admin 账号
        resp_json = user_api.user_login(client)
        assert resp_json['success'] == True

        # 2. 直接添加座位
        resp_json = room_api.seat_add(client)
        assert resp_json['success'] == False


    @pytest.mark.room_app
    def test_seat_add_invalid_seat_id(self, client):
        """ 创建 N 个空座位 case 3 : 自习室内的座位序号重复 """
        
        # 1. 登录 admin 账号，并创建一个空自习室
        resp_json = user_api.user_login(client)
        assert resp_json['success'] == True
        resp_json = room_api.room_add(client)
        assert resp_json['success'] != False

        # 2. 自习室内的座位序号重复
        resp_json = room_api.seat_add(client, seat_list=[{
            'room_id': 1, 
            'seat_id': '1_1', 
            'mark': i%2
        } for i in range(3)])
        assert resp_json['success'] == False

    
    @pytest.mark.room_app
    def test_seat_add_success(self, client):
        """ 创建 N 个空座位 case 4 : 添加成功 """
        
         # 1. 登录 admin 账号，并创建一个空自习室
        resp_json = user_api.user_login(client)
        assert resp_json['success'] == True
        resp_json = room_api.room_add(client)
        assert resp_json['success'] != False

        # 2. 向 id 为 1 的房间添加 3 个座位
        resp_json = room_api.seat_add(client)
        assert resp_json['success'] == True

        # 3. 确认是否添加成功
        resp_json = room_api.seat_admin_get(client)
        assert len(resp_json['seats']) == 3
    

    @pytest.mark.room_app
    def test_seat_update_unauthorized(self, client):
        """ 管理端更新某自习室信息 case 1 : 未登录，或未用管理员登录，HTTP 401 """
        
        # 1. 未登录
        room_api.seat_update(client, is_login=False)

        # 2. 使用普通用户 Alice 登录，并尝试修改自习室信息
        resp_json = user_api.user_login(client, user_dict={
            'name': 'Alice',
            'password': '111111'
        })
        assert resp_json['success'] == True
        room_api.seat_update(client, is_admin=False)

    
    @pytest.mark.room_app
    def test_seat_update_seat_not_exist(self, client):
        """ 管理端更新某自习室信息 case 2 :  修改一个不存在的座位 """
        
        # 1. 登录 admin 账号，并创建 1 个空自习室，和 3 个座位
        resp_json = user_api.user_login(client)
        assert resp_json['success'] == True
        resp_json = room_api.room_add(client)
        assert resp_json['success'] != False
        resp_json = room_api.seat_add(client)
        assert resp_json['success'] != False

        # 2. 将 id 为 4 的座位的特殊标记记为 1
        resp_json = room_api.seat_update(client, seat_dict={
            'id': 4,
            'mark': 1
        })
        assert resp_json['success'] == False


    @pytest.mark.room_app
    def test_seat_update_invalid_seat_id(self, client):
        """ 管理端更新某自习室信息 case 3 :  自习室内的座位序号重复 """
        
        # 1. 登录 admin 账号，并创建 1 个空自习室，和 3 个座位
        resp_json = user_api.user_login(client)
        assert resp_json['success'] == True
        resp_json = room_api.room_add(client)
        assert resp_json['success'] != False
        resp_json = room_api.seat_add(client)
        assert resp_json['success'] != False

        # 2. 将 id 为 2 的座位的 seat_id 修改成 id 为 1 的座位的 seat_id
        resp_json = room_api.seat_update(client, seat_dict={
            'id': 2,
            'seat_id': "1_0"
        })
        assert resp_json['success'] == False


    @pytest.mark.room_app
    def test_seat_update_success(self, client):

        """ 管理端更新某自习室信息 case 4 : 正确更新座位信息 """
        
        # 1. 登录 admin 账号，并创建 1 个空自习室，和 3 个座位
        resp_json = user_api.user_login(client)
        assert resp_json['success'] == True
        resp_json = room_api.room_add(client)
        assert resp_json['success'] != False
        resp_json = room_api.seat_add(client)
        assert resp_json['success'] != False

        # 2. 将 id 为 1 的座位的特殊标记设为 1
        resp_json = room_api.seat_update(client)
        assert resp_json['success'] != False

        # 3. 确认修改后的数据
        resp_json = room_api.seat_admin_get(client)
        assert resp_json['seats'][1]['mark'] == 1


    def setup_before_query_room(self, client, has_hidden: bool=False, has_time: bool=False, has_occupy: bool=False):
        """ 运行每个用例前创建一批自习室、座位、预定 """

        # 登录 admin 账号
        resp_json = user_api.user_login(client)
        assert resp_json['success'] == True

        # 添加自习室以及他们的座位
        resp_json = room_api.room_add(client, room_dict={
            'name': 'A101', 
            'area': '江湾校区', 
            'building': '教学楼A', 
            'location_x': 121.51186, 
            'location_y': 31.34207
        }) # 默认自习室，每天开放时间 7:00 ~ 22:00
        assert resp_json['success'] != False
        resp_json = room_api.seat_add(client, seat_list=[{'room_id': 1, 'seat_id': '1_'+str(i+1), 'mark': i%2} for i in range(5)])
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
        resp_json = room_api.seat_add(client, seat_list=[{'room_id': 2, 'seat_id': '2_'+str(i+1), 'mark': i%2} for i in range(5)])
        assert resp_json['success'] != False

        resp_json = room_api.room_add(client, room_dict={
            'name': '2001', 
            'area': '江湾校区', 
            'building': '图书馆', 
            'location_x': 121.51382, 
            'location_y': 31.34269
        }) # 在图书馆的自习室
        assert resp_json['success'] != False
        resp_json = room_api.seat_add(client, seat_list=[{'room_id': 3, 'seat_id': '3_'+str(i+1), 'mark': i%2} for i in range(5)])
        assert resp_json['success'] != False

        if has_hidden:
            resp_json = room_api.room_add(client, room_dict={
                'name': 'A102', 
                'area': '江湾校区', 
                'building': '教学楼A', 
                'location_x': 121.51186, 
                'location_y': 31.34207,
                'is_hidden': True
            }) # 被隐藏的自习室
            assert resp_json['success'] != False
            resp_json = room_api.seat_add(client, seat_list=[{'room_id': 4, 'seat_id': '4_'+str(i+1), 'mark': i%2} for i in range(5)])
            assert resp_json['success'] != False
        
        if has_time:
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
            room_id = 5 if has_hidden else 4
            resp_json = room_api.seat_add(client, seat_list=[{'room_id': room_id, 'seat_id': str(room_id)+'_'+str(i+1), 'mark': i%2} for i in range(5)])
            assert resp_json['success'] != False


        if has_occupy:
            # admin 创建预约
            resp_json = book_api.book_add(client, book_dict={
                'seat_id': 2,
                'start_time': datetime(2023, 4, 15, 15).__str__(),
                'end_time': datetime(2023, 4, 15, 19).__str__()
            })

        # 登出
        resp_json = user_api.user_logout(client)


    @pytest.mark.room_app
    def test_room_get_unauthorized(self, client):
        """ 客户端获取自习室列表 case 1 : 未登录，HTTP 401 """
        
        room_api.room_get(client, is_login=False)

    
    @pytest.mark.room_app
    def test_room_get_hidden(self, client):
        """ 客户端获取自习室列表 case 2 : 存在被隐藏的自习室 """
        self.setup_before_query_room(client, has_hidden=True)

        # 1. 登录 Alice 
        resp_json = user_api.user_login(client, user_dict={
            'name': 'Alice',
            'password': '111111'
        })
        assert resp_json['success'] == True

        # 2. 获取可见的自习室
        resp_json = room_api.room_get(client, query_dict={
            'start_time': datetime(2023, 4, 15, 0).__str__(),
            'end_time': datetime(2023, 4, 16, 0).__str__(),
            'user_location_x': 121.51186,
            'user_location_y': 31.34207,
            'sort_method': "recommendation_basic"
        })
        assert len(resp_json['rooms'].keys()) == 3

    
    @pytest.mark.room_app
    def test_room_get_time(self, client):
        """ 客户端获取自习室列表 case 3 : 存在开放时间不在查询时间内的自习室 """
        self.setup_before_query_room(client, has_time=True)

        # 1. 登录 Alice 
        resp_json = user_api.user_login(client, user_dict={
            'name': 'Alice',
            'password': '111111'
        })
        assert resp_json['success'] == True

        # 2. 获取可见的自习室
        resp_json = room_api.room_get(client, query_dict={
            'start_time': datetime(2023, 4, 15, 7).__str__(),
            'end_time': datetime(2023, 4, 15, 8).__str__(),
            'user_location_x': 121.51186,
            'user_location_y': 31.34207,
            'sort_method': "recommendation_basic"
        })
        assert len(resp_json['rooms'].keys()) == 3


    @pytest.mark.room_app
    def test_room_get_occupy(self, client):
        """ 客户端获取自习室列表 case 4 : 存在查询时间内的已经被占用的座位 """
        self.setup_before_query_room(client, has_occupy=True)

        # 1. 登录 Alice 
        resp_json = user_api.user_login(client, user_dict={
            'name': 'Alice',
            'password': '111111'
        })
        assert resp_json['success'] == True

        # 2. 获取可见的自习室
        resp_json = room_api.room_get(client, query_dict={
            'start_time': datetime(2023, 4, 15, 15).__str__(),
            'end_time': datetime(2023, 4, 15, 20).__str__(),
            'user_location_x': 121.51186,
            'user_location_y': 31.34207,
            'sort_method': "recommendation_basic"
        })
        assert resp_json['rooms']['1']['count'] == 4


    @pytest.mark.room_app
    def test_room_get_complex(self, client):
        """ 客户端获取自习室列表 case 5 : 包含 case 2,3,4 的复杂情况 """
        self.setup_before_query_room(client, has_hidden=True, has_time=True, has_occupy=True)

        # 1. 登录 Alice 
        resp_json = user_api.user_login(client, user_dict={
            'name': 'Alice',
            'password': '111111'
        })
        assert resp_json['success'] == True

        # 2. 获取可见的自习室
        resp_json = room_api.room_get(client, query_dict={
            'start_time': datetime(2023, 4, 15, 15).__str__(),
            'end_time': datetime(2023, 4, 15, 16).__str__(),
            'user_location_x': 121.51186,
            'user_location_y': 31.34207,
            'sort_method': "recommendation_basic"
        })
        assert len(resp_json['rooms'].keys()) == 3
        assert resp_json['rooms']['1']['count'] == 4


    def setup_before_query_seat(self, client, has_hidden: bool=False, has_occupy: bool=False):
        """ 运行每个用例前创建一批自习室、座位、预定 """

        # 登录 admin 账号
        resp_json = user_api.user_login(client)
        assert resp_json['success'] == True

        # 添加自习室以及他们的座位
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
        resp_json = room_api.seat_add(client, seat_list=[{'room_id': 1, 'seat_id': '1_'+str(i+1), 'mark': i%2} for i in range(5)])
        assert resp_json['success'] != False

        if has_hidden:
            resp_json = room_api.seat_update(client, seat_dict={
                'id': 1,
                'is_hidden': 'True'
            })
            assert resp_json['success'] != False

        if has_occupy:
            # admin 创建预约
            resp_json = book_api.book_add(client, book_dict={
                'seat_id': 2,
                'start_time': datetime(2023, 4, 15, 15).__str__(),
                'end_time': datetime(2023, 4, 15, 19).__str__()
            })

        # 登出
        resp_json = user_api.user_logout(client)


    @pytest.mark.room_app
    def test_seat_get_unauthorized(self, client):
        """ 客户端获取自习室列表 case 1 : 未登录，HTTP 401 """

        room_api.seat_get(client, is_login=False)

    
    @pytest.mark.room_app
    def test_seat_get_hidden(self, client):
        """ 客户端获取自习室列表 case 2 : 存在被隐藏的座位 """
        self.setup_before_query_seat(client, has_hidden=True)

        # 1. 登录 Alice 
        resp_json = user_api.user_login(client, user_dict={
            'name': 'Alice',
            'password': '111111'
        })
        assert resp_json['success'] == True

        # 2. 获取可见的座位
        resp_json = room_api.seat_get(client, query_dict={
            'room_id': 1,
            'start_time': datetime(2023, 4, 15, 15).__str__(),
            'end_time': datetime(2023, 4, 15, 16).__str__(),
        })
        assert len(resp_json['seats']) == 4


    @pytest.mark.room_app
    def test_seat_get_occupy(self, client):
        """ 客户端获取自习室列表 case 3 : 存在查询时间内的已经被占用的座位 """
        self.setup_before_query_seat(client, has_occupy=True)

        # 1. 登录 Alice 
        resp_json = user_api.user_login(client, user_dict={
            'name': 'Alice',
            'password': '111111'
        })
        assert resp_json['success'] == True

        # 2. 获取可见的座位
        resp_json = room_api.seat_get(client, query_dict={
            'room_id': 1,
            'start_time': datetime(2023, 4, 15, 15).__str__(),
            'end_time': datetime(2023, 4, 15, 16).__str__(),
        })
        assert len(resp_json['seats']) == 4


    @pytest.mark.room_app
    def test_seat_get_complex(self, client):
        """ 客户端获取自习室列表 case 4 : 包含 case 2,3 的复杂情况 """
        self.setup_before_query_seat(client, has_hidden=True, has_occupy=True)

        # 1. 登录 Alice 
        resp_json = user_api.user_login(client, user_dict={
            'name': 'Alice',
            'password': '111111'
        })
        assert resp_json['success'] == True

        # 2. 获取可见的座位
        resp_json = room_api.seat_get(client, query_dict={
            'room_id': 1,
            'start_time': datetime(2023, 4, 15, 15).__str__(),
            'end_time': datetime(2023, 4, 15, 16).__str__(),
        })
        assert len(resp_json['seats']) == 3