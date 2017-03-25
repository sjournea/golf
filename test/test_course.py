import unittest

from golf_db.course import GolfCourse
from golf_db.hole import GolfHole
from golf_db.doc import DocValidateFail
from golf_db.test_data import GolfCourses
from golf_db.db import GolfDB
from golf_db.exceptions import GolfException

class GolfCourseTestCase(unittest.TestCase):
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
      
  def test_toDict(self):
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

  def test_validate_good_data(self):
    # check course name
    for dct in GolfCourses:
      course = GolfCourse(dct=dct)
      course.validate()

  def test_validate_fails(self):
    fall_river_men_holes = [
      {'par': 4, 'handicap':  15},
      {'par': 4, 'handicap':   5},
      {'par': 5, 'handicap':   1},
      {'par': 3, 'handicap':  13},
      {'par': 4, 'handicap':  17},
      {'par': 4, 'handicap':   3},
      {'par': 4, 'handicap':   7},
      {'par': 3, 'handicap':  11},
      {'par': 5, 'handicap':   9},
    
      {'par': 4, 'handicap':  12},
      {'par': 3, 'handicap':  14},
      {'par': 4, 'handicap':   8},
      {'par': 4, 'handicap':   6},
      {'par': 5, 'handicap':   2},
      {'par': 3, 'handicap':  16},
      {'par': 4, 'handicap':   4},
      {'par': 4, 'handicap':  18},
      {'par': 5, 'handicap':  10},
    ]
    
    course = GolfCourse()
    # validate fail, no holes
    with self.assertRaises(DocValidateFail):
      course.validate()
    # validate pass after adding holes
    course.holes = [GolfHole(dct=dct) for dct in fall_river_men_holes]
    course.validate()
    # force a bad handicap so validate fails
    old_handicap = course.holes[0].handicap
    course.holes[0].handicap = 10
    with self.assertRaises(DocValidateFail):
      course.validate()
    course.holes[0].handicap = old_handicap
    # force a bad par value so validate fails
    old_par = course.holes[0].par
    for bad_par in [0, 1, 2, 7, 8]:
      course.holes[0].par = bad_par
      with self.assertRaises(DocValidateFail):
        course.validate()
    course.holes[0].par = old_par
    
  def test_get_tee(self):
    # Find Lake Chabot 
    db = GolfDB(database='golf_test')
    db.create()
    course = db.courseFind('Lake Chabot')
    # test get tee by nme and gender, default gender is "mens"
    tee = course.getTee('Blue')
    self.assertDictEqual(tee, {'gender':'mens', 'name':'Blue', 'rating': 68.9, 'slope': 119})
    tee = course.getTee('Blue', gender='mens')
    self.assertDictEqual(tee, {'gender':'mens', 'name':'Blue', 'rating': 68.9, 'slope': 119})
    with self.assertRaises(GolfException):
      tee = course.getTee('Blue', gender='womens')
    tee = course.getTee('White')
    self.assertDictEqual(tee, {'gender':'mens', 'name':'White', 'rating': 67.4, 'slope': 116})
    with self.assertRaises(GolfException):
      tee = course.getTee('Red')
    tee = course.getTee('Red', gender='womens')
    self.assertDictEqual(tee, {'gender':'womens', 'name':'Red', 'rating': 70.1, 'slope': 116})
    
    
    
