"""db_sqlalchemy.py"""
import datetime
from sqlalchemy import Table, Column, ForeignKey
from sqlalchemy import Integer, Float, String, Enum, Text, Date
from sqlalchemy.ext.declarative import declarative_base 
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .player import GolfPlayer
from .course import GolfCourse
from .score import GolfScore
from .test_data import DBGolfCourses, DBGolfPlayers
from .exceptions import GolfDBException
from util.tl_logger import TLLog

log = TLLog.getLogger( 'alchemy' )

Base = declarative_base()

class Player(Base):
  __tablename__ = 'players'
  golf_class = GolfPlayer
  id = Column(Integer(), primary_key=True)
  email = Column(String(64), nullable=False, unique=True)
  dict_value = Column(Text())

  def makeGolf(self):
    dct = eval(self.dict_value)
    return self.golf_class(dct=dct)

class Course(Base):
  __tablename__ = 'courses'
  golf_class = GolfCourse
  id = Column(Integer(), primary_key=True)
  name = Column(String(132), nullable=False, unique=True)
  dict_value = Column(Text(), nullable=False)

  def makeGolf(self):
    dct = eval(self.dict_value)
    return self.golf_class(dct=dct)

class Score(Base):
  __tablename__ = 'scores'
  golf_class = GolfScore
  id = Column(Integer(), primary_key=True)
  player_id = Column(Integer(), ForeignKey('players.id'), nullable=False)
  course_id = Column(Integer(), ForeignKey('courses.id'), nullable=False)
  date_played = Column(Date(), nullable=False)
  dict_value = Column(Text(), nullable=False)
  
  def makeGolf(self):
    dct = eval(self.dict_value)
    return self.golf_class(dct=dct)


class Round(Base):
  __tablename__ = 'rounds'
  id = Column(Integer(), primary_key=True)
  course_id =  Column(Integer(), ForeignKey('courses.id'), nullable=False)
  date_played = Column(Date(), nullable=False, default=datetime.date.today())
  dict_value = Column(Text(), nullable=False)


class Database(object):
  def __init__(self, url):
    self.url = url
    self.engine = create_engine(self.url)
    self.Session = sessionmaker(bind=self.engine)

  def create_session(self):
    return self.Session()

  def create_tables(self):
    """Create all tables."""
    Base.metadata.create_all(self.engine)
  
