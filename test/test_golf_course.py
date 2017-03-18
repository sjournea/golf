import unittest

from golf_db.course import GolfCourse
from golf_db.test_data import GolfCourses, GolfPlayers, CanyonLake_Players

class GolfCourseInitCase(unittest.TestCase):
  lstDicts = [
    {'name': 'Canyon Lakes', 'holes':[], 'tees':[]},
    {'name': 'Santa Clara', 'holes':[], 'tees':[]},
    {'name': 'Diablo Grande', 'holes':[], 'tees':[]},
  ]

  def test_init_empty(self):
    # check default parameters
    course = GolfCourse()
    self.assertIsNone(course.name)
    self.assertEqual(course.holes, [])
    self.assertEqual(course.tees, [])

  def test_init_from_dict(self):
    for dct in self.lstDicts:
      course = GolfCourse(dct=dct)
      self.assertEqual(dct['name'], course.name)
      self.assertEqual(dct['holes'], course.holes)
      self.assertEqual(dct['tees'], course.tees)
      
class GolfCourseDictCase(unittest.TestCase):
  def test_toDict(self):
    self.maxDiff = None
    # check course name
    for dct in GolfCourses:
      course = GolfCourse(dct=dct) 
      self.assertEqual(course.toDict(), dct)
    
  def test_fromDict(self):
    for dct in GolfCourses:
      course = GolfCourse()
      course.fromDict(dct)
      self.assertEqual(course.toDict(), dct)

  def test_equalOperator(self):
    for dct in GolfCourses:
      course = GolfCourse(dct=dct)
      course2 = GolfCourse(dct=course.toDict())
      self.assertEqual(course, course2)
      course2.holes[0].par += 1
      self.assertNotEqual(course, course2)

