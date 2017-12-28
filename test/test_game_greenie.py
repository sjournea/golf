import unittest
import datetime

from golf_db.round import GolfRound
from golf_db.player import GolfPlayer
from golf_db.course import GolfCourse
#from golf_db.test_data import GolfRoun7ds,GolfCourses, GolfPlayers
from golf_db.db import GolfDBAdmin
#from golf_db.game import GolfGame, SkinsGame, NetGame
from golf_db.game_greenie import GreenieGame
#from golf_db.game_factory import GolfGa7meFactory
from golf_db.exceptions import GolfException


class GolfGameGreenieTest(unittest.TestCase):
  @classmethod
  def setUpClass(cls):
    cls.db = GolfDBAdmin(database='golf_game_test')
    cls.db.create()
    
  def setUp(self):
    course_name = 'Canyon Lakes'
    tee_name = 'Blue'
    date_of_round = datetime.datetime(2017, 3, 23)
    lstPlayers = ['sjournea', 'snake']
    
    self.gr = GolfRound()
    self.gr.course = self.db.courseFind(course_name, dbclass=GolfCourse)[0]
    self.gr.date = date_of_round
    for email in lstPlayers:
      pl = self.db.playerFind(email, dbclass=GolfPlayer)[0]
      self.gr.addPlayer(pl, tee_name)

  def test_game_init(self):
    g = GreenieGame(self.gr, self.gr.scores)
    self.assertEquals(g._carry_over, True)
    self.assertEquals(g._double_birdie, True)
    self.assertEquals(g._last_par_3_carry, True)
    self.assertIsNone(g._wager)
    self.assertIsNone(g.total_payout)

    g = GreenieGame(self.gr, self.gr.scores, carry_over=False, double_birdie=False, last_par_3_carry=False)
    self.assertEquals(g._carry_over, False)
    self.assertEquals(g._double_birdie, False)
    self.assertEquals(g._last_par_3_carry, False)
    self.assertIsNone(g._wager)
    self.assertIsNone(g.total_payout)
    
  def test_game_wager(self):
    with self.assertRaises(GolfException):
      g = GreenieGame(self.gr, self.gr.scores, wager=0.0)
    
    with self.assertRaises(GolfException):
      g = GreenieGame(self.gr, self.gr.scores, wager=-45.0)
 
    g = GreenieGame(self.gr, self.gr.scores, wager=1.0)
    self.assertEqual(g._wager, 1.0)
    self.assertEqual(g.total_payout,1*2*5)
    
  def test_game_start(self):
    g = GreenieGame(self.gr, self.gr.scores)
    g.start()
    for pl in g.scores:
      self.assertEquals(pl.dct_points['holes'], 18*[None])
      self.assertEquals(pl.dct_points['in'], 0)
      self.assertEquals(pl.dct_points['out'], 0)
      self.assertEquals(pl.dct_points['total'], 0)
      self.assertIsNone(pl.dct_money)
    self.assertEquals(g._carry, 0)
    self.assertEquals(g._next_hole, 0)
    self.assertEquals(g._use_green_in_regulation, False)
    self.assertIn('header', g.dctScorecard)
    
    g = GreenieGame(self.gr, self.gr.scores, wager=1.0)
    g.start()
    for pl in g.scores:
      self.assertEquals(pl.dct_money['holes'], 18*[None])
      self.assertEquals(pl.dct_money['in'], 0.0)
      self.assertEquals(pl.dct_money['out'], 0.0)
      self.assertEquals(pl.dct_money['total'], 0.0)
    self.assertIn('header', g.dctScorecard)

  def test_game_add_score(self):
    g = GreenieGame(self.gr, self.gr.scores)
    g.start()
    g.setGrossScore(0, [4,4], options={'putts':[1,1]})
    g.setGrossScore(1, [5,5], options={'putts':[1,1]})
    g.setGrossScore(2, [3,3], {'putts':[1,1], 'closest_to_pin':0})
    self.assertEqual(g.scores[0].dct_points['holes'][2], 1)
    self.assertEqual(g.scores[0].dct_points['out'], 1)
    self.assertEqual(g.scores[0].dct_points['in'], 0)
    self.assertEqual(g.scores[0].dct_points['total'], 1)
    g.setGrossScore(3, [4,4], options={'putts':[1,1]})
    g.setGrossScore(4, [3,3], options={'putts':[1,1], 'closest_to_pin':0})
    self.assertEqual(g.scores[0].dct_points['holes'][4], 1)
    self.assertEqual(g.scores[0].dct_points['out'], 2)
    self.assertEqual(g.scores[0].dct_points['in'], 0)
    self.assertEqual(g.scores[0].dct_points['total'], 2)
    
    g = GreenieGame(self.gr, self.gr.scores, wager=1.0)
    g.start()
    g.setGrossScore(0, [4,4], options={'putts':[1,1]})
    g.setGrossScore(1, [5,5], options={'putts':[1,1]})
    g.setGrossScore(2, [3,3], {'putts':[1,1], 'closest_to_pin':0})
    self.assertEqual(g.scores[0].dct_money['holes'][2], 2.0)
    self.assertEqual(g.scores[0].dct_money['out'], 2.0)
    self.assertEqual(g.scores[0].dct_money['in'], 0)
    self.assertEqual(g.scores[0].dct_money['total'], 2)
    g.setGrossScore(3, [4,4], options={'putts':[1,1]})
    g.setGrossScore(4, [3,3], options={'putts':[1,1], 'closest_to_pin':0})
    self.assertEqual(g.scores[0].dct_money['holes'][4], 2.0)
    self.assertEqual(g.scores[0].dct_money['out'], 4.0)
    self.assertEqual(g.scores[0].dct_money['in'], 0)
    self.assertEqual(g.scores[0].dct_money['total'], 4)

  def test_game_scorecard(self):
    g = GreenieGame(self.gr, self.gr.scores)
    g.start()
    for index in range(18):
      g.setGrossScore(1, [4,4], options={'putts':[1,1]})
      dct = g.getScorecard()
      self.assertIn('header', dct)
      self.assertIn('players', dct)

  def test_game_leaderboard(self):
    g = GreenieGame(self.gr, self.gr.scores)
    g.start()
    for index in range(18):
      g.setGrossScore(1, [4,4], options={'putts':[1,1]})
      dct = g.getLeaderboard()
      self.assertIn('hdr', dct)
      self.assertIn('leaderboard', dct)

  def test_game_status(self):
    g = GreenieGame(self.gr, self.gr.scores)
    g.start()
    dct = g.getStatus()
    self.assertIn('line', dct)
    self.assertIn('next_hole', dct)
    self.assertEqual(dct['next_hole'], 1)
    for index in range(18):
      g.setGrossScore(1, [4,4], options={'putts':[1,1]})
      dct = g.getStatus()
      self.assertIn('line', dct)
      self.assertIn('next_hole', dct)
      if index < 17:
        self.assertEqual(dct['next_hole'], index+2)
      else:
        self.assertIsNone(dct['next_hole'])
