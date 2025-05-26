import enum
from datetime import datetime

from sqlalchemy import Column, Enum, Float, ForeignKey, Integer, LargeBinary, String, Text, TIMESTAMP
from sqlalchemy.orm import relationship

from .base import Base


class StatusEnum(enum.Enum):
    new = 'new'
    pending = 'pending'
    accepted = 'accepted'
    rejected = 'rejected'


class User(Base):
    __tablename__ = 'User'
    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    email = Column(String(128), nullable=False, unique=True, index=True)
    surname = Column(String(150), nullable=False)
    name = Column(String(150), nullable=False)
    patronymic = Column(String(150), default='')
    phone = Column(String(15), unique=True)
    pass_added = relationship('PassAdded', back_populates='user')


class Coord(Base):
    __tablename__ = 'Coord'
    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    height = Column(Integer, nullable=False)
    pass_added = relationship('PassAdded', back_populates='coords')


class Level(Base):
    __tablename__ = 'Level'
    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    winter = Column(String(length=2), default='')
    summer = Column(String(length=2), default='')
    autumn = Column(String(length=2), default='')
    spring = Column(String(length=2), default='')
    pass_added = relationship('PassAdded', back_populates='levels')


class Image(Base):
    __tablename__ = 'Image'
    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    title = Column(String(150), nullable=False)
    data = Column(LargeBinary, nullable=False)
    mountain_pass_id = Column(Integer, ForeignKey('Mountain_Pass.id'), nullable=False)
    pass_added = relationship('PassAdded', back_populates='images')


class PassAdded(Base):
    __tablename__ = 'Mountain_Pass'
    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    beauty_title = Column(String(250), nullable=False)
    title = Column(String(250), nullable=False)
    other_titles = Column(String(250), nullable=False)
    connect = Column(Text, default='')
    add_time = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey('User.id'), nullable=False)
    coord_id = Column(Integer, ForeignKey('Coord.id'), nullable=False)
    level_id = Column(Integer, ForeignKey('Level.id'), nullable=False)
    status = Column(Enum(StatusEnum), nullable=False, default='new')
    user = relationship('User', back_populates='pass_added')
    coords = relationship('Coord', back_populates='pass_added')
    levels = relationship('Level', back_populates='pass_added')
    images = relationship('Image', back_populates='pass_added')


