import unittest
import datetime

from golf_db.round import GolfRound
from golf_db.test_data import GolfRounds,GolfCourses, GolfPlayers
from golf_db.db import GolfDB
from golf_db.game import GolfGame, GolfGameFactory, SkinsGame, GrossGame, NetGame
from golf_db.exceptions import GolfException

class GolfGameTest(unittest.TestCase):
  @classmethod
  def setUpClass(cls):
    cls.db = GolfDB(database='golf_game_test')
    cls.db.create()
    
  def setUp(self):
    course_name = 'Canyon Lakes'
    tee_name = 'Blue'
    date_of_round = datetime.datetime(2017, 3, 23)
    lstPlayers = ['sjournea', 'snake']
    
    self.gr = GolfRound()
    self.gr.course = self.db.courseFind(course_name)
    self.gr.date = date_of_round
    for email in lstPlayers:
      pl = self.db.playerFind(email)
      self.gr.addPlayer(pl, tee_name)
      
  def test_base_init(self):
    g = GolfGame(self.gr, self.gr.scores)
    self.assertEqual(g.golf_round, self.gr)
    self.assertEqual(g.scores, self.gr.scores)
    self.assertEqual(g.options, {})
    
  def test_base_methods(self):
    g = GolfGame(self.gr, self.gr.scores)
    g.validate()
    g.start()
    g.addScore(0, [])
    g.getScorecard()
    g.getLeaderboard()
    g.complete()
    
class GolfGameFactoryTest(unittest.TestCase):
  def test_games(self):
    lstGames = [
      ('skins', SkinsGame),
      ('gross', GrossGame),
      ('net', NetGame),
    ]
    for game, game_class in lstGames:
      gm_cls = GolfGameFactory(game)
      self.assertEqual(gm_cls, game_class)
    
  def test_bad_game(self):
    with self.assertRaises(GolfException):
      gm_cls = GolfGameFactory('bad_golf_game_name')


class GolfGrossGameTest(unittest.TestCase):
  @classmethod
  def setUpClass(cls):
    cls.db = GolfDB(database='golf_game_test')
    cls.db.create()
    
  def setUp(self):
    course_name = 'Canyon Lakes'
    tee_name = 'Blue'
    date_of_round = datetime.datetime(2017, 3, 23)
    lstPlayers = ['sjournea', 'snake']
    
    self.gr = GolfRound()
    self.gr.course = self.db.courseFind(course_name)
    self.gr.date = date_of_round
    for email in lstPlayers:
      pl = self.db.playerFind(email)
      self.gr.addPlayer(pl, tee_name)

  def test_game_init(self):
    g = GrossGame(self.gr, self.gr.scores)
    
  def test_game_start(self):
    g = GrossGame(self.gr, self.gr.scores)
    g.start()
    for pl in g.scores:
      self.assertEquals(pl.gross['score'], 18*[0])
      self.assertEquals(pl.gross['in'], 0)
      self.assertEquals(pl.gross['out'], 0)
      self.assertEquals(pl.gross['total'], 0)
      self.assertEquals(pl.gross['esc'], 0)
      
  def test_game_add_score(self):
    g = GrossGame(self.gr, self.gr.scores)
    g.start()
    g.addScore(1, [4,4])
    
  def test_game_scorecard(self):
    g = GrossGame(self.gr, self.gr.scores)
    g.start()
    g.addScore(1, [4,4])
    dct = g.getScorecard()
    self.assertIn('header', dct)
    self.assertIn('gross', dct)

  def test_game_leaderboard(self):
    g = GrossGame(self.gr, self.gr.scores)
    g.start()
    g.addScore(1, [4,4])
    dct = g.getLeaderboard()
    self.assertIn('hdr', dct)
    self.assertIn('leaderboard', dct)


class GolfNetGameTest(unittest.TestCase):
  @classmethod
  def setUpClass(cls):
    cls.db = GolfDB(database='golf_game_test')
    cls.db.create()
    
  def setUp(self):
    course_name = 'Canyon Lakes'
    tee_name = 'Blue'
    date_of_round = datetime.datetime(2017, 3, 23)
    lstPlayers = ['sjournea', 'snake']
    
    self.gr = GolfRound()
    self.gr.course = self.db.courseFind(course_name)
    self.gr.date = date_of_round
    for email in lstPlayers:
      pl = self.db.playerFind(email)
      self.gr.addPlayer(pl, tee_name)

  def test_game_init(self):
    g = NetGame(self.gr, self.gr.scores)
    
  def test_game_start(self):
    g = NetGame(self.gr, self.gr.scores)
    g.start()
    for pl in g.scores:
      self.assertEquals(pl.net['score'], 18*[0])
      self.assertEquals(pl.net['in'], 0)
      self.assertEquals(pl.net['out'], 0)
      self.assertEquals(pl.net['total'], 0)
      
  def test_game_add_score(self):
    g = NetGame(self.gr, self.gr.scores)
    g.start()
    g.addScore(1, [4,4])
    
  def test_game_scorecard(self):
    g = NetGame(self.gr, self.gr.scores)
    g.start()
    g.addScore(1, [4,4])
    dct = g.getScorecard()
    self.assertIn('header', dct)
    self.assertIn('net', dct)

  def test_game_leaderboard(self):
    g = NetGame(self.gr, self.gr.scores)
    g.start()
    g.addScore(1, [4,4])
    dct = g.getLeaderboard()
    self.assertIn('hdr', dct)
    self.assertIn('leaderboard', dct)


class GolfSkinsGameTest(unittest.TestCase):
  @classmethod
  def setUpClass(cls):
    cls.db = GolfDB(database='golf_game_test')
    cls.db.create()
    
  def setUp(self):
    course_name = 'Canyon Lakes'
    tee_name = 'Blue'
    date_of_round = datetime.datetime(2017, 3, 23)
    lstPlayers = ['sjournea', 'snake']
    
    self.gr = GolfRound()
    self.gr.course = self.db.courseFind(course_name)
    self.gr.date = date_of_round
    for email in lstPlayers:
      pl = self.db.playerFind(email)
      self.gr.addPlayer(pl, tee_name)

  def test_game_init(self):
    g = SkinsGame(self.gr, self.gr.scores)
    
  def test_game_start(self):
    g = SkinsGame(self.gr, self.gr.scores)
    g.start()
    for pl in g.scores:
      self.assertEquals(pl.net['score'], 18*[0])
      self.assertEquals(pl.net['in'], 0)
      self.assertEquals(pl.net['out'], 0)
      self.assertEquals(pl.net['total'], 0)
      self.assertEquals(pl.skins['skin'], 18*[0])
      self.assertEquals(pl.skins['in'], 0)
      self.assertEquals(pl.skins['out'], 0)
      self.assertEquals(pl.skins['total'], 0)
    self.assertEqual(g.carryover, 1)
    
  def test_game_add_score(self):
    g = SkinsGame(self.gr, self.gr.scores)
    g.start()
    g.addScore(1, [4,4])
    
  def test_game_scorecard(self):
    g = SkinsGame(self.gr, self.gr.scores)
    g.start()
    g.addScore(1, [4,4])
    dct = g.getScorecard()
    self.assertIn('header', dct)
    self.assertIn('skins', dct)

  def test_game_leaderboard(self):
    g = SkinsGame(self.gr, self.gr.scores)
    g.start()
    g.addScore(1, [4,4])
    dct = g.getLeaderboard()
    self.assertIn('hdr', dct)
    self.assertIn('leaderboard', dct)
