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
    self.addMenuItem( MenuItem( 'dc', '',        'create golf database.',   self._createDatabase) )
    self.addMenuItem( MenuItem( 'pli', '',       'player insert.',          self._playerInsert) )
    self.addMenuItem( MenuItem( 'pll', '',       'player list.',            self._playerList) )
    self.addMenuItem( MenuItem( 'plu', '',       'player update.',          self._playerUpdate) )
    self.addMenuItem( MenuItem( 'plr', '',       'player remove.',          self._playerRemove) )
    self.updateHeader()

  def updateHeader(self):
    self.header = 'database url:{} - database:{}'.format(self.url, '???')

  def _createDatabase(self):
    self.db.create_tables()
    
  def _playerInsert(self):
    for arg in self.lstCmd[2:]:
      lst = arg.split('=')
      if lst[0] == 'gross':
        lstGross = eval(lst[1])
    session = self.db.Session()
    for dct in DBGolfPlayers:
      player = Player(**dct)
      session.add(player)
    session.commit()
    
  def _playerList(self):
    session = self.db.Session()
    players = session.query(Player).all()
    print '{} players'.format(len(players))
    for n,player in enumerate(players):
      print '  {:<2}:{}'.format(n+1,player)

  def _playerRemove(self):
    session = self.db.Session()
    query = session.query(Player)
    players = query.all()
    for player in players:
      session.delete(player)
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