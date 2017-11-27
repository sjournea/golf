import unittest
import datetime

from golf_db.round import GolfRound
from golf_db.course import GolfCourse
from golf_db.test_data import TestGolfPlayers
from golf_db.db import GolfDBAdmin
from golf_db.game_six_point import SixPointGame
from golf_db.player import GolfPlayer
from golf_db.exceptions import GolfException


class GolfSixPointGamePlayersTest(unittest.TestCase):
  @classmethod
  def setUpClass(cls):
    cls.db = GolfDBAdmin(database='golf_game_test')
    cls.db.create()

  def test_wrong_number_of_players(self):
    course_name = 'Canyon Lakes'
    tee_name = 'Blue'
    date_of_round = datetime.datetime(2017, 3, 23)
    lstPlayers = ['sjournea', 'snake', 'spanky', 'reload']
    
    gr = GolfRound()
    gr.course = self.db.courseFind(course_name, dbclass=GolfCourse)[0]
    gr.date = date_of_round
    for email in lstPlayers:
      pl = self.db.playerFind(email, dbclass=GolfPlayer)[0]
      gr.addPlayer(pl, tee_name)

    with self.assertRaises(GolfException):
      g = SixPointGame(gr, gr.scores)

    gr2 = GolfRound()
    gr2.course = self.db.courseFind(course_name, dbclass=GolfCourse)[0]
    gr2.date = date_of_round
    for email in lstPlayers[:2]:
      pl = self.db.playerFind(email, dbclass=GolfPlayer)[0]
      gr2.addPlayer(pl, tee_name)
    with self.assertRaises(GolfException):
      g2 = SixPointGame(gr, gr.scores)

  def test_right_number_of_players(self):
    course_name = 'Canyon Lakes'
    tee_name = 'Blue'
    date_of_round = datetime.datetime(2017, 3, 23)
    lstPlayers = ['sjournea', 'snake', 'spanky']
    
    gr = GolfRound()
    gr.course = self.db.courseFind(course_name, dbclass=GolfCourse)[0]
    gr.date = date_of_round
    for email in lstPlayers:
      pl = self.db.playerFind(email, dbclass=GolfPlayer)[0]
      gr.addPlayer(pl, tee_name)

    g = SixPointGame(gr, gr.scores)
    g.start()


class GolfSixPointGameTest(unittest.TestCase):
  @classmethod
  def setUpClass(cls):
    cls.db = GolfDBAdmin(database='golf_game_test')
    cls.db.create()
    
  def setUp(self):
    course_name = 'Canyon Lakes'
    tee_name = 'Blue'
    date_of_round = datetime.datetime(2017, 3, 23)
    
    self.gr = GolfRound()
    self.gr.course = self.db.courseFind(course_name, dbclass=GolfCourse)[0]
    self.gr.date = date_of_round
    for dct in TestGolfPlayers[:3]:
      pl = GolfPlayer(dct=dct)
      self.gr.addPlayer(pl, tee_name)

  def test_game_init(self):
    g = SixPointGame(self.gr, self.gr.scores)
    
  def test_game_start(self):
    g = SixPointGame(self.gr, self.gr.scores)
    g.start()
    for pl in g.scores:
      self.assertEquals(pl._score, 18*[None])
      self.assertEquals(pl._points, 18*[None])
      self.assertEquals(pl._in, 0)
      self.assertEquals(pl._out, 0)
      self.assertEquals(pl._total, 0)
      
  def test_game_add_score(self):
    g = SixPointGame(self.gr, self.gr.scores)
    g.start()
    g.addScore(0, [4,4,4])
    self.assertEqual(g.scores[0]._points[0], 2)
    self.assertEqual(g.scores[1]._points[0], 2)
    self.assertEqual(g.scores[2]._points[0], 2)
    g.addScore(1, [3,4,4])
    self.assertEqual(g.scores[0]._points[1], 4)
    self.assertEqual(g.scores[1]._points[1], 1)
    self.assertEqual(g.scores[2]._points[1], 1)
    g.addScore(2, [3,3,4])
    self.assertEqual(g.scores[0]._points[2], 3)
    self.assertEqual(g.scores[1]._points[2], 3)
    self.assertEqual(g.scores[2]._points[2], 0)
    g.addScore(3, [3,4,5])
    self.assertEqual(g.scores[0]._points[3], 4)
    self.assertEqual(g.scores[1]._points[3], 2)
    self.assertEqual(g.scores[2]._points[3], 0)
    
  def test_game_scorecard(self):
    g = SixPointGame(self.gr, self.gr.scores)
    g.start()
    dct = g.getScorecard()
    self.assertIn('course', dct)
    self.assertIn('header', dct)
    self.assertIn('players', dct)
    players = dct['players']
    for player in players:
      self.assertIn('line', player)
      self.assertEqual(player['in'], 0)
      self.assertEqual(player['out'], 0)
      self.assertEqual(player['total'], 0)
      
    g.addScore(0, [4,4,4])
    dct = g.getScorecard()
    self.assertIn('course', dct)
    self.assertIn('header', dct)
    self.assertIn('players', dct)
    for player in dct['players']:
      self.assertIn('line', player)
      self.assertEqual(player['in'], 0)
      self.assertEqual(player['out'], 2)
      self.assertEqual(player['total'], 2)

    g.addScore(1, [3,4,4])
    dct = g.getScorecard()
    self.assertIn('course', dct)
    self.assertIn('header', dct)
    self.assertIn('players', dct)
    for player in dct['players']:
      self.assertIn('line', player)
      self.assertIn('in', player)
      self.assertIn('out', player)
      self.assertIn('total', player)

  def test_game_leaderboard(self):
    g = SixPointGame(self.gr, self.gr.scores)
    g.start()
    dct = g.getLeaderboard()
    self.assertIn('hdr', dct)
    self.assertIn('leaderboard', dct)
    players = dct['leaderboard']
    for player in players:
      self.assertIn('player', player)
      self.assertIn('total', player)
      self.assertIn('line', player)
      self.assertIn('pos', player)
      self.assertIn('thru', player)

    g.addScore(1, [4,4,4])
    dct = g.getLeaderboard()
    self.assertIn('hdr', dct)
    self.assertIn('leaderboard', dct)
    players = dct['leaderboard']
    for player in players:
      self.assertIn('player', player)
      self.assertIn('total', player)
      self.assertIn('line', player)
      self.assertIn('pos', player)
      self.assertIn('thru', player)
