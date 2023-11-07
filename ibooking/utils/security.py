from ast import List
from flask_login import UserMixin, current_user
from ibooking.dao.models import UserModel
from ibooking.dao.Entity import db
from werkzeug.security import check_password_hash
from functools import wraps
from flask import current_app

class User(UserMixin):
    def __init__(self, user_dict: dict):
        self.id = user_dict['id']
        self.name = user_dict['name']
        self.pwdhash = user_dict['password']
        self.email = user_dict['email']
        self.authority = user_dict['authority']
        self.mark = user_dict['mark']

    def verify_password(self, password:str) -> bool:
        if password is None:
            return False
        return check_password_hash(self.pwdhash, password)

    def check_authority(self, authority) -> bool:
        return self.authority == authority

    @staticmethod
    def get(id:int) -> dict:
        if id is None:
            return None
        users = db['users'][{'id': id}]
        if len(users) == 0:
            return None
        return User(users[0].get())


def authority_requried(authority_group:list=None):

    if authority_group is None:
        authority_group = [1]

    def inner(func):
        @wraps(func)
        def decorator(*args, **kwargs):
            for authoirty in authority_group:
                if current_user.check_authority(authoirty):
                    return func(*args, **kwargs)
            return current_app.login_manager.unauthorized()
        return decorator
    return inner