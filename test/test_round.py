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
    self.assertIsNone(r.tee)

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
    r.tee = r.course.getTee('Blue')
    #print r
    lst = self.db.playerList()
    #for pl in lst:
      #print pl
    #pl = self.db.playerFind('sjourea')
    #print pl
    r.addPlayer(lst[0])
    r.addPlayer(lst[1])
    #print r
    dct = r.getScorecard()
    #for key,value in dct.items():
      #print '{:<15} - {}'.format(key, value)