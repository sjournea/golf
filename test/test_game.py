import unittest
import datetime

from golf_db.round import GolfRound
from golf_db.test_data import GolfRounds,GolfCourses, GolfPlayers
from golf_db.db import GolfDB
from golf_db.game import GolfGame
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


