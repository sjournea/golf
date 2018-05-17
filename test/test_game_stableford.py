import unittest
import datetime

from golf_db.round import GolfRound
from golf_db.course import GolfCourse
from golf_db.data.test_data import TestGolfPlayers
from golf_db.db import GolfDBAdmin
from golf_db.game_stableford import StablefordGame
from golf_db.player import GolfPlayer
from golf_db.exceptions import GolfException


class GolfStablefordGameTest(unittest.TestCase):
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
    for dct in TestGolfPlayers:
      pl = GolfPlayer(dct=dct)
      self.gr.addPlayer(pl, tee_name)

  def test_game_init(self):
    g = StablefordGame(self.gr, self.gr.scores)
    self.assertEqual(g.stableford_type, 'Classic')
    self.assertIsNone(g.jokers)

    g = StablefordGame(self.gr, self.gr.scores, stableford_type='British')
    self.assertEqual(g.stableford_type, 'British')
    self.assertIsNone(g.jokers)
    
    with self.assertRaises(GolfException):
      g = StablefordGame(self.gr, self.gr.scores, stableford_type='Spanish')
  
    with self.assertRaises(GolfException):
      g = StablefordGame(self.gr, self.gr.scores, stableford_type='Spanish', jokers=((1,10),(2,11),(3,12)))

    with self.assertRaises(GolfException):
      g = StablefordGame(self.gr, self.gr.scores, stableford_type='Spanish', jokers=((1,10),(2,11),(3,12),(13,)))

    with self.assertRaises(GolfException):
      g = StablefordGame(self.gr, self.gr.scores, stableford_type='Spanish', jokers=((1,5),(2,11),(3,12),(4,13)))

    g = StablefordGame(self.gr, self.gr.scores, stableford_type='Spanish', jokers=((1,10),(2,11),(3,12),(4,13)))
    self.assertEqual(g.stableford_type, 'Spanish')
    self.assertEqual(g.jokers,((1,10),(2,11),(3,12),(4,13)))

  def test_game_wager(self):
    wager = 0.5
    num_players = len(self.gr.scores)
    num_holes = len(self.gr.course.holes)
    g = StablefordGame(self.gr, self.gr.scores, wager=wager)
    self.assertEqual(g.stableford_type, 'Classic')
    self.assertEqual(g._wager, 0.5)
    self.assertEqual(g.total_payout, wager*num_players*num_holes)

  def test_game_start(self):
    g = StablefordGame(self.gr, self.gr.scores)
    g.start()
    for pl in g.scores:
      self.assertEquals(pl._score, 18*[None])
      self.assertEquals(pl.dct_points['holes'], 18*[None])
      self.assertEquals(pl.dct_points['in'], 0)
      self.assertEquals(pl.dct_points['out'], 0)
      self.assertEquals(pl.dct_points['total'], 0)
      
  def test_game_add_score(self):
    g = StablefordGame(self.gr, self.gr.scores)
    g.start()
    g.addScore(0, [4,4,4,4])
    self.assertEqual(g.scores[0].dct_points['holes'][0], 2)
    self.assertEqual(g.scores[1].dct_points['holes'][0], 2)
    self.assertEqual(g.scores[2].dct_points['holes'][0], 2)
    self.assertEqual(g.scores[3].dct_points['holes'][0], 2)
    g.addScore(1, [3,4,5,6])
    self.assertEqual(g.scores[0].dct_points['holes'][1], 8)
    self.assertEqual(g.scores[1].dct_points['holes'][1], 5)
    self.assertEqual(g.scores[2].dct_points['holes'][1], 2)
    self.assertEqual(g.scores[3].dct_points['holes'][1], 0)
    g.addScore(2, [3,3,4,4])
    self.assertEqual(g.scores[0].dct_points['holes'][2], 2)
    self.assertEqual(g.scores[1].dct_points['holes'][2], 2)
    self.assertEqual(g.scores[2].dct_points['holes'][2], 0)
    self.assertEqual(g.scores[3].dct_points['holes'][2], 0)
    
  #def test_game_scorecard(self):
    #g = SixPointGame(self.gr, self.gr.scores)
    #g.start()
    #dct = g.getScorecard()
    #self.assertIn('course', dct)
    #self.assertIn('header', dct)
    #self.assertIn('players', dct)
    #players = dct['players']
    #for player in players:
      #self.assertIn('line', player)
      #self.assertEqual(player['in'], 0)
      #self.assertEqual(player['out'], 0)
      #self.assertEqual(player['total'], 0)
      
    #g.addScore(0, [4,4,4])
    #dct = g.getScorecard()
    #self.assertIn('course', dct)
    #self.assertIn('header', dct)
    #self.assertIn('players', dct)
    #for player in dct['players']:
      #self.assertIn('line', player)
      #self.assertEqual(player['in'], 0)
      #self.assertEqual(player['out'], 2)
      #self.assertEqual(player['total'], 2)

    #g.addScore(1, [3,4,4])
    #dct = g.getScorecard()
    #self.assertIn('course', dct)
    #self.assertIn('header', dct)
    #self.assertIn('players', dct)
    #for player in dct['players']:
      #self.assertIn('line', player)
      #self.assertIn('in', player)
      #self.assertIn('out', player)
      #self.assertIn('total', player)

  #def test_game_leaderboard(self):
    #g = SixPointGame(self.gr, self.gr.scores)
    #g.start()
    #dct = g.getLeaderboard()
    #self.assertIn('hdr', dct)
    #self.assertIn('leaderboard', dct)
    #players = dct['leaderboard']
    #for player in players:
      #self.assertIn('player', player)
      #self.assertIn('total', player)
      #self.assertIn('line', player)
      #self.assertIn('pos', player)
      #self.assertIn('thru', player)

    #g.addScore(1, [4,4,4])
    #dct = g.getLeaderboard()
    #self.assertIn('hdr', dct)
    #self.assertIn('leaderboard', dct)
    #players = dct['leaderboard']
    #for player in players:
      #self.assertIn('player', player)
      #self.assertIn('total', player)
      #self.assertIn('line', player)
      #self.assertIn('pos', player)
      #self.assertIn('thru', player)
