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

from golf_db.db_sqlalchemy import Player,Course,Round,Database,Hole,Tee,Result,Score,Game

TLLog.config('logs/sqlmain.log', defLogLevel=logging.INFO )

log = TLLog.getLogger( 'sqlmain' )

class SQLMenu(Menu):
  def __init__(self, **kwargs):
    cmdFile = kwargs.get('cmdFile')
    super(SQLMenu, self).__init__(cmdFile)
    self.url = kwargs.get('url')
    self.db = Database(self.url)
    self._round_id = None
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
    self.addMenuItem( MenuItem( 'coi', 'testdata',       
        'course insert.', self._courseInsert) )
    self.addMenuItem( MenuItem( 'col', '',       
        'course list.', self._courseList) )
    self.addMenuItem( MenuItem( 'cou', '<name> <key,value>', 
        'course update.', self._courseUpdate) )
    self.addMenuItem( MenuItem( 'cor', '',       
        'course remove.', self._courseRemove) )
    self.addMenuItem( MenuItem( 'cos', '',
        'Get a scorecard', self._courseGetScorecard))
    self.addMenuItem( MenuItem( 'gcr', '<course> <YYYY-MM-DD>',
        'Create a Round of Golf',      self._roundCreate))
    self.addMenuItem( MenuItem( 'gad', '<email> <tee>',
        'Add player to Round of Golf', self._roundAddPlayer))
    self.addMenuItem( MenuItem( 'gag', '<game> <players>',
        'Add game to Round of Golf',   self._roundAddGame))
    self.addMenuItem( MenuItem( 'gst', '',
        'Start Round of Golf',         self._roundStart))
    #self.addMenuItem( MenuItem( 'gps', '<game>...',
         #'Print Game Scorecards',               self._roundScorecard))
    #self.addMenuItem( MenuItem( 'gpl', '<game>...',
         #'Print Game Leaderboards',             self._roundLeaderboard))
    #self.addMenuItem( MenuItem( 'gpt', '<game>...',
        #'Print Game Status',                   self._roundStatus))
    #self.addMenuItem( MenuItem( 'gpd', '',
       #'Print Game Scorecards, Leaderboards, Status',                   self._roundDump))
    self.addMenuItem( MenuItem( 'gas', '<hole> gross=<gross..> <pause=enable>',
       'Add Scores',                 self._roundScore))
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
      print '  {:<2}:{}'.format(n+1,player)

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

  def _courseInsert(self):
    """Inserts courses to database."""
    session = self.db.Session()
    if self.lstCmd[1] == 'testdata':
      for dct in DBGolfCourses:
        co = GolfCourse(dct=dct)
        course = Course(name=co.name)
        for n,gh in enumerate(co.holes):
          hole = Hole(par=gh.par, handicap=gh.handicap, num=n+1, course=course)
          session.add(hole)
        for gt in co.tees:
          tee = Tee(gender=gt['gender'], name=gt['name'], rating=gt['rating'], slope=gt['slope'], course=course)
          session.add(tee)
        session.add(course)
    else:
      raise InputException('only testdata allowed for courses insert.')
    session.commit()
    
  def _courseList(self):
    """List all courses in database."""
    session = self.db.Session()
    query = session.query(Course)
    match = 'all'
    if len(self.lstCmd) > 1:
      query = query.filter(Course.name.like('%{}%'.format(self.lstCmd[1])))
      match = 'name contains "{}"'.format(self.lstCmd[1])
    courses = query.all()
    print '{} courses - {}'.format(len(courses), match)
    for n,course in enumerate(courses):
      print '  {:<2}:{}'.format(n+1,course)

  def _courseRemove(self):
    """Remove course from database.
    cor <name>|all
    """
    session = self.db.Session()
    query = session.query(Course)
    if self.lstCmd[1] == 'all':
      courses = query.all()
    else:
      course = query.filter(Course.name.like('%{}%'.format(self.lstCmd[1]))).first()
      courses = [course]
    for course in courses:
      session.delete(course)
    session.commit()

  def _courseUpdate(self):
    """Update a course record.
    cou <name> <key=value> ...
    """
    raise InputException('course update not implemented (yet)')

  def _courseGetScorecard(self):
    if len(self.lstCmd) < 2:
      raise InputException('Not enough arguments for {} command'.format(self.lstCmd[0]))
    session = self.db.Session()
    query = session.query(Course).filter(Course.name.like('%{}%'.format(self.lstCmd[1])))
    course = query.first()
    print course
    dct = course.getScorecard()
    print dct['hdr']
    print dct['par']
    print dct['hdcp']

  def _roundCreate(self):
    if len(self.lstCmd) < 3:
      raise InputException( 'Not enough arguments for %s command' % self.lstCmd[0] )
    course_name = self.lstCmd[1]
    dtPlay = datetime.datetime.strptime(self.lstCmd[2], "%Y-%m-%d")
    # session
    session = self.db.Session()
    query = session.query(Course).filter(Course.name.like('%{}%'.format(self.lstCmd[1])))
    course = query.first()
    golf_round = Round(course_id=course.course_id, date_played=dtPlay)
    session.add(golf_round)
    session.commit()
    # save round id
    self._round_id = golf_round.round_id
    print 'new round id = {}'.format(golf_round.round_id)

  def _roundAddPlayer(self):
    # gap <email like> <tee>
    if self._round_id is None:
      raise InputException( 'Golf round not created')
    if len(self.lstCmd) < 3:
      raise InputException( 'Not enough arguments for %s command' % self.lstCmd[0] )

    session = self.db.Session()
    # get round
    golf_round = session.query(Round).filter(Round.round_id == self._round_id).one()
    # find player
    player = session.query(Player).filter(Player.email.like('%{}%'.format(self.lstCmd[1])) == self._round_id).one()
    # get tee
    tee = session.query(Tee).filter(
      Tee.course_id == golf_round.course_id,
      Tee.gender == player.genderPlural,
      Tee.name == self.lstCmd[2]).one()
    # Create Result
    result = Result(round=golf_round, player_id=player.player_id, tee_id=tee.tee_id)
    result.calcCourseHandicap(player, tee)
    
    print result
    session.add(result)
    session.commit()

  def _roundStart(self):
    if self._round_id is None:
      raise InputException( 'Golf round not created')
    # TODO: Is this even needed
    # self.golf_round.start()

  def _roundAddGame(self):
    if self._round_id is None:
      raise InputException( 'Golf round not created')
    if len(self.lstCmd) < 2:
      raise InputException( 'Not enough arguments for %s command' % self.lstCmd[0] )
    game_type = self.lstCmd[1]

    players = None
    dct = {}
    for arg in self.lstCmd[2:]:
      lst = arg.split('=')
      if lst[0] == 'players':
        players = eval(lst[1])
      else:
        dct[lst[0]] = eval(lst[1])

    session = self.db.Session()
    # get round
    golf_round = session.query(Round).filter(Round.round_id == self._round_id).one()
    golf_round.addGame(session, game_type)
    session.commit()

  def _roundScore(self):
    """ gas <hole> gross=<list> [pause=enable]"""
    if self._round_id is None:
      raise InputException( 'Golf round not created')
    if len(self.lstCmd) < 3:
      raise InputException( 'Not enough arguments for %s command' % self.lstCmd[0] )
    hole = int(self.lstCmd[1])
    pause_command = 'pause'
    lstGross, lstPutts = None, None
    options = {}
    for arg in self.lstCmd[2:]:
      lst = arg.split('=')
      if lst[0] == 'gross':
        lstGross = eval(lst[1])
      elif lst[0] == 'putts':
        lstPutts = eval(lst[1])
      elif lst[0] in ('closest_to_pin'):
        options[lst[0]] = eval(lst[1])
      elif lst[0] == 'pause':
        pause_command += ' '+ lst[1]
      else:
        raise InputException('Unknown argument {}'.format(arg))
    if lstGross is None:
      raise InputException('gross must be set with gas command.')
    #
    session = self.db.Session()
    # get round
    golf_round = session.query(Round).filter(Round.round_id == self._round_id).one()

    dct_score_data = {
      'lstGross': lstGross,
      'lstPutts': lstPutts,
      'options': options,
    }
    golf_round.addScores(session, hole, dct_score_data)
    session.commit()
    
    self._roundDump()
    self.pushCommands([pause_command])

  def _roundDump(self):
    """ dump scorecard, leaderboard, status."""
    session = self.db.Session()
    # get round
    golf_round = session.query(Round).filter(Round.round_id == self._round_id).one()
    games = [game.CreateGame() for game in golf_round.games]

    self._roundScorecard(golf_round, games)
    self._roundLeaderboard(golf_round, games)
    self._roundLeaderboard(golf_round, games, sort_type='money')
    self._roundStatus(golf_round, games)

  def _roundScorecard(self, golf_round, games):
    dct = golf_round.course.getScorecard(ESC=True)
    print dct['title']
    print dct['hdr']
    print dct['par']
    print dct['hdcp']
    for game in games:
      dct = game.getScorecard()
      print dct['header']
      for player in dct['players']:
        print player['line']

  def _roundLeaderboard(self, golf_round, games, **kwargs):
    length = 22
    lstLines = [None for _ in range(10)]
    def update_line(index, msg):
      if lstLines[index] is None:
        lstLines[index] = '{:<22}'.format(msg)
      else:
        lstLines[index] += ' {:<22}'.format(msg)

    header = '{0:-^22}' if kwargs.get('sort_type') == 'money' else '{0:*^22}'
    for game in games:
      dctLeaderboard = game.getLeaderboard(**kwargs)
      update_line(0, header.format(' '+ game.short_description+ ' '))
      update_line(1, dctLeaderboard['hdr'])
      for i,dct in enumerate(dctLeaderboard['leaderboard']):
        update_line(i+2, dct['line'])
    for line in [line for line in lstLines if line is not None]:
      print line

  def _roundStatus(self, golf_round, games):
    for game in games:
      dctStatus = game.getStatus()
      print '{:<15} - {}'.format(game.short_description, dctStatus['line'])



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