import sqlalchemy

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship, sessionmaker
import psycopg2
from psycopg2.extras import RealDictCursor


Base = declarative_base()

DB_URI = "mysql://admin:admin@localhost/barbershop_telegram"

engine = create_engine(DB_URI)

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, unique=True)
    first_name = Column(String(100))
    last_name = Column(String(100))
    phone = Column(String(50), unique=True, nullable=False)
    procedure = Column(String(50), nullable=False)
    date = Column(DateTime)
    time = Column(String(10))

Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()
def __repr__(self):
    return f'User(id={self.chat_id}, first_name={self.first_name}, last_name={self.last_name}, phone={self.phone}, procedure={self.procedure}, date={self.date}, time={self.time})'

