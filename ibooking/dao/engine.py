from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy.orm import sessionmaker, declarative_base
import logging


db_handle = logging.FileHandler('ibooking_db.log')
db_handle.setFormatter(logging.Formatter('%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s'))
db_handle.setLevel(logging.DEBUG)

db_logger = logging.getLogger('sqlalchemy')
db_logger.addHandler(db_handle)


engine = create_engine("sqlite:///ibooking_db.db?check_same_thread=False", pool_size=50, echo=False)

if not database_exists(engine.url):
    create_database(engine.url)

Base = declarative_base()
Session = sessionmaker(bind=engine)
db_session = Session()



