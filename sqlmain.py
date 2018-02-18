#!/usr/bin/env python
""" dbmain.py - simple query test program for database """ 
import ast
import datetime
#import sys
import logging
#import ConfigParser
import os
import traceback
import threading
#import time,datetime,re,os,traceback,pdb

from golf_db.test_data import GolfCourses, GolfPlayers, GolfRounds, RoundsPlayed
from golf_db.player import GolfPlayer
from golf_db.course import GolfCourse
from golf_db.round import GolfRound
from golf_db.game_factory import GolfGameList
from golf_db.test_data import DBGolfCourses, DBGolfPlayers

# from golf_db.db import GolfDB, GolfDBAdmin
from util.menu import MenuItem, Menu, InputException, FileInput
from util.tl_logger import TLLog,logOptions

from golf_db.db_sqlalchemy import Player,Course,Round,Database

TLLog.config('logs/sqlmain.log', defLogLevel=logging.INFO )

log = TLLog.getLogger( 'sqlmain' )

class SQLMenu(Menu):
  def __init__(self, **kwargs):
    cmdFile = kwargs.get('cmdFile')
    super(SQLMenu, self).__init__(cmdFile)
    self.url = kwargs.get('url')
    self.db = Database(self.url)
    # add menu items
    self.addMenuItem( MenuItem( 'dc', '',        
        'create golf database.', self._createDatabase) )
    self.addMenuItem( MenuItem( 'pli', '',       
        'player insert.', self._playerInsert) )
    self.addMenuItem( MenuItem( 'pll', '',       
        'player list.', self._playerList) )
    self.addMenuItem( MenuItem( 'plu', '<email> <key,value>', 
        'player update.', self._playerUpdate) )
    self.addMenuItem( MenuItem( 'plr', '',       
        'player remove.', self._playerRemove) )
    self.updateHeader()

  def updateHeader(self):
    self.header = 'database url:{} - database:{}'.format(self.url, '???')

  def _createDatabase(self):
    self.db.create_tables()
    
  def _playerInsert(self):
    """Inserts ALL players from DBGolfPlayers."""
    session = self.db.Session()
    if self.lstCmd[1] == 'testdata':
      for dct in DBGolfPlayers:
        player = Player(**dct)
        session.add(player)
    else:
      dct = {}
      for values in self.lstCmd[1:]:
        lst = values.split('=')
        dct[lst[0]] = eval(lst[1])
      player = Player(**dct) 
      session.add(player)
    session.commit()
    
  def _playerList(self):
    """List all players in database."""
    session = self.db.Session()
    players = session.query(Player).all()
    print '{} players'.format(len(players))
    for n,player in enumerate(players):
      gp = player.makeGolfPlayer()
      print '  {:<2}:{}'.format(n+1,gp)

  def _playerRemove(self):
    """Remove ALL players from database.
    plr <email>|all
    """
    session = self.db.Session()
    query = session.query(Player)
    if self.lstCmd[1] == 'all':
      players = query.all()
    else:
      player = query.filter(Player.email == self.lstCmd[1]).first()
      players = [player]
    for player in players:
      session.delete(player)
    session.commit()

  def _playerUpdate(self):
    """Update a player record.
    plu <email> <key=value> ...
    """
    session = self.db.Session()
    email = self.lstCmd[1]
    query = session.query(Player)
    player = query.filter(Player.email == email).first()
    for values in self.lstCmd[2:]:
      lst = values.split('=')
      if hasattr(player, lst[0]):
        setattr(player, lst[0], eval(lst[1]))
      else:
        raise InputException('player has no attribute "{}"'.format(lst[0]))
    session.commit()

def main():
  DEF_LOG_ENABLE = 'sqlmain'
  DEF_DATABASE = 'golf'
  DEF_DB_TYPE = 'local'
  DEF_DB_URL = 'sqlite:///golf.sqlite'
  # build the command line arguments
  from optparse import OptionParser
  parser = OptionParser()
  parser.add_option( "-u",  "--url", dest="url", default=DEF_DB_URL,
                     help='SQLAlchemy Comma separated list of log modules to enable, * for all. Default is "%s"' % DEF_LOG_ENABLE)
  parser.add_option( "-m",  "--logEnable", dest="lstLogEnable", default=DEF_LOG_ENABLE,
                       help='Comma separated list of log modules to enable, * for all. Default is "%s"' % DEF_LOG_ENABLE)
  parser.add_option( "-g",  "--showLogs", action="store_true", dest="showLogs", default=False,
                       help='list all log options.' )
  parser.add_option( "-y",  "--runCmdFile", dest="cmdFile", default=None,
                       help="Run a command file at startup.")

  #  parse the command line and set values
  (options, args) = parser.parse_args()

  master = None
  try:
    # set the main thread name
    thrd = threading.currentThread()
    thrd.setName( 'sqlmain' )

    log.info(80*"*")
    ##log.info( 'dbmain - starting' )
    logOptions(options.lstLogEnable, options.showLogs, log=log)

    # create menu application 
    menu = SQLMenu(url=options.url, cmdFile=options.cmdFile)
    menu.runMenu()

  except Exception, err:
    s = '%s: %s' % (err.__class__.__name__, err)
    log.error( s )
    print s

    print '-- traceback --'
    traceback.print_exc()
    print

  finally:
    log.info( 'dbmain - exiting' )
    TLLog.shutdown()        

if __name__ == '__main__':
  main()