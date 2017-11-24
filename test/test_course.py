import unittest

from golf_db.course import GolfCourse
from golf_db.hole import GolfHole
from golf_db.test_data import GolfCourses
from golf_db.db import GolfDBAdmin
from golf_db.exceptions import GolfException,DocValidateFail

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
    db = GolfDBAdmin(database='golf_test')
    db.create()
    lst = db.courseFind('Lake Chabot', dbclass=GolfCourse)
    self.assertEqual(len(lst), 1)
    course = lst[0]
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
    
  def test_calcBumps(self):
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
    # build handicap list
    handicap_index = []
    for num in xrange(1, 19, 1):
      for n,dct in enumerate(fall_river_men_holes):
        hdcp = dct['handicap']
        if num == hdcp:
          handicap_index.append(n)
          break
    #print handicap_index
    
    course = GolfCourse()
    course.holes = [GolfHole(dct=dct) for dct in fall_river_men_holes]
    expected_bumps = 18*[0]
    for handicap in xrange(38):
      bumps = course.calcBumps(handicap)
      #print '    bumps:{}'.format(bumps)
      #print 'exp_bumps:{}'.format(expected_bumps)
      self.assertListEqual(bumps, expected_bumps, 'handicap == {} fail'.format(handicap))
      expected_bumps[handicap_index[handicap % 18]] += 1
    
  def test_calcESC(self):
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
    # build handicap list
    course_handicaps = [n for n in range(45)]
    gross_scores = [n for n in range(2, 15)]

    course = GolfCourse()
    course.holes = [GolfHole(dct=dct) for dct in fall_river_men_holes]
    for index,hole in enumerate(course.holes):
      for course_handicap in course_handicaps:
        for gross in gross_scores:
          esc = course.calcESC(index, gross, course_handicap)
          if course_handicap < 10:
            exp_esc = gross if gross < hole.par+2 else hole.par+2
          elif course_handicap < 20:
            exp_esc = gross if gross < 7 else 7
          elif course_handicap < 30:
            exp_esc = gross if gross < 8 else 8
          elif course_handicap < 40:
            exp_esc = gross if gross < 9 else 9
          else: # course_handicap >= 40
            exp_esc = gross if gross < 10 else 10
          self.assertEqual(esc, exp_esc, 'hdcp:{} hole:{} par:{} gross:{} esc:{} exp_esc:{}'.format(
              course_handicap, index+1, hole.par, gross, esc, exp_esc))
            
  def test_getScorecard(self):
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
    course.holes = [GolfHole(dct=dct) for dct in fall_river_men_holes]
    
    dct = course.getScorecard()
    self.assertEqual(len(dct), 3)
    for key in ['hdr', 'par', 'hdcp']:
      self.assertIn(key, dct)
    self.assertNotIn('ESC', dct['hdr'])
      
    dct = course.getScorecard(ESC=1)
    self.assertEqual(len(dct), 3)
    for key in ['hdr', 'par', 'hdcp']:
      self.assertIn(key, dct)
    self.assertIn('ESC', dct['hdr'])
