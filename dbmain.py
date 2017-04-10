#!/usr/bin/env python
""" dbmain.py - simple query test program for database """ 
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
from golf_db.db import GolfDB
from util.db_mongo import MongoDB
from util.menu import MenuItem, Menu, InputException, FileInput
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

    self.addMenuItem( MenuItem( 'gcr', '<course> <YYYY-MM-DD>', 'Create a Round of Golf',    self._roundCreate))
    self.addMenuItem( MenuItem( 'gad', '<email> <tee>', 'Add player to Round of Golf',       self._roundAddPlayer))
    self.addMenuItem( MenuItem( 'gag', '<game>',        'Add game to Round of Golf',         self._roundAddGame))
    self.addMenuItem( MenuItem( 'gst', '',              'Start Round of Golf',               self._roundStart))
    self.addMenuItem( MenuItem( 'gps', '<game>...',     'Print Game Scorecards',             self._roundScorecard))
    self.addMenuItem( MenuItem( 'gpl', '<game>...',     'Print Game Leaderboards',           self._roundLeaderboard))
    self.addMenuItem( MenuItem( 'gpt', '<game>...',     'Print Game Statuss',                self._roundStatus))
    self.addMenuItem( MenuItem( 'gac', '<hole> <gross..>', 'Add Round Scores',               self._roundAddScore))

    self.addMenuItem( MenuItem( 'lag', '',                   'List games',                   self._gamesList))

    self.addMenuItem( MenuItem( 'acr', '<index> <games>...', 'Create round',                 self._createRound))
    self.addMenuItem( MenuItem( 'acl', '',                   'List rounds',                  self._listRounds))
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
    game = self.lstCmd[1] if len(self.lstCmd) > 1 else 'gross'
    rnd = self.gdb.roundFind(self.lstCmd[1])
    print rnd
    dct = rnd.getScorecard(game)
    print dct['header']
    print dct['hdr']
    print dct['par']
    print dct['hdcp']
    for player in dct[game]:
      print player['line']

  def _roundGetLeaderboard(self):
    if len(self.lstCmd) < 2:
      raise InputException( 'Not enough arguments for %s command' % self.lstCmd[0] )
    game = self.lstCmd[1] if len(self.lstCmd) > 1 else 'gross'
    rnd = self.gdb.roundFind(self.lstCmd[1])
    print rnd
    dctLeaderboard = rnd.getLeaderboard(game)
    print dctLeaderboard['hdr']
    for dct in dctLeaderboard['leaderboard']:
      print dct['line']

  def _roundCreate(self):
    if len(self.lstCmd) < 3:
      raise InputException( 'Not enough arguments for %s command' % self.lstCmd[0] )
    course_name = self.lstCmd[1]
    dtPlay = datetime.datetime.strptime(self.lstCmd[2], "%Y-%m-%d")
    self.golf_round = GolfRound()
    self.golf_round.course = self.gdb.courseFind(course_name)
    self.golf_round.date = dtPlay
    print self.golf_round

  def _roundAddPlayer(self):
    if self.golf_round is None:
      raise InputException( 'Golf round not created')
    if len(self.lstCmd) < 3:
      raise InputException( 'Not enough arguments for %s command' % self.lstCmd[0] )
    player = self.gdb.playerFind(email=self.lstCmd[1])
    if player is None:
      raise InputException( 'Player "%s" not found in database.' % self.lstCmd[0] )
    tee = self.lstCmd[2]
    self.golf_round.addPlayer(player, tee)
    print self.golf_round

  def _roundAddGame(self):
    if self.golf_round is None:
      raise InputException( 'Golf round not created')
    if len(self.lstCmd) < 2:
      raise InputException( 'Not enough arguments for %s command' % self.lstCmd[0] )
    game = self.lstCmd[1]
    self.golf_round.addGame(game)
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
    lstGames = self.lstCmd[1:]
    for n,game in enumerate(lstGames):
      dct = self.golf_round.getScorecard(game)
      print dct['header']
      if n == 0:
        print dct['course']['hdr']
        print dct['course']['par']
        print dct['course']['hdcp']
      for player in dct[game]:
        print player['line']

  def _roundLeaderboard(self):
    if self.golf_round is None:
      raise InputException( 'Golf round not created')
    lstGames = self.lstCmd[1:]
    for game in lstGames:
      dctLeaderboard = self.golf_round.getLeaderboard(game)
      print dctLeaderboard['hdr']
      for dct in dctLeaderboard['leaderboard']:
        print dct['line']

  def _roundStatus(self):
    if self.golf_round is None:
      raise InputException( 'Golf round not created')
    lstGames = self.lstCmd[1:]
    for game in lstGames:
      dctStatus = self.golf_round.getStatus(game)
      print '{:<10} - {}'.format(game, dctStatus['line'])

  def _createRound(self):
    if len(self.lstCmd) < 2:
      raise InputException( 'Not enough arguments for %s command' % self.lstCmd[0] )
    if self.lstCmd[1] == 'all':
      rounds = [x for x in range(len(RoundsPlayed))]
    else:
      rounds = [int(self.lstCmd[1])]
    lstGames = self.lstCmd[2:]
    output = 'round.txt'
    with open(output, 'wt') as f:
      for index in rounds:
        roundData = RoundsPlayed[index]
        f.write('# create round\n')
        f.write('gcr {} {}\n'.format(roundData['course'], roundData['date']))
        f.write('# add players\n')
        for player,tee in roundData['players']:
          f.write('gad {} {}\n'.format(player, tee))
        f.write('# add games\n')
        for game in lstGames:
          f.write('gag {}\n'.format(game))
        f.write('# start all games\n')
        f.write('gst\n')
        f.write('# show scorecard, leaderboard and status for all games\n')
        f.write('gps {}\n'.format(' '.join(lstGames)))
        f.write('gpl {}\n'.format(' '.join(lstGames)))
        f.write('gpt {}\n'.format(' '.join(lstGames)))
        f.write('pause\n')
        for hole, scores in roundData['scores']:
          f.write('# hole {}\n'.format(hole))
          f.write('gac {} {}\n'.format(hole, ' '.join(str(sc) for sc in scores)))
          f.write('gps {}\n'.format(' '.join(lstGames)))
          f.write('gpl {}\n'.format(' '.join(lstGames)))
          f.write('gpt {}\n'.format(' '.join(lstGames)))
          f.write('pause{}\n'.format(' enable' if hole in [9, 18] else ''))
    # now run this script
    self.cmdFile = FileInput(output)

  def _gamesList(self):
    lstGames = GolfGameList()
    for game in lstGames:
      print game

  def _listRounds(self):
    for n,gr in enumerate(RoundsPlayed):
      print '{:>2} - {} {:<10} players:{}'.format(
        n, gr['date'], gr['course'], len(gr['players']))

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