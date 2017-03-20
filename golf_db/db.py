"""db.py - databae wrapper for golf objects.

"""
from .course import GolfCourse
from .player import GolfPlayer
from .round import GolfRound
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
  
  def courseList(self, **kwargs):
    """Return a list of courses."""
    return self._buildList('courses', GolfCourse, **kwargs)
  
  def courseCount(self, **kwargs):
    """Return count of courses."""
    return self._countCollection('courses', **kwargs)
  
  def playerList(self, **kwargs):
    """Return a list of all players."""
    return self._buildList('players', GolfPlayer, **kwargs)
  
  def playerCount(self, **kwargs):
    """Return count of players."""
    return self._countCollection('players', **kwargs)
  
  def roundList(self, **kwargs):
    """Return a list of all rounds."""
    return self._buildList('rounds', GolfRound, **kwargs)
  
  def roundCount(self, **kwargs):
    """Return count of rounds."""
    return self._countCollection('rounds', **kwargs)
  
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
    
  def _countCollection(self, collection, **kwargs):
    """Return a list of all courses by name."""
    lst = []
    with self.db as session:
      db = session.conn[self.database]
      co = db[collection]
      return co.count()
  