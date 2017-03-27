#!/usr/bin/env python
""" dbmain.py - simple query test program for database """ 
import datetime
#import sys
import logging
#import ConfigParser
import traceback
import threading
#import time,datetime,re,os,traceback,pdb

from golf_db.test_data import GolfCourses, GolfPlayers, GolfRounds
from golf_db.player import GolfPlayer
from golf_db.course import GolfCourse
from golf_db.round import GolfRound
from golf_db.db import GolfDB
from util.db_mongo import MongoDB
from util.menu import MenuItem, Menu, InputException
from util.tl_logger import TLLog,logOptions

TLLog.config('logs/dbmain.log', defLogLevel=logging.INFO )

log = TLLog.getLogger( 'dbmain' )

class GolfMenu(Menu):
  def __init__(self, mongo_db, cmdFile=None, **kwargs):
    super(GolfMenu, self).__init__(cmdFile)
    self.db = mongo_db
    self.database = kwargs.get('database')
    self.gdb = GolfDB(database=self.database)
    self.golf_round = None
    # add menu items
    self.addMenuItem( MenuItem( 'dl', '',             'Show databases.' ,                  self._showDatabases) )
    self.addMenuItem( MenuItem( 'dc', '<database>',   'create golf test data database.',   self._createGolfDatabase) )
    self.addMenuItem( MenuItem( 'dr', '<database>',   'Drop a database.',                  self._dropDatabase) )
    self.addMenuItem( MenuItem( 'use', '<database>',  'Use a database.',                   self._useDatabase) )
    self.addMenuItem( MenuItem( 'pll',  '',           'List players.',                     self._listPlayers) )
    self.addMenuItem( MenuItem( 'col',  '',           'List courses.',                     self._listCourses) )
    self.addMenuItem( MenuItem( 'co', '',             'Execute a command',                 self._execute))
    self.addMenuItem( MenuItem( 'cos', '',            'Get a scorecard'  ,                 self._courseGetScorecard))
    self.addMenuItem( MenuItem( 'tp', '',             'test a put ',                       self._playerPut))
    self.addMenuItem( MenuItem( 'rol',  '',           'List rounds.',                      self._listRounds) )
    self.addMenuItem( MenuItem( 'ros', '',            'Round scorecard'  ,                 self._roundGetScorecard))
    self.addMenuItem( MenuItem( 'rob', '',            'Round leaderboard'  ,               self._roundGetLeaderboard))

    self.addMenuItem( MenuItem( 'gcr', '',              'Create a Round of Golf',            self._roundCreate))
    self.addMenuItem( MenuItem( 'gad', '<email> <tee>', 'Add player to Round of Golf',       self._roundAddPlayer))
    self.addMenuItem( MenuItem( 'gst', '',              'Start Round of Golf',               self._roundStart))
    self.addMenuItem( MenuItem( 'gps', '',              'Print Round Scorecard',             self._roundScorecard))
    self.addMenuItem( MenuItem( 'gpl', '',              'Print Round Leaderboard',           self._roundLeaderboard))
    self.addMenuItem( MenuItem( 'gac', '<hole> <gross..>', 'Add Round Scores',               self._roundAddScore))
    self.updateHeader()

    # for wing IDE object lookup, code does not need to be run
    if 0:
      assert isinstance(self.db, MongoDB) 

  def updateHeader(self):
    self.header = 'Mongo DB - host:{} port:{} database:{}'.format(self.db.host, self.db.port, self.database)

  def _showDatabases(self):
    with self.db as session:
      dctDatabases = self.db.databases()
    for database, tables in dctDatabases.items():
      print '{:<15} : {}'.format(str(database), ','.join([str(tbl) for tbl in tables]))

  def _dropDatabase(self):
    self.gdb.remove()

  def _createGolfDatabase(self):
    self.gdb.create()

  def _useDatabase(self):
    if len(self.lstCmd) < 2:
      raise InputException( 'Not enough arguments for %s command' % self.lstCmd[0] )
    self.database = self.lstCmd[1]
    self.gdb = GolfDB(self.database)
    self.updateHeader()

  def _listPlayers(self):
    players = self.gdb.playerList()
    for n,player in enumerate(players):
      print '{} - {}'.format(n,player)
      
  def _listCourses(self):
    courses = self.gdb.courseList()
    for n,course in enumerate(courses):
      print '{} - {}'.format(n,course)
      
  def _listRounds(self):
    rounds = self.gdb.roundList()
    for n,r in enumerate(rounds):
      print '{} - {}'.format(n,r)
      
  def _execute(self):
    if self.database is None:
      raise InputException( 'Database must be set with use command.')      
    if len(self.lstCmd) < 2:
      raise InputException( 'Not enough arguments for %s command' % self.lstCmd[0] )
    with self.db as session:
      db = session.conn[self.database]
      cmd = ' '.join(self.lstCmd[1:])
      cmd_string = 'rc = db.{}'.format(cmd)
      print 'cmd_string:"{}"'.format(cmd_string)
      exec(cmd_string)
      print rc

  def _playerPut(self):
    if self.database is None:
      raise InputException( 'Database must be set with use command.')      
    if len(self.lstCmd) < 2:
      raise InputException( 'Not enough arguments for %s command' % self.lstCmd[0] )
    with self.db as session:
      db = session.conn[self.database]
      dct = db.players.find_one()
      player = GolfPlayer(dct=dct)
      print player
      player.last_name = 'Abbaub'
      player.put(db.players)

  def _courseGetScorecard(self):
    if len(self.lstCmd) < 2:
      raise InputException( 'Not enough arguments for %s command' % self.lstCmd[0] )
    course = self.gdb.courseFind(self.lstCmd[1])
    print course
    dct = course.getScorecard()
    print dct['hdr']
    print dct['par']
    print dct['hdcp']

  def _roundGetScorecard(self):
    if len(self.lstCmd) < 2:
      raise InputException( 'Not enough arguments for %s command' % self.lstCmd[0] )
    rnd = self.gdb.roundFind(self.lstCmd[1])
    print rnd
    dct = rnd.getScorecard()
    print dct['hdr']
    print dct['par']
    print dct['hdcp']
    if 'player_0_gross' in dct: print dct['player_0_gross']['gross_line']
    if 'player_1_gross' in dct: print dct['player_1_gross']['gross_line']
    if 'player_2_gross' in dct: print dct['player_2_gross']['gross_line']
    if 'player_3_gross' in dct: print dct['player_3_gross']['gross_line']

  def _roundGetLeaderboard(self):
    if len(self.lstCmd) < 2:
      raise InputException( 'Not enough arguments for %s command' % self.lstCmd[0] )
    rnd = self.gdb.roundFind(self.lstCmd[1])
    print rnd
    dctLeaderboard = rnd.getLeaderboard()
    print dctLeaderboard['hdr']
    for dct in dctLeaderboard['leaderboard']:
      print dct['line']

  def _roundCreate(self):
    self.golf_round = GolfRound()
    self.golf_round.course = self.gdb.courseFind('Canyon Lakes')
    self.golf_round.date = datetime.datetime(2017, 3, 23)
    self.golf_round.tee = self.golf_round.course.getTee('Blue')
    print self.golf_round

  def _roundAddPlayer(self):
    if self.golf_round is None:
      raise InputException( 'Golf round not created')
    if len(self.lstCmd) < 3:
      raise InputException( 'Not enough arguments for %s command' % self.lstCmd[0] )
    player = self.gdb.playerFind(email=self.lstCmd[1])
    if player is None:
      raise InputException( 'Player "%s" not found in database.' % self.lstCmd[0] )
    self.golf_round.addPlayer(player, tee_name=self.lstCmd[2])
    print self.golf_round

  def _roundStart(self):
    if self.golf_round is None:
      raise InputException( 'Golf round not created')
    self.golf_round.start()
    
  def _roundAddScore(self):
    if self.golf_round is None:
      raise InputException( 'Golf round not created')
    if len(self.lstCmd) < len(self.golf_round.scores) + 1:
      raise InputException( 'Not enough arguments for %s command' % self.lstCmd[0] )
    hole = int(self.lstCmd[1])
    lstGross = [int(gross) for gross in self.lstCmd[2:]]
    self.golf_round.addScores(hole, lstGross)
    
  def _roundScorecard(self):
    if self.golf_round is None:
      raise InputException( 'Golf round not created')
    dct = self.golf_round.getScorecard()
    print dct['hdr']
    print dct['par']
    print dct['hdcp']
    if 'player_0_gross' in dct: print dct['player_0_gross']['gross_line']
    if 'player_1_gross' in dct: print dct['player_1_gross']['gross_line']
    if 'player_2_gross' in dct: print dct['player_2_gross']['gross_line']
    if 'player_3_gross' in dct: print dct['player_3_gross']['gross_line']

  def _roundLeaderboard(self):
    if self.golf_round is None:
      raise InputException( 'Golf round not created')
    dctLeaderboard = self.golf_round.getLeaderboard()
    print dctLeaderboard['hdr']
    for dct in dctLeaderboard['leaderboard']:
      print dct['line']

def main():
  DEF_LOG_ENABLE = 'dbmain'
  DEF_DB_HOST = MongoDB.DEF_HOST
  DEF_DB_PORT = MongoDB.DEF_PORT
  DEF_DATABASE = 'golf'

  # build the command line arguments
  from optparse import OptionParser
  parser = OptionParser()
  parser.add_option( "-o",  "--host", dest="db_host", default=DEF_DB_HOST,
                       help='Database host. Default is "%s"' % DEF_DB_HOST)
  parser.add_option( "-p",  "--port", dest="db_port", default=DEF_DB_PORT,
                       help='Database port. Default is "%s"' % DEF_DB_PORT)
  parser.add_option( "-d",  "--database", dest="database", default=DEF_DATABASE,
                       help='Set database to use. Default is ' )
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
    thrd.setName( 'dbmain' )

    log.info(80*"*")
    log.info( 'dbmain - starting' )
    logOptions(options.lstLogEnable, options.showLogs, log=log)

    # create MongoDB object
    db = MongoDB(host=options.db_host, port=options.db_port)

    # create menu application 
    menu = GolfMenu(db, options.cmdFile, database=options.database)
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