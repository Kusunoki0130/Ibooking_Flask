from typing import Any
from sqlalchemy import text, or_, and_, func
from sqlalchemy.exc import SQLAlchemyError, DBAPIError
import sys
print(sys.path)
from ibooking.dao.engine import *
from ibooking.dao.models import *
import typing as t
import sys
from datetime import datetime

class ORMException(Exception):
    
    def __init__(self, message:str):
        super().__init__()
        self.message = message


class ORM:

    
    def create(self, table: Base):
        table.__table__.create(engine, checkfirst=True)


    def insert(self, session, table: Base, values:dict) -> t.Union[int, bool]:
        recd = table(**values)
        try:
            session.add(recd)
            session.commit()
            return recd.id
        except Exception as e:
            session.rollback()
            return False


    def select(self, session, table: Base, cond: str=None, cond_dict :dict=None) -> t.Union[list, None]:
        if cond is None and (cond_dict is None or len(cond_dict.keys()) == 0):
            return session.query(table).all()
        elif cond is not None:
            return session.query(table).filter(eval(cond)).all()
        else:
            return session.query(table).filter_by(**cond_dict).all()
        

    def update(self, session, table: Base, values: dict, cond: str=None, cond_dict: dict=None) -> bool:
        try:
            if cond is None and (cond_dict is None or len(cond_dict.keys()) == 0):
                session.query(table).update(values)
            elif cond is not None:
                session.query(table).filter(eval(cond)).update(values)
            else:
                session.query(table).filter_by(**cond_dict).update(values)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            return False


    def excute(self, sql: str) -> any:
        conn = engine.connect()
        try:
            ret = conn.execute(text(sql))
            try:
                res = ret.fetchall()
                return res
            except Exception as e:
                return ret
        except Exception as e:
            conn.rollback()
            return None



class Entity:

    orm = ORM()

    class EntityTable:


        def __init__(self, table: Base, session: any) -> None:
            self.__table = table
            self.__session = session
    
        
        def all(self) -> list:
            return Entity.orm.select(self.__session, self.__table)

        
        def __getitem__(self, __name:t.Union[str, dict]) -> list:
            if isinstance(__name, str):
                return Entity.orm.select(self.__session, self.__table, cond=__name)
            return Entity.orm.select(self.__session, self.__table, cond_dict=__name)
        
        
        def __setitem__(self, __name:t.Union[str, dict], __value: dict):
            if isinstance(__name, str):
                success = Entity.orm.update(self.__session, self.__table, cond=__name, values=__value)
            success = Entity.orm.update(self.__session, self.__table, cond_dict=__name, values=__value)
            if success is False:
                raise ORMException("Failed when updating " + self.__table.__tablename__)
        

        def append(self, **values:dict):
            return Entity.orm.insert(self.__session, self.__table, values)
    
    
    def __init__(self, session:any=None):
        # Base.metadata.drop_all(engine)
        self.__testing = False
        self.__session = db_session if session is None else session
        self.__tables = {}
        modules = sys.modules[__name__]
        for type_name in dir(modules):
            if  type_name[-5:] == 'Model':
                self.__tables[getattr(modules, type_name).__tablename__] = Entity.EntityTable(getattr(modules, type_name), self.__session)
                Entity.orm.create(getattr(modules, type_name))

    
    def __getitem__(self, __name:str) -> EntityTable:
        assert __name in self.__tables
        return self.__tables[__name]
    
    
    def __setitem__(self, __name:str, table:Base):
        assert __name not in self.__tables
        self.__tables[__name] = Entity.EntityTable(table)
        Entity.orm.create(table)

    
    def append(self, table:Base):
        assert table.__tablename__ not in self.__tables
        self.__tables[table.__tablename__] = Entity.EntityTable(table)
        Entity.orm.create(table)

    
    def __call__(self, sql:str) -> Any:
        return Entity.orm.excute(sql)


    @property
    def testing(self) -> bool:
        return self.__testing

    @testing.setter
    def testing(self, __value:bool):
        if isinstance(__value, bool) and __value:
            self.__session.close()
            Base.metadata.drop_all(engine)
            self.__init__(session=Session())
        self._testing = True


db = Entity()