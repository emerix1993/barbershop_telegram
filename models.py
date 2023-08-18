import sqlalchemy

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship, sessionmaker
import psycopg2
from psycopg2.extras import RealDictCursor


Base = declarative_base()

engine = create_engine('postgresql://postgres:postgres@localhost:5432/postgres', echo=True)

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, unique=True)
    first_name = Column(String)
    last_name = Column(String)
    phone = Column(String, unique=True, nullable=False)
    procedure = Column(String, nullable=False)
    date = Column(DateTime)
    time = Column(String)

Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()
def __repr__(self):
    return f'User(id={self.chat_id}, first_name={self.first_name}, last_name={self.last_name}, phone={self.phone}, procedure={self.procedure}, date={self.date}, time={self.time})'

