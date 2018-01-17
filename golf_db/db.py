"""db.py - databae wrapper for golf objects.
"""
import platform
from .db_connect_local import DBConnectLocal
from .exceptions import GolfDBException

from util.tl_logger import TLLog

log = TLLog.getLogger( 'golfdb' )

class GolfDB(object):
  """Database wrapper for golf objects."""
  DATABASE = 'golf'

  connections = {'local': DBConnectLocal }
  if platform.uname()[0] == 'Linux':
    from .db_connect_mongo import DBConnectMongo
    connections['mongo'] = DBConnectMongo
  
  def __init__(self, **kwargs):
    self.db_type = kwargs.get('db_type', 'local')
    self.database = kwargs.get('database', self.DATABASE)
    self.conn = None
    self._setup_connection(**kwargs)

  def _setup_connection(self, **kwargs):
    """Create all parameters needed for db_type."""
    if self.db_type in GolfDB.connections:
      self.conn = GolfDB.connections[self.db_type](self, **kwargs)
    else:
      raise GolfDBException('db_type "{}" not supported.'.format(self.db_type))

  def databases(self):
    return self.conn.databases()
  
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
    return self.conn.courseList(**kwargs)

  def courseFind(self, name, **kwargs):
    """Return a list of courses."""
    return self.conn.courseFind(name, **kwargs)
  
  def playerList(self, **kwargs):
    """Return a list of all players."""
    return self.conn.playerList(**kwargs)
  
  def playerFind(self, email, **kwargs):
    """Return a matching player by email."""
    return self.conn.playerFind(email, **kwargs)

  def playerSave(self, player):
    """Return a matching player by email."""
    return self.conn.playerSave(player)

  def roundList(self, **kwargs):
    """Return a list of all rounds."""
    return self.conn.roundList(**kwargs)
  
  def roundFind(self, name, **kwargs):
    """Return a matching round by course name."""
    return self.conn.roundFind(name, **kwargs)

  
class GolfDBAdmin(GolfDB):
  """Database wrapper for golf admin objects."""

  def create(self, **kwargs):
    """Create a new golf database and add all collections and indexes needed."""
    self.conn.create_database()

  def remove(self, database=None):
    """Delete a database."""
    self.conn.drop_database(database)
