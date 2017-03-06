import unittest

from golf_db.course import GolfCourse, GolfHole

from util.tl_logger import TLLog
log = TLLog.getLogger('mongo')

class GolfCourseInitCase(unittest.TestCase):
  lstDicts = [
    {'name': 'Canyon Lakes', 'holes':[]},
    {'name': 'Santa Clara', 'holes':[]},
    {'name': 'Diablo Grande', 'holes':[]},
  ]

  def test_init_empty(self):
    # check default parameters
    course = GolfCourse()
    self.assertIsNone(course.name)
    self.assertIsNone(course.holes)

  def test_init_from_dict(self):
    for dct in self.lstDicts:
      course = GolfCourse(dct=dct)
      self.assertEqual(dct['name'], course.name)
      self.assertEqual(dct['holes'], course.holes)
      
class GolfCourseDictCase(unittest.TestCase):
  canyon_lakes_mens_holes = [
    {'par': 4, 'handicap': 17},
    {'par': 5, 'handicap':  9},
    {'par': 3, 'handicap':  5},
    {'par': 4, 'handicap': 11},
    {'par': 3, 'handicap': 15},
    {'par': 4, 'handicap': 13},
    {'par': 5, 'handicap':  7},
    {'par': 4, 'handicap':  1},
    {'par': 4, 'handicap':  3},

    {'par': 3, 'handicap':  8},
    {'par': 4, 'handicap': 14},
    {'par': 4, 'handicap': 12},
    {'par': 3, 'handicap': 16},
    {'par': 5, 'handicap':  4},
    {'par': 3, 'handicap': 10},
    {'par': 4, 'handicap': 18},
    {'par': 5, 'handicap':  2},
    {'par': 4, 'handicap':  6},
  ]
  sj_muni_holes = [
    {'par': 5, 'handicap': 15},
    {'par': 4, 'handicap':  1},
    {'par': 4, 'handicap':  5},
    {'par': 3, 'handicap': 17},
    {'par': 4, 'handicap': 11},
    {'par': 4, 'handicap':  7},
    {'par': 3, 'handicap':  9},
    {'par': 4, 'handicap':  3},
    {'par': 5, 'handicap': 13},

    {'par': 4, 'handicap': 12},
    {'par': 5, 'handicap':  4},
    {'par': 3, 'handicap': 18},
    {'par': 4, 'handicap':  6},
    {'par': 4, 'handicap': 16},
    {'par': 4, 'handicap':  2},
    {'par': 4, 'handicap':  8},
    {'par': 3, 'handicap': 10},
    {'par': 5, 'handicap': 14},
  ]    
  diablo_grande_men_holes = [
    {'par': 4, 'handicap': 15},
    {'par': 4, 'handicap':  9},
    {'par': 4, 'handicap':  3},
    {'par': 3, 'handicap': 11},
    {'par': 5, 'handicap':  7},
    {'par': 4, 'handicap': 13},
    {'par': 3, 'handicap':  5},
    {'par': 4, 'handicap':  1},
    {'par': 5, 'handicap': 17},

    {'par': 4, 'handicap':  8},
    {'par': 3, 'handicap': 14},
    {'par': 5, 'handicap':  4},
    {'par': 4, 'handicap': 16},
    {'par': 4, 'handicap':  2},
    {'par': 4, 'handicap':  6},
    {'par': 5, 'handicap': 12},
    {'par': 3, 'handicap': 18},
    {'par': 4, 'handicap': 10},
  ]    
  poppy_hills_men_holes = [
    {'par': 4, 'handicap':  7},
    {'par': 3, 'handicap': 15},
    {'par': 4, 'handicap':  9},
    {'par': 5, 'handicap':  3},
    {'par': 4, 'handicap':  1},
    {'par': 3, 'handicap': 17},
    {'par': 4, 'handicap': 13},
    {'par': 4, 'handicap': 11},
    {'par': 5, 'handicap':  5},

    {'par': 5, 'handicap':  8},
    {'par': 3, 'handicap': 18},
    {'par': 4, 'handicap':  4},
    {'par': 4, 'handicap': 10},
    {'par': 4, 'handicap': 12},
    {'par': 3, 'handicap': 14},
    {'par': 4, 'handicap':  2},
    {'par': 3, 'handicap': 16},
    {'par': 5, 'handicap':  6},
  ]    
  lstDicts = [
    {'name': 'Canyon Lakes', 'holes': canyon_lakes_mens_holes},
    {'name': 'Santa Jose Muni', 'holes':sj_muni_holes},
    {'name': 'Diablo Grande', 'holes':diablo_grande_men_holes},
    {'name': 'Poppy Hills', 'holes':poppy_hills_men_holes},
  ]
  def test_toDict(self):
    # check course name
    for dct in self.lstDicts:
      course = GolfCourse(dct=dct) 
      self.assertEqual(course.toDict(), dct)
    
  def test_fromDict(self):
    # check course name
    for dct in self.lstDicts:
      course = GolfCourse()
      course.fromDict(dct)
      self.assertEqual(course.toDict(), dct)

class GolfCourseHoleCase(unittest.TestCase):
  lstDicts = [
    {'par': 5, 'handicap': 1},
    {'par': 4, 'handicap': 10},
    {'par': 3, 'handicap': 18},
  ]

  def test_init_empty(self):
    # check default parameters
    hole = GolfHole()
    self.assertIsNone(hole.par)
    self.assertIsNone(hole.handicap)

  def test_init_from_dict(self):
    for dct in self.lstDicts:
      hole = GolfHole(dct=dct)
      self.assertEqual(dct['par'], hole.par)
      self.assertEqual(dct['handicap'], hole.handicap)
      
class GolfHoleDictCase(unittest.TestCase):
  lstDicts = [
    {'par': 5, 'handicap': 1},
    {'par': 4, 'handicap': 10},
    {'par': 3, 'handicap': 18},
  ]
  def test_toDict(self):
    # check course name
    for dct in self.lstDicts:
      hole = GolfHole(dct=dct) 
      self.assertEqual(hole.toDict(), dct)
    
  def test_fromDict(self):
    # check course name
    for dct in self.lstDicts:
      hole = GolfHole() 
      hole.fromDict(dct)
      self.assertEqual(hole.toDict(), dct)

