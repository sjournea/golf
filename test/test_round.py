import unittest
import datetime

from golf_db.round import GolfRound
from golf_db.test_data import GolfRounds,GolfCourses, GolfPlayers
from golf_db.db import GolfDB
from golf_db.game import SkinsGame
from golf_db.game_gross import GrossGame
from golf_db.game_net import NetGame

class GolfRoundTest(unittest.TestCase):

  def test_init_empty(self):
    # check default parameters
    r = GolfRound()
    self.assertIsNone(r.course)
    self.assertIsNone(r.date)
    self.assertEqual(r.scores, [])
    self.assertEqual(r.games, {})

  def test_init_from_dict(self):
    for dct in GolfRounds:
      r = GolfRound(dct=dct)
      r2 = GolfRound()
      r2.fromDict(dct)
      self.assertEqual(r, r2)
      
  def test_add_games(self):
    # check default parameters
    r = GolfRound()
    skins = r.addGame('skins')
    gross = r.addGame('gross')
    self.assertEqual(len(r.games), 2)
    self.assertIsInstance(r.games['skins'], SkinsGame)
    self.assertIsInstance(r.games['gross'], GrossGame)
    self.assertEqual(skins, r.games['skins'])
    self.assertEqual(gross, r.games['gross'])


class PlayRoundTest(unittest.TestCase):
  @classmethod
  def setUp(cls):
    cls.db = GolfDB(database='golf_round_test')
    cls.db.create()
    
  def test_add_players(self):
    course_name = 'Canyon Lakes'
    tee_name = 'Blue'
    date_of_round = datetime.datetime(2017, 3, 23)
    lstPlayers = ['sjournea', 'snake']
    
    r = GolfRound()
    r.course = self.db.courseFind(course_name)
    r.date = date_of_round
    for email in lstPlayers:
      pl = self.db.playerFind(email)
      r.addPlayer(pl, tee_name)
    self.assertEqual(len(r.scores), 2)
    
  def test_add_games(self):
    course_name = 'Canyon Lakes'
    tee_name = 'Blue'
    date_of_round = datetime.datetime(2017, 3, 23)
    lstPlayers = ['sjournea', 'snake']
    
    r = GolfRound()
    r.course = self.db.courseFind(course_name)
    r.date = date_of_round
    for email in lstPlayers:
      pl = self.db.playerFind(email)
      r.addPlayer(pl, tee_name)
    r.addGame('skins')

  def test_start(self):
    course_name = 'Canyon Lakes'
    tee_name = 'Blue'
    date_of_round = datetime.datetime(2017, 3, 23)
    lstPlayers = ['sjournea', 'snake']
    
    r = GolfRound()
    r.course = self.db.courseFind(course_name)
    r.date = date_of_round
    for email in lstPlayers:
      pl = self.db.playerFind(email)
      r.addPlayer(pl, tee_name)

    r.addGame('gross')
    r.addGame('net')
    r.addGame('skins')
    r.start()

  def test_add_scores(self):
    course_name = 'Canyon Lakes'
    tee_name = 'Blue'
    date_of_round = datetime.datetime(2017, 3, 23)
    lstPlayers = ['sjournea', 'snake']
    
    r = GolfRound()
    r.course = self.db.courseFind(course_name)
    r.date = date_of_round
    for email in lstPlayers:
      pl = self.db.playerFind(email)
      r.addPlayer(pl, tee_name)

    gross = r.addGame('gross')
    net = r.addGame('net')
    skins = r.addGame('skins')
    r.start()
    
    r.addScores(1, [4,4])
    dct = r.getScorecard('gross')
    dct = r.getScorecard('net')
    dct = r.getScorecard('skins')
    dct = r.getLeaderboard('gross')
    dct = r.getLeaderboard('net')
    dct = r.getLeaderboard('skins')

    dct = gross.getScorecard()
    dct = net.getScorecard()
    dct = skins.getScorecard()
    dct = gross.getLeaderboard()
    dct = net.getLeaderboard()
    dct = skins.getLeaderboard()
  