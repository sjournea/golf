import unittest

from golf_db.round import GolfRound
from golf_db.test_data import GolfRounds

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
      
