import unittest
import datetime

from golf_db.round import GolfRound
from golf_db.test_data import GolfRounds,GolfCourses, GolfPlayers
from golf_db.db import GolfDB

class GolfRoundTest(unittest.TestCase):

  def test_init_empty(self):
    # check default parameters
    r = GolfRound()
    self.assertIsNone(r.course)
    self.assertIsNone(r.date)
    self.assertEqual(r.scores, [])

  def test_init_from_dict(self):
    for dct in GolfRounds:
      r = GolfRound(dct=dct)
      r2 = GolfRound()
      r2.fromDict(dct)
      self.assertEqual(r, r2)
      
class PlayRoundTest(unittest.TestCase):
  def setUp(self):
    self.db = GolfDB(database='golf_round_test')
    self.db.create()
    
  def test_play(self):
    # check default parameters
    r = GolfRound()
    r.course = self.db.courseFind('Canyon Lakes')
    r.date = datetime.datetime(2017, 3, 23)
    tee = r.course.getTee('Blue')
    pl1 = self.db.playerFind('sjournea')
    r.addPlayer(pl1, tee)
    pl2 = self.db.playerFind('snake')
    r.addPlayer(pl2, tee)
    #print r
    dct = r.getScorecard()
    #for key,value in dct.items():
      #print '{:<15} - {}'.format(key, value)