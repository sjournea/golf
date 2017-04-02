import unittest

from golf_db.score import GolfScore
from golf_db.player import GolfPlayer
from golf_db.test_data import CanyonLake_Players

class GolfScoreTest(unittest.TestCase):

  def test_init_empty(self):
    # check default parameters
    score = GolfScore()
    self.assertIsInstance(score.player, GolfPlayer)
    self.assertEqual(score.tee, None)
    self.assertEqual(score.course_handicap, 0)

  def test_init_from_dict(self):
    for dct in CanyonLake_Players:
      score = GolfScore(dct=dct)
      self.assertEqual(dct['player'], score.player.toDict())
      
  def test_calc_handicap(self):
    for dct in CanyonLake_Players:
      score = GolfScore(dct=dct)
      score.calcCourseHandicap()
