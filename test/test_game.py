import unittest
import datetime

from golf_db.round import GolfRound
from golf_db.course import GolfCourse
from golf_db.player import GolfPlayer
from golf_db.db import GolfDBAdmin
from golf_db.game import GolfGame
#from golf_db.exceptions import GolfException

class GolfGameTest(unittest.TestCase):
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
      
  def test_base_abstract(self):
    with self.assertRaises(TypeError):
      g = GolfGame(self.gr, self.gr.scores)
    


