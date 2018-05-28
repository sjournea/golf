"""db_connect_local.py"""
from .db_connect import DBConnect
from .data.test_data import DBGolfRounds
from .data.test_courses import DBGolfCourses
from .data.test_players import DBGolfPlayers
from .exceptions import GolfDBException
from util.tl_logger import TLLog

log = TLLog.getLogger( 'golfdb' )


class MyList(list):
  def count(self):
    return len(self)


class DBConnectLocal(DBConnect):
  DATABASE = 'golf'
  dct_databases = {
    'golf': ['players', 'courses', 'rounds'],
    'golf_test': ['players', 'courses', 'rounds'],
  }

  def __init__(self, db, **kwargs):
    DBConnect.__init__(self, db, **kwargs)
    self._database = kwargs.get('database', self.DATABASE)
    self._courses = MyList(DBGolfCourses[:])
    self._players = MyList(DBGolfPlayers[:])
    self._rounds = MyList(DBGolfRounds[:])

  def databases(self, **kwargs):
    """ return dictionaries of database names with list of collection namess """
    return self.dct_databases

  def create_database(self, **kwargs):
    pl = kwargs.get('players', DBGolfPlayers)
    co = kwargs.get('courses', DBGolfCourses)
    ro = kwargs.get('rounds', DBGolfRounds)
    self._courses = MyList(co[:])
    self._players = MyList(pl[:])
    self._rounds = MyList(ro[:])

  def drop_database(self, database=None):
    """Remove a database."""
    database = str(database) if database else self._database
    self.dct_databases.pop(database)

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
    limit = kwargs.get('limit', 20)
    skip = kwargs.get('skip', 0)
    dbclass = kwargs.get('dbclass')
    lst = [dct for dct in self._courses[skip:skip+limit]]
    if dbclass:
      lst = [dbclass(dct=dct) for dct in lst]
    return lst

  def courseFind(self, name, **kwargs):
    """Return a list of courses that match name."""
    limit = kwargs.get('limit', 20)
    skip = kwargs.get('skip', 0)
    dbclass = kwargs.get('dbclass')
    lst = [dct for dct in self.courses if name in dct['name']]
    if dbclass:
      lst = [dbclass(dct=dct) for dct in lst]
    return lst

  def playerList(self, **kwargs):
    """Return a list of all players."""
    limit = kwargs.get('limit', 20)
    skip = kwargs.get('skip', 0)
    dbclass = kwargs.get('dbclass')
    lst = [dct for dct in self.players[skip:skip+limit]]
    if dbclass:
      lst = [dbclass(dct=dct) for dct in lst]
    return lst

  def playerFind(self, email, **kwargs):
    """Return a matching player by email."""
    limit = kwargs.get('limit', 20)
    skip = kwargs.get('skip', 0)
    dbclass = kwargs.get('dbclass')
    lst = [dct for dct in self.players[skip:skip+limit] if email in dct['email']]
    if dbclass:
      lst = [dbclass(dct=dct) for dct in lst]
    return lst

  def playerSave(self, player):
    """Return a matching player by email."""
    for pl in self.players:
      if pl['email'] == player.email:
        raise GolfDBException('Duplicate key error')
    self.players.append(player.toDict())

  def roundList(self, **kwargs):
    """Return a list of all rounds."""
    limit = kwargs.get('limit', 20)
    skip = kwargs.get('skip', 0)
    dbclass = kwargs.get('dbclass')
    lst = [dct for dct in self.rounds[skip:skip+limit]]
    if dbclass:
      lst = [dbclass(dct=dct) for dct in lst]
    return lst

  def roundFind(self, name, **kwargs):
    """Return a matching round by course name."""
    """Return a list of all rounds."""
    limit = kwargs.get('limit', 20)
    skip = kwargs.get('skip', 0)
    dbclass = kwargs.get('dbclass')
    lst = [dct for dct in self.rounds[skip:skip+limit] if name in dct['course']['name']]
    if dbclass:
      lst = [dbclass(dct=dct) for dct in lst]
    return lst

