import unittest

from golf_db.score import GolfScore
from golf_db.test_data import CanyonLake_Players

class GolfScoreTest(unittest.TestCase):

  def test_init_empty(self):
    # check default parameters
    score = GolfScore()
    self.assertIsNone(score.player.nick_name)
    self.assertEqual(score.gross, [])

  def test_init_from_dict(self):
    for dct in CanyonLake_Players:
      score = GolfScore(dct=dct)
      self.assertEqual(dct['player'], score.player.toDict())
      self.assertEqual(dct['gross'], score.gross)
      
  def test_calc_handicap(self):
    for dct in CanyonLake_Players:
      score = GolfScore(dct=dct)
      score.calcCourseHandicap(133)
