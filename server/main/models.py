from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey, ForeignKeyConstraint, PickleType
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
    # profile_pic = Column(String(300)) # stores filepath to image in filesystem

    is_authenticated = Column(Boolean)
    is_active = Column(Boolean)

    start_time = Column(DateTime)
    end_time = Column(DateTime)

    swipe_count = Column(Integer)
    swipe_price = Column(Float)

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

    def get_id(self):
        return str(self.id)

    def get_start_time(self):
        return self.start_time.strftime("%I:%M %p")

    def get_end_time(self):
        return self.end_time.strftime("%I:%M %p")

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
    accepted_status = Column(Boolean, default=False)
    swipe_redeemed = Column(Boolean, default=False)
    notified_status = Column(Boolean, default=False)

    client = Column(PickleType)
    seller = Column(PickleType)
    # client = Column(PickleType, ForeignKey('users'))
    # users = relationship(User, foreign_keys=[client])
    # seller = Column(PickleType, ForeignKey('users'))
    # users = relationship(User, foreign_keys=[seller])

    meet_time = Column(DateTime)

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
