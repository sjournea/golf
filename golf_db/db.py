"""db.py - databae wrapper for golf objects.
"""
from pymongo import MongoClient, errors

from .course import GolfCourse
from .player import GolfPlayer
from .round import GolfRound
from .test_data import DBGolfCourses, DBGolfPlayers, DBGolfRounds

from util.tl_logger import TLLog

log = TLLog.getLogger( 'golfdb' )

class GolfDBException(Exception):
  pass


class DBConnect:
  """Base databse connection class."""
  # TODO: Make abstract
  def __init__(self, db, **kwargs):
    self.db = db

class DBConnectMongo(DBConnect):
  DEF_HOST = 'localhost'
  DEF_PORT = 27017
  DATABASE = 'golf'
  
  def __init__(self, db, **kwargs):
    DBConnect.__init__(self, db, **kwargs)
    self.host = kwargs.get('host', self.DEF_HOST)
    self.port = kwargs.get('port', self.DEF_PORT)
    self._conn = MongoClient(host=self.host, port=self.port)
    self._database = self._conn[kwargs.get('database', self.DATABASE)]
    self._courses = self._database.courses
    self._players = self._database.players
    self._rounds = self._database.rounds
    
  lstDBIgnore = ['local']
  lstCollIgnore = ['system.indexes']
  def databases(self, showAll=False):
    """ return dictionaries of database names with list of collection namess """
    log.debug( 'databases() - showAll:%s' % showAll)
    dct = {}
    lstDBNames = self._conn.database_names()
    if not showAll:
      lstDBNames = [dbName for dbName in lstDBNames if dbName not in self.lstDBIgnore]
    for dbName in lstDBNames:
      db = self._conn[dbName]
      lstCollNames = db.collection_names()
      if not showAll:
        lstCollNames = [colName for colName in lstCollNames if colName not in self.lstCollIgnore]
      dct[dbName] = lstCollNames
    return dct

  def drop_database(self, database=None):
    """Remove a database."""
    database = str(database) if database else self._database
    self._conn.drop_database(database)
  
  @property
  def courses(self):
    return self._courses
  
  @property
  def players(self):
    return self._players
  
  @property
  def rounds(self):
    return self._rounds
  
  
class GolfDB(object):
  """Database wrapper for golf objects."""
  DATABASE = 'golf'
  COURSE = 'course'
  PLAYERS = 'players'
  ROUNDS = 'rounds'
  
  def __init__(self, **kwargs):
    self.db_type = kwargs.get('db_type', 'mongo')
    self.database = kwargs.get('database', self.DATABASE)
    self.conn = None
    self._setup_connection(**kwargs)

  def _setup_connection(self, **kwargs):
    """Create all parameters needed for db_type."""
    if self.db_type == 'mongo':
      self.conn = DBConnectMongo(self, **kwargs)
    elif self.db_type == 'rest_api':
      raise GolfDBException('db_type "{}" not implemented (yet).'.format(self.db_type))
    else:
      raise GolfDBException('db_type "{}" not supported.'.format(self.db_type))

  def create(self, **kwargs):
    """Create all collections and indexes needed."""
    # WARNING -- DB* test_data is changed with mongo db insertion, _id added to all inserted.
    self.conn.drop_database()
    self.conn.players.insert_many(DBGolfPlayers)
    self.conn.courses.insert_many(DBGolfCourses)
    self.conn.rounds.insert_many(DBGolfRounds)
    # create index on player email
    self.conn.players.create_index('email', unique=True, background=True)
      
  def databases(self):
    return self.conn.databases()
  
  def remove(self, database=None):
    self.conn.drop_database(database)

  @property
  def courses(self):
    return self.conn.courses
  
  @property
  def players(self):
    return self.conn.players
  
  @property
  def rounds(self):
    return self.conn.rounds
  
  def courseList(self, **kwargs):
    """Return a list of courses."""
    return self._buildList2(self.courses, **kwargs)

  def courseFind(self, name, **kwargs):
    """Return a list of courses."""
    return self._buildList2(self.courses, filter={'name': { '$regex': name}}, **kwargs)
  
  def playerList(self, **kwargs):
    """Return a list of all players."""
    return self._buildList2(self.players, **kwargs)
  
  def playerFind(self, email, **kwargs):
    """Return a matching player by email."""
    return self._buildList2(self.players, filter={'email': { '$regex': email}}, **kwargs)

  def playerSave(self, player):
    """Return a matching player by email."""
    return self._saveCollection2(self.players, player.toDict())

  def roundList(self, **kwargs):
    """Return a list of all rounds."""
    return self._buildList2(self.rounds, **kwargs)
  
  def roundFind(self, name, **kwargs):
    """Return a matching round by course name."""
    return self._buildList2(self.rounds, filter={'course.name': { '$regex': name}}, **kwargs)

  def _buildList2(self, collection, **kwargs):
    """Return a list of all courses by name."""
    lst = []
    filter = kwargs.get('filter', {})
    limit = kwargs.get('limit', 20)
    skip = kwargs.get('skip', 0)
    dbclass = kwargs.get('dbclass')
    lst = [dct for dct in collection.find(filter).limit(limit).skip(skip)]
    if dbclass:
      lst = [dbclass(dct=dct) for dct in lst]
    return lst
    
  def _findOne2(self, collection, **kwargs):
    """Return a list of all courses by name."""
    query = kwargs.get('query', {})
    dbclass = kwargs.get('dbclass')
    dct = collection.find_one(query)
    if dct and dbclass:
      dct = dbclass(dct=dct)
    return dct

  def _saveCollection2(self, collection, dct):
    """Save dict to collection."""
    try:
      collection.save(dct)
    except errors.DuplicateKeyError, ex:
      raise GolfDBException('Duplicate key error')
      