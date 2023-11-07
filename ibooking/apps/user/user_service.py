from ast import List
import sys
sys.path.append("..")
from ibooking.dao.Entity import *
from werkzeug.security import generate_password_hash, check_password_hash
import rsa
import typing as t


class Rsa_key:
    
    def __init__(self):
        self.public_key, self.private_key = rsa.newkeys(512)
        

# 密码传输用密钥
rsa_key = Rsa_key()


# 创建一个新用户
def create_user(name:str, password:str, email:str) -> bool:
    return db['users'].append(name=name, password=generate_password_hash(password), email=email)


# 更新用户信息
def update_user(id:int, name:str=None, password:str=None, email:str=None, authority:int=None, mark:bool=None) -> bool:
    user = db['users'][{'id':int(id)}][0]
    try:
        db['users'][{'id':id}] = {
            'name': name if name is not None and name != "" else user.name,
            'password': generate_password_hash(password) if password is not None and password != "" else user.password,
            'mark': user.mark + 1 if mark is not None and mark else user.mark,
            'authority': int(authority) if authority is not None and authority != "" else user.authority,
            'email': email if email is not None and email != "" else user.email,
            
        }
        return True
    except ORMException as e:
        print(e.message)
        return False


# 获取用户
def get_user(id:int=None, name:str=None) -> t.Union[dict, List, None]:
    
    if id is not None:
        id = int(id)
        ret = db['users'][{'id':id}]
        return ret[0].get() if len(ret)!=0 else None
    elif name is not None:
        ret = db['users'][{'name':name}]
        return ret[0].get() if len(ret)!=0 else None
    else:
        users = db['users'].all()
        ret = [user.get() for user in users]
        print(ret)
        return ret

