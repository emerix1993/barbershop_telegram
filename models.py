import sqlalchemy

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship, sessionmaker

Base = declarative_base()

engine = create_engine('mysql://admin:admin@localhost/barbershop_telegram')

Session = sessionmaker(bind=engine)
session = Session()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, unique=True)
    first_name = Column(String(50))
    last_name = Column(String(50))
    phone = Column(String(50), unique=True, nullable=False)
    procedure = Column(String(50), nullable=False)
    date = Column(DateTime)
    time = Column(String(50))

    Base.metadata.create_all(engine)


    def __repr__(self):
        return f'User(id={self.chat_id}, first_name={self.first_name}, last_name={self.last_name}, phone={self.phone}, procedure={self.procedure}, date={self.date}, time={self.time})'
