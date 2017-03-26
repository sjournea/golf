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
    course_name = 'Canyon Lakes'
    tee_name = 'Blue'
    date_of_round = datetime.datetime(2017, 3, 23)
    lstPlayers = ['sjournea', 'snake']
    
    r = GolfRound()
    r.course = self.db.courseFind(course_name)
    r.date = date_of_round
    for email in lstPlayers:
      pl = self.db.playerFind('sjournea')
      r.addPlayer(pl, tee_name)
      
    r.start()
    
    r.addScores(1, [4,4])
    dct = r.getScorecard()
    #for key,value in dct.items():
      #print '{:<15} - {}'.format(key, value)