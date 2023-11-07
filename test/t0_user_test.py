import json
import logging
import rsa
import base64
import pytest
from .user_api_access import user_api

# —————————————————————————————— User 模块用例测试 —————————————————————————————— #

class Test_user:

    @pytest.mark.user_app
    def test_user_login_invalid_username(self, client):
        """ 登录测试 case 1 : 用户名不存在 """

        resp_json = user_api.user_login(client, user_dict={
            'name': 'admin_1',
            'password': '111111',
        })
        assert resp_json == {
            'success': False,
            'msg': "username invalid"
        }


    @pytest.mark.user_app
    def test_user_login_invalid_password(self, client):
        """ 登录测试 case 2 : 密码错误 """

        resp_json = user_api.user_login(client, user_dict={
            'name': 'admin',
            'password': '123456',
        })

        assert resp_json == {
            'success': False,
            'msg': "password invalid"
        }


    @pytest.mark.user_app
    def test_user_login_success(self, client):
        """ 登录测试 case 3 : 正确登录 """

        resp_json = user_api.user_login(client, user_dict={
            'name': 'admin',
            'password': '111111',
        })

        assert resp_json == {
            'success': True,
            'msg': "login success"
        }


    @pytest.mark.user_app
    def test_user_get_self_unauthorized(self, client):
        """ 获取个人信息 case 1 : 未登录, HTTP 401"""

        # 1. 未登录无法获取个人信息
        resp = user_api.user_get_self(client, is_login=False)
        

    @pytest.mark.user_app
    def test_user_get_self_success(self, client):
        """ 获取个人信息 case 2 ： 登录后正确获取个人信息"""

        # 1. 正确登录
        resp_json = user_api.user_login(client, user_dict={
            'name': 'Alice',
            'password': '111111'
        })
        assert resp_json['success'] == True

        # 2. 成功获取个人信息
        resp_json = user_api.user_get_self(client)
        assert resp_json['data']['id'] == 2


    @pytest.mark.user_app
    def test_user_admin_get_unauthorized(self, client):
        """ 管理端获取用户信息 case 1 : 未登录，未用管理员账号登录 HTTP 401"""

        # 1. 未登录无法获取个人信息
        user_api.user_admin_get(client, is_login=False, is_admin=False)

        # 2. 登录普通用户 Alice 无法获取
        resp_json = user_api.user_login(client, user_dict={
            'name': 'Alice',
            'password': '111111'
        })
        assert resp_json['success'] == True

        user_api.user_admin_get(client, is_admin=False)


    @pytest.mark.user_app
    def test_user_admin_get_success(self, client):
        """ 管理端获取用户信息 case 2 ： 登录管理员账号后正确获取个人信息"""

        # 1. 正确登录管理员账号
        resp_json = user_api.user_login(client)
        assert resp_json['success'] == True

        # 2. 成功获取 Alice 信息
        resp_json = user_api.user_admin_get(client, user_id=2)
        assert resp_json['data']['id'] == 2

        # 3. 成功获取所有人信息
        resp_json = user_api.user_admin_get(client)
        assert len(resp_json['data']) == 2

        # 4. 当查询不存在用户时，得到 None
        resp_json = user_api.user_admin_get(client, user_id=114514)
        assert resp_json['data'] == None


    @pytest.mark.user_app
    def test_user_rigister_invalid_username(self, client):
        """ 注册测试 case 1 : 用户名重复"""
        
        # 1. 尝试注册用户名为 Alice 的账户
        resp_json = user_api.user_register(client, user_dict={
            'name': 'Alice',
            'password': '111111',
            'email': "xxxxx@qq.com"
        })
        assert resp_json['success'] == False


    @pytest.mark.user_app
    def test_user_rigister_invalid_email(self, client):
        """ 注册测试 case 2 : 电子邮箱重复"""
        
        # 1. 尝试注册用户名为 Alice 的账户
        resp_json = user_api.user_register(client, user_dict={
            'name': 'Bob',
            'password': '111111',
            'email': "1505979366@qq.com"
        })
        assert resp_json['success'] == False


    @pytest.mark.user_app
    def test_user_rigister_success(self, client):
        """ 注册测试 case 3 : 正确注册"""
        
        # 1. 尝试注册用户名为 Alice 的账户
        resp_json = user_api.user_register(client, user_dict={
            'name': 'Bob',
            'password': '111111',
            'email': "xxxxx@qq.com"
        })
        assert resp_json['success'] != False


    @pytest.mark.user_app
    def test_user_logout_unauthorized(self, client):
        """ 登出测试 case 1 : 未登录，HTTP 401"""

        user_api.user_logout(client, is_login=False)

    
    @pytest.mark.user_app
    def test_user_logout_success(self, client):
        """ 登出测试 case 2 : 在登录的情况下正确登出 """

        # 1. 登出 admin 账号
        resp_json = user_api.user_login(client)
        assert resp_json['success'] == True
        
        # 2. 正确登出
        resp_json = user_api.user_logout(client)
        assert resp_json['msg'] == 'logout'


    @pytest.mark.user_app
    def test_user_update_unauthorized(self, client):
        """ 用户更新个人信息测试 case 1 : 未登录，HTTP 401 """

        user_api.user_update(client, is_login=False)


    @pytest.mark.user_app
    def test_user_update_invalid_username(self, client):
        """ 用户更新个人信息测试 case 2 : 用户名重复 """

        # 1. 登录 admin 账号
        resp_json = user_api.user_login(client)
        assert resp_json['success'] == True
        
        # 2. 将 admin 的名称改为 Alice
        resp_json = user_api.user_update(client, user_dict={
            'name': 'Alice'
        })
        assert resp_json['success'] == False


    @pytest.mark.user_app
    def test_user_update_invalid_email(self, client):
        """ 用户更新个人信息测试 case 3 : 邮箱重复 """

        # 1. 登录 admin 账号
        resp_json = user_api.user_login(client)
        assert resp_json['success'] == True

        # 2. 将 admin 的邮箱改为 Alice 的邮箱
        resp_json = user_api.user_update(client, user_dict={
            'email': '1505979367@qq.com'
        })
        assert resp_json['success'] == False

    
    @pytest.mark.user_app
    def test_user_update_success(self, client):
        """ 用户更新个人信息测试 case 3 : 邮箱重复 """

        # 1. 登录 admin 账号
        resp_json = user_api.user_login(client)
        assert resp_json['success'] == True

        # 2. 将 admin 的密码改为 123456
        resp_json = user_api.user_update(client, user_dict={
            'password': '123456'
        })
        assert resp_json['success'] == True

        # 3. 登出 admin 账号
        user_api.user_logout(client)

        # 3. 测试能否正常登录 admin 账号
        resp_json = user_api.user_login(client, user_dict={
            'name': 'admin',
            'password': '123456'
        })
        assert resp_json['success'] == True
