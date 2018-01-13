from sqlalchemy import Column, Integer, String, Boolean, Date, Float, ForeignKey, ForeignKeyConstraint
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

from passlib.apps import custom_app_context as pwd_context
import random, string

Base = declarative_base()


class User (Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    email = Column(String(200))
    class_year = Column(String(50))
    password_hash = Column(String(300))

    is_authenticated = Column(Boolean)
    is_active = Column(Boolean)

    start_time = Column(Date)
    end_time = Column(Date)

    swipe_count = Column(Integer)
    swipe_price = Column(Float)

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

    def get_id(self):
        return str(self.id)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'class': self.class_year,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'swipe_count': self.swipe_count,
            'swipe_price': self.swipe_price
        }

class Transactions(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True)
    accepted_status = Column(Boolean)

    client = Column(Integer, ForeignKey('users.id'))
    users = relationship(User, foreign_keys=[client])
    seller = Column(Integer, ForeignKey('users.id'))
    users = relationship(User, foreign_keys=[seller])

    meet_time = Column(Date)

    def get_id(self):
        return str(self.id)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'accepted': self.accepted,
            'requester': self.requester,
            'client': self.client,
            'seller': self.seller,
            'meet_time': self.meet_time,
        }


engine = create_engine('sqlite:///site.db')
Base.metadata.create_all(engine)
