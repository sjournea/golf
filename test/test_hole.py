import unittest

from golf_db.hole import GolfHole
from golf_db.doc import DocValidateFail

class GolfHoleTest(unittest.TestCase):
  lst_legal_golf_holes = [
    {'par':3, 'handicap': 1},
    {'par':4, 'handicap': 18},
    {'par':5, 'handicap': 2},
    {'par':6, 'handicap': 9},
  ]
  def test_init_keywords(self):
    for dct in self.lst_legal_golf_holes:
      g = GolfHole(par=dct['par'], handicap=dct['handicap'])
      self.assertEqual(g.par, dct['par'])
      self.assertEqual(g.handicap, dct['handicap'])

  def test_init_dct(self):
    for dct in self.lst_legal_golf_holes:
      g = GolfHole(dct=dct)
      self.assertEqual(g.par, dct['par'])
      self.assertEqual(g.handicap, dct['handicap'])

class GolfHoleValidateTest(unittest.TestCase):
  def test_init(self):
    g = GolfHole()
    with self.assertRaises(DocValidateFail):
      g.validate()

  def test_init_good_values(self):
    for par in [3,4,5,6]:
      g = GolfHole(par=par, handicap=1)
      g.validate()
    for handicap in [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18]:
      g = GolfHole(par=5, handicap=handicap)
      g.validate()

  def test_init_bad_values(self):
    for par in [1,2,7,100]:
      g = GolfHole(par=par, handicap=1)
      with self.assertRaises(DocValidateFail):
        g.validate()
    for handicap in [0, -1, 25, 19, 101]:
      g = GolfHole(par=5, handicap=handicap)
      with self.assertRaises(DocValidateFail):
        g.validate()
