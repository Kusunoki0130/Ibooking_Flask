import rsa
import base64

# —————————————————————————————— User 模块接口访问 —————————————————————————————— #

class User_api:

    def user_login(self, client, user_dict:dict=None) -> dict:
        """ 登录 """

        user_dict = {
            'name': 'admin',
            'password': '111111',
        } if user_dict is None else user_dict

        # 1. 获取 rsa 公钥
        resp = client.get("/user/login")
        assert resp.status_code == 200
        
        # 2. 提交登录表单
        public_key = resp.json['public_key']
        user_dict['password'] = str(base64.b64encode(rsa.encrypt(user_dict['password'].encode('utf-8'), rsa.PublicKey.load_pkcs1(public_key.encode('utf-8')))).decode('utf-8'))
        resp = client.post("/user/login", data=user_dict)
        assert resp.status_code == 200
        return resp.json


    def user_get_self(self, client, is_login: bool=True) -> dict:
        """ 客户端获取用户信息 """

        resp = client.get("/user/get_self")
        assert resp.status_code == 200 if is_login else resp.status_code == 401
        return resp.json


    def user_admin_get(self, client, is_login: bool=True, is_admin: bool=True, user_id:int=None) -> dict:
        """ 管理端获取用户信息 """

        if user_id is None:
            resp = client.get("/user/admin/get_all")
        else:
            resp = client.get("/user/admin/get_all", query_string={
                'id': user_id
            })
        assert resp.status_code == 200 if is_login and is_admin else resp.status_code == 401
        return resp.json


    def user_register(self, client, user_dict:dict=None) -> dict:
        """ 注册 """
        
        user_dict = {
            'name': 'Kusunoki_NaN',
            'password': '123456',
            'email': '22210240132@m.fudan.edn.cn'
        } if user_dict is None else user_dict

        # 1. 获取 rsa 公钥
        resp = client.get("/user/register")
        assert resp.status_code == 200

        # 2. 提交注册表单
        public_key = resp.json['public_key']
        user_dict['password'] = str(base64.b64encode(rsa.encrypt(user_dict['password'].encode('utf-8'), rsa.PublicKey.load_pkcs1(public_key.encode('utf-8')))).decode('utf-8'))
        resp = client.post("/user/register", data=user_dict)
        assert resp.status_code == 200
        return resp.json


    def user_logout(self, client, is_login:bool=True) -> dict:
        """ 登出 """

        resp = client.post("/user/logout")
        assert resp.status_code == 200 if is_login else resp.status_code == 401
        return resp.json


    def user_update(self, client, is_login:bool=True, user_dict:dict=None) -> dict:
        """ 客户端更新用户信息 """
        
        user_dict = {
            'password': '123456'
        } if user_dict is None else user_dict

        # 1. 获取 rsa 公钥
        resp = client.get("/user/update")
        assert resp.status_code == 200 if is_login else resp.status_code == 401

        # 2. 提交更新表单
        if resp.status_code == 200:
            public_key = resp.json['public_key']
            if 'password' in user_dict:
                user_dict['password'] = str(base64.b64encode(rsa.encrypt(user_dict['password'].encode('utf-8'), rsa.PublicKey.load_pkcs1(public_key.encode('utf-8')))).decode('utf-8'))
            resp = client.post("/user/update", data=user_dict)
            assert resp.status_code == 200 if is_login else resp.status_code == 401
        
        return resp.json


    def user_admin_update(self, client, is_login:bool=True, is_admin:bool=True, user_dict:dict=None) -> dict:
        """ 管理端更新用户信息 """

        user_dict = {
            'id': 2,
            'mark': True
        }

        # 1. 获取 rsa 公钥
        resp = client.get("/user/admin/public_key")
        assert resp.status_code == 200

        # 2. 提交更新表单
        public_key = resp.json['public_key']
        if 'password' in user_dict:
            user_dict['password'] = str(base64.b64encode(rsa.encrypt(user_dict['password'].encode('utf-8'), rsa.PublicKey.load_pkcs1(public_key.encode('utf-8')))).decode('utf-8'))
        resp = client.post("/user/update", data=user_dict)
        assert resp.status_code == 200 if is_login and is_admin else resp.status_code == 401


user_api = User_api()