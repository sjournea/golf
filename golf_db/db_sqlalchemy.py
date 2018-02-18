"""db_sqlalchemy.py"""
import datetime
from sqlalchemy import Table, Column, ForeignKey
from sqlalchemy import Integer, Float, String, Enum, Text, Date
from sqlalchemy.ext.declarative import declarative_base 
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .player import GolfPlayer
from .test_data import DBGolfCourses, DBGolfPlayers
from .exceptions import GolfDBException
from util.tl_logger import TLLog

log = TLLog.getLogger( 'alchemy' )

Base = declarative_base()

class Player(Base):
  __tablename__ = 'players'
  player_id = Column(Integer(), primary_key=True)
  email = Column(String(132), nullable=False, unique=True)
  first_name = Column(String(20), default='')
  last_name = Column(String(20), default='')
  nick_name = Column(String(20), default='')
  handicap = Column(Float(), default=0.0)
  gender = Column(Enum('man', 'woman', name='genders'), nullable=False)
  
  def makeGolfPlayer(self):
    dct = {
      'email': self.email,
      'last_name': self.last_name,
      'first_name': self.first_name,
      'nick_name': self.nick_name,
      'handicap': self.handicap,
      'gender': self.gender,
    }
    return GolfPlayer(dct=dct)
  
  def getFullName(self):
    return '{} {}'.format(self.first_name, self.last_name)
  
  def getInitials(self):
    return self.first_name[0] + self.last_name[0]
  
  def __str__(self):
    return '{:<15} - {:<6} {:<10} {:<8} {:<5} handicap {:.1f}'.format(
        self.email, self.first_name, self.last_name, self.nick_name, self.gender, self.handicap)


class Course(Base):
  __tablename__ = 'courses'
  course_id = Column(Integer(), primary_key=True)
  name = Column(String(132), nullable=False, unique=True)
  dict_value = Column(Text(), nullable=False)

  def __str__(self):
    return 'Course {}'.format(self.name)

class Score(Base):
  __tablename__ = 'scores'
  score_id = Column(Integer(), primary_key=True)
  player_id =  Column(Integer(), ForeignKey('players.player_id'), nullable=False)
  course_id =  Column(Integer(), ForeignKey('courses.course_id'), nullable=False)
  date_played = Column(Date(), nullable=False, default=datetime.date.today())
  dict_value = Column(Text(), nullable=False)
  

class Round(Base):
  __tablename__ = 'rounds'
  round_id = Column(Integer(), primary_key=True)
  course_id =  Column(Integer(), ForeignKey('courses.course_id'), nullable=False)
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
  
