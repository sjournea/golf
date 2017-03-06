"""course.py - simple golf course class."""

class GolfHole(object):
  """Golf hole
  
  Members:
    par      - Int - Usually 3, 4, or 5.
    handicap - Int - 1 to 18.
  """
  def __init__(self, dct=None):
    super(GolfHole, self).__init__()
    self.par = None
    self.handicap = None
    if dct:
      self.fromDict(dct)
   
  def fromDict(self, dct):
    self.par = dct['par']
    self.handicap = dct['handicap']
  
  def toDict(self):
    return { 'par': self.par, 'handicap': self.handicap }

  def __str__(self):
    return 'par {} handicap {}'.format(self.par, self.handicap)
  
  def __repr__(self):
    return 'GolfHole(dct={})'.format(self.toDict())
  
class GolfCourse(object):
  """Golf course object
  
  Members:
    name  - String - Golf course name
    holes - list of golf holes
  """
  def __init__(self, dct=None):
    super(GolfCourse, self).__init__()
    self.name = None
    self.holes = None
    if dct:
      self.fromDict(dct)
   
  def fromDict(self, course_dct):
    self.name = course_dct['name']
    self.holes = [GolfHole(dct) for dct in course_dct['holes']]
  
  def toDict(self):
    return { 'name': self.name,
             'holes': [hole.toDict() for hole in self.holes] }
  
  def __str__(self):
    return '{} - {} holes'.format(self.name, len(self.holes))
  
  def __repr__(self):
    return 'GolfCourse(dct={})'.format(self.toDict())