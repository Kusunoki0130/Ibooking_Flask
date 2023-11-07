from sqlalchemy import Column, DateTime, Integer, String, Boolean, Float, DATE
from .engine import Base, engine
from ..config import *

class UserModel(Base):

    __tablename__ = "users"

    # 自增主键
    id = Column(Integer, primary_key=True, autoincrement=True)
    # 用户名
    name = Column(String(32), unique=True, nullable=False)
    # 用户密码，sha256 + salt
    password = Column(String(32), nullable=False)
    # 邮箱
    email = Column(String(32), unique=True, nullable=False)
    # 权限组编号
    authority = Column(Integer, nullable=False, default=0)
    # 违纪次数
    mark = Column(Integer, nullable=False, default=0)


    def __repr__(self):
        return self.get().__repr__()


    def get(self):
        self_dict = {**self.__dict__}
        if '_sa_instance_state' in self_dict:
            self_dict.pop('_sa_instance_state')
        return self_dict



class RoomModel(Base):
    
    __tablename__ = "rooms"

    # 自增主键
    id = Column(Integer, primary_key=True, autoincrement=True)
    # 房间名
    name = Column(String(32), nullable=False)
    # 所在校区、城市等
    area = Column(String(32), nullable=False)
    # 所在建筑、楼层等
    building = Column(String(32), nullable=False)
    # 经纬度坐标 1
    location_x = Column(Float, nullable=False)
    # 经纬度坐标 2
    location_y = Column(Float, nullable=False)
    # 开始开放时间
    start_time = Column(Integer, nullable=False, default=start_time_default)
    # 开放持续时间
    persist_time = Column(Integer, nullable=False, default=persist_time_default)
    # 对无权限用户隐藏
    is_hidden = Column(Boolean, nullable=False, default=False)


    def __repr__(self):
        return self.get().__repr__()


    def get(self):
        self_dict = {**self.__dict__}
        if '_sa_instance_state' in self_dict:
            self_dict.pop('_sa_instance_state')
        return self_dict


class SeatModel(Base):
    
    __tablename__ = "seats"

    # 自增主键
    id = Column(Integer, primary_key=True, autoincrement=True)
    # 座位编号，存储格式 房间编号_座位在房间内的编号
    seat_id = Column(String(32), unique=True, nullable=False)
    # 自习室编号
    room_id = Column(Integer, nullable=False)
    # 特殊记号： 例如：0，普通；1，有插座；2，靠窗；3，靠窗有插座 ......
    mark = Column(Integer, nullable=False, default=0)
    # 是否被正在被占用
    is_occupy = Column(Boolean, nullable=False, default=False)
    # 对无权限用户隐藏
    is_hidden = Column(Boolean, nullable=False, default=False)


    def __repr__(self):
        return self.get().__repr__()


    def get(self):
        self_dict = {**self.__dict__}
        if '_sa_instance_state' in self_dict:
            self_dict.pop('_sa_instance_state')
        return self_dict



class BookingModel(Base):
    
    __tablename__ = "bookings"

    # 自增主键
    id = Column(Integer, primary_key=True, autoincrement=True)
    # 用户 id
    user_id = Column(Integer, nullable=False)
    # 座位 id
    seat_id = Column(Integer, nullable=False)
    # 开放时间
    start_time = Column(DateTime, nullable=False)
    # 结束时间
    end_time = Column(DateTime, nullable=False)
    # 预约进行度
    process = Column(Integer, nullable=False, default=1) 

    # PROCESS STATUS:
    # 0：未开始；
    PROCESS_WAIT = 1
    # 1: 已签到，未开始；
    PROCESS_SIGN = 2
    # 2：进行中；
    PROCESS_RUN = 4
    # 3：违约（未签到）；
    PROCESS_MARK = 8
    # 4：提前结束；
    PROCESS_STOP = 16
    # 5：取消；
    PROCESS_CANCEL = 32
    # 6：完成
    PROCESS_COMPLETE = 64
    
    def __repr__(self):
        return self.get().__repr__()


    def get(self):
        self_dict = {**self.__dict__}
        if '_sa_instance_state' in self_dict:
            self_dict.pop('_sa_instance_state')
        return self_dict
