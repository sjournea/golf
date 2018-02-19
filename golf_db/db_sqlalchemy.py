"""db_sqlalchemy.py"""
import datetime
import enum

from sqlalchemy import Table, Column, ForeignKey
from sqlalchemy import Integer, Float, String, Enum, Text, Date
from sqlalchemy.ext.declarative import declarative_base 
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, relationship, backref

from .exceptions import GolfDBException
from util.tl_logger import TLLog

log = TLLog.getLogger( 'alchemy' )

Base = declarative_base()

class Player(Base):
  __tablename__ = 'players'
  player_id = Column(Integer(), primary_key=True)
  email = Column(String(132), nullable=False, unique=True)
  first_name = Column(String(20))
  last_name = Column(String(20))
  nick_name = Column(String(20))
  handicap = Column(Float())
  gender = Column(Enum('man', 'woman', name='gender'))

  def getFullName(self):
    return '{} {}'.format(self.first_name, self.last_name)
  
  def getInitials(self):
    return self.first_name[0] + self.last_name[0]
  
  def __str__(self):
    return '{:<15} - {:<6} {:<10} {:<8} {:<5} handicap {:.1f}'.format(
        self.email, self.first_name, self.last_name, self.nick_name, self.gender, self.handicap)


class Hole(Base):
  __tablename__ = 'holes'
  hole_id = Column(Integer(), primary_key=True)
  course_id = Column(Integer(), ForeignKey('courses.course_id'), nullable=False)
  num = Column(Integer(), nullable=False)
  par = Column(Integer(), nullable=False)
  handicap = Column(Integer(), nullable=False)
  course = relationship("Course", back_populates="holes")


class Tee(Base):
  __tablename__ = 'tees'
  tee_id = Column(Integer(), primary_key=True)
  course_id = Column(Integer(), ForeignKey('courses.course_id'), nullable=False)
  gender = Column(Enum('mens', 'womens', name='gender'))
  name = Column(String(32), nullable=False)
  rating = Column(Float(), nullable=False)
  slope = Column(Integer(), nullable=False)
  course = relationship("Course", back_populates="tees")


class Course(Base):
  __tablename__ = 'courses'
  course_id = Column(Integer(), primary_key=True)
  name = Column(String(132), nullable=False, unique=True)  
  holes = relationship("Hole", order_by=Hole.hole_id, back_populates="course")  
  tees = relationship("Tee", order_by=Tee.tee_id, back_populates="course")  

  def setStats(self):
    """Par totals."""
    self.out_tot = sum([hole.par for hole in self.holes[:9]])
    self.in_tot  = sum([hole.par for hole in self.holes[9:]])
    self.total   = self.in_tot + self.out_tot

  def getScorecard(self, **kwargs):
    """Return hdr, par and hdcp lines for scorecard."""
    self.setStats()
    hdr  = 'Hole  '
    par  = 'Par   '
    hdcp = 'Hdcp  '
    ESC = kwargs.get('ESC', False)
    for n,hole in enumerate(self.holes[:9]):
      hdr += ' {:>3}'.format(n+1)
      par += ' {:>3}'.format(hole.par)
      hdcp += ' {:>3}'.format(hole.handicap)
    hdr += '  Out '
    par += ' {:>4} '.format(self.out_tot)
    hdcp += '      '
    for n,hole in enumerate(self.holes[9:]):
      hdr += '{:>3} '.format(n+10)
      par += '{:>3} '.format(hole.par)
      hdcp += '{:>3} '.format(hole.handicap)
    hdr += '  In  Tot'
    par += '{:>4} {:>4}'.format(self.in_tot, self.total)
    if ESC:
      hdr += '  ESC'
      
    return { 'title': '{0:*^98}'.format(' '+self.name+' '),
             'hdr': hdr,
             'par': par,
             'hdcp': hdcp,
           }

  def course_par(self):
    return sum([hole.par for hole in self.holes])

  def __str__(self):
    return '{:<40} - {} holes - {} tees par:{}'.format(self.name, len(self.holes), len(
      self.tees), self.course_par())


#class Result(Base):
  #__tablename__ = 'results'
  #result_id = Column(Integer(), primary_key=True)
  #player_id = Column(Integer(), ForeignKey('players.player_id'), nullable=False)
  #course_id = Column(Integer(), ForeignKey('courses.course_id'), nullable=False)
  #date_played = Column(Date(), nullable=False)
  #dict_value = Column(Text(), nullable=False)
  


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
  
