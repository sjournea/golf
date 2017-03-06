import unittest

from golf_db.course import GolfCourse, GolfHole
from golf_db.test_data import GolfCourseTestData
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
  def test_toDict(self):
    # check course name
    for dct in GolfCourseTestData:
      course = GolfCourse(dct=dct) 
      self.assertEqual(course.toDict(), dct)
    
  def test_fromDict(self):
    for dct in GolfCourseTestData:
      course = GolfCourse()
      course.fromDict(dct)
      self.assertEqual(course.toDict(), dct)

  def test_equalOperator(self):
    for dct in GolfCourseTestData:
      course = GolfCourse(dct=dct)
      course2 = GolfCourse(dct=course.toDict())
      self.assertEqual(course, course2)
      course2.holes[0].par += 1
      self.assertNotEqual(course, course2)

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

  def test_equalOperator(self):
    for dct in self.lstDicts:
      hole1 = GolfHole(dct=dct) 
      hole2 = GolfHole(dct=hole1.toDict()) 
      self.assertEqual(hole1, hole2)
      hole2.par += 1 
      self.assertNotEqual(hole1, hole2)

