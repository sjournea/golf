"""db_connect_mongo.py"""
from pymongo import MongoClient, errors

from .db_connect import DBConnect
from .test_data import DBGolfCourses, DBGolfPlayers, DBGolfRounds
from .exceptions import GolfDBException
from util.tl_logger import TLLog

log = TLLog.getLogger( 'golfdb' )

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
  def databases(self, **kwargs):
    """ return dictionaries of database names with list of collection namess """
    show_all = kwargs.get('show_all') 
    log.debug( 'databases() - show_all:%s' % show_all)
    dct = {}
    lstDBNames = self._conn.database_names()
    if not show_all:
      lstDBNames = [dbName for dbName in lstDBNames if dbName not in self.lstDBIgnore]
    for dbName in lstDBNames:
      db = self._conn[dbName]
      lstCollNames = db.collection_names()
      if not show_all:
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

  def create_database(self, **kwargs):
    pl = kwargs.get('players', DBGolfPlayers)
    co = kwargs.get('courses', DBGolfCourses)
    ro = kwargs.get('rounds', DBGolfRounds)
    # WARNING -- DB* test_data is changed with mongo db insertion, _id added to all inserted.
    self.drop_database()
    self.players.insert_many(pl)
    self.courses.insert_many(co)
    self.rounds.insert_many(ro)
    # create index on player email
    self.players.create_index('email', unique=True, background=True)

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


