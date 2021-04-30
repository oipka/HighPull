import sys
# для настройки баз данных
from sqlalchemy import Column, ForeignKey, Integer, String

# для определения таблицы и модели
from sqlalchemy.ext.declarative import declarative_base

# для создания отношений между таблицами
from sqlalchemy.orm import relationship

# для настроек
from sqlalchemy import create_engine

# создание экземпляра declarative_base
Base = declarative_base()

# здесь добавим классы

# создает экземпляр create_engine в конце файла
engine = create_engine('sqlite:///auto.db')

Base.metadata.create_all(engine)

class Auto(Base):
    __tablename__ = 'auto'

    id = Column(Integer, primary_key=True)
    mark = Column(String(250), nullable=False)
    number = Column(String(250), nullable=False)

class Camera(Base):
    __tablename__ = 'camera'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    koord = Column(String(250), nullable=False)

class Check_Map(Base):
    __tablename__ = 'check_map'

    id = Column(Integer, primary_key=True)
    mark = Column(String(250), nullable=False)
    number = Column(String(250), nullable=False)
    koord = Column(String(250), nullable=False)
    time = Column(String(250), nullable=False)
    path = Column(String(250), nullable=False)