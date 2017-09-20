"""db.py - databae wrapper for golf objects.

"""
from .course import GolfCourse
from .player import GolfPlayer
from .round import GolfRound
from .test_data import DBGolfCourses, DBGolfPlayers, DBGolfRounds

from pymongo import errors
from util.db_mongo import MongoDB

class GolfDBException(Exception):
  pass

class GolfDB(object):
  """Database wrapper for golf objects."""
  DATABASE = 'golf'
  COURSE = 'course'
  PLAYERS = 'players'
  ROUNDS = 'rounds'
  def __init__(self, **kwargs):
    self.host = kwargs.get('host', MongoDB.DEF_HOST)
    self.port = kwargs.get('port', MongoDB.DEF_PORT)
    self.database = kwargs.get('database', self.DATABASE)
    self.db = MongoDB(self.host, self.port)
  
  def create(self, **kwargs):
    """Create all collections and indexes needed."""
    # WARNING -- DB* test_data is changed with mongo db insertion, _id added to all inserted.
    with self.db as session:
      self.db.drop_database(self.database)
      self.db.insert_many(self.database, 'players', DBGolfPlayers)
      self.db.insert_many(self.database, 'courses', DBGolfCourses)
      self.db.insert_many(self.database, 'rounds', DBGolfRounds)
      # create index on player email
      db = session.conn[self.database]
      db.players.create_index('email', unique=True, background=True)
      
  def remove(self, **kwargs):
    """Remove database."""
    with self.db as session:
      self.db.drop_database(self.database)

  def courseList(self, **kwargs):
    """Return a list of courses."""
    return self._buildList('courses', GolfCourse, **kwargs)
  
  def courseCount(self, **kwargs):
    """Return count of courses."""
    return self._countCollection('courses', **kwargs)
  
  def courseFind(self, name):
    """Return a matching course by name."""
    return self._findOne('courses', GolfCourse, query={'name': { '$regex': name}})
  
  def playerList(self, **kwargs):
    """Return a list of all players."""
    return self._buildList('players', GolfPlayer, **kwargs)
  
  def playerCount(self, **kwargs):
    """Return count of players."""
    return self._countCollection('players', **kwargs)
  
  def playerFind(self, email):
    """Return a matching player by email."""
    return self._findOne('players', GolfPlayer, query={'email': { '$regex': email}})

  def playerSave(self, player):
    """Return a matching player by email."""
    return self._saveCollection('players', player.toDict())

  def roundList(self, **kwargs):
    """Return a list of all rounds."""
    return self._buildList('rounds', GolfRound, **kwargs)
  
  def roundCount(self, **kwargs):
    """Return count of rounds."""
    return self._countCollection('rounds', **kwargs)
  
  def roundFind(self, name):
    """Return a matching round by course name."""
    return self._findOne('rounds', GolfRound, query={'course.name': { '$regex': name}})

  def _buildList(self, collection, DBClass, **kwargs):
    """Return a list of all courses by name."""
    lst = []
    limit = kwargs.get('limit', 20)
    skip = kwargs.get('skip', 0)
    with self.db as session:
      db = session.conn[self.database]
      co = db[collection]
      for dct in co.find().limit(limit).skip(skip):
        lst.append(DBClass(dct=dct))
    return lst
    
  def _findOne(self, collection, DBClass, **kwargs):
    """Return a list of all courses by name."""
    query = kwargs.get('query', {})
    with self.db as session:
      db = session.conn[self.database]
      co = db[collection]
      dct = co.find_one(query)
      return DBClass(dct=dct) if dct else None

  def _countCollection(self, collection, **kwargs):
    """Return a list of all courses by name."""
    lst = []
    with self.db as session:
      db = session.conn[self.database]
      co = db[collection]
      return co.count()

  def _saveCollection(self, collection, dct):
    """Save dict to collection."""
    try:
      lst = []
      with self.db as session:
        db = session.conn[self.database]
        co = db[collection]
        co.save(dct)
    except errors.DuplicateKeyError, ex:
      raise GolfDBException('Duplicate key error')
      