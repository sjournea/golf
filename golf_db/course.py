"""course.py - simple golf course class."""

class DB(object):
  def __init__(self):
    super(DB, self).__init__()
    
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
    """Load from a dictionary."""
    self.par = dct.get('par')
    self.handicap = dct.get('handicap')
  
  def toDict(self):
    """Return a dictionary of all values."""
    return { 'par': self.par, 'handicap': self.handicap }

  def __eq__(self, other):
    return (self.par == other.par and
            self.handicap == other.handicap)

  def __ne__(self,other):
    return not self == other

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
    self.name = course_dct.get('name')
    self.holes = [GolfHole(dct) for dct in course_dct['holes']]
  
  def toDict(self):
    return { 'name': self.name,
             'holes': [hole.toDict() for hole in self.holes] }
  
  def __eq__(self, other):
    return (self.name == other.name and
            self.holes == other.holes)

  def __ne__(self, other):
    return not self == other

  def __str__(self):
    return '{} - {} holes'.format(self.name, len(self.holes))
  
  def __repr__(self):
    return 'GolfCourse(dct={})'.format(self.toDict())
  

class GolfPlayer(object):
  """Golf player
  
  Members:
    first_name - string
    last_name  - string
    nick_name  - string
    handicap   - float
  """
  def __init__(self, dct=None):
    super(GolfPlayer, self).__init__()
    self.first_name = None
    self.last_name = None
    self.nick_name = None
    self.handicap = None
    if dct:
      self.fromDict(dct)
   
  def fromDict(self, dct):
    """Load from a dictionary."""
    self.first_name = dct.get('first_name')
    self.last_name = dct.get('last_name')
    self.nick_name = dct.get('nick_name')
    self.handicap = dct.get('handicap')
    
  def toDict(self):
    """Return a dictionary of all values."""
    return { 'first_name': self.first_name,
             'last_name': self.last_name,
             'nick_name': self.nick_name,
             'handicap': self.handicap,
             }

  def __eq__(self, other):
    return (self.first_name == other.first_name and
            self.last_name == other.last_name and
            self.nick_name == other.nick_name and
            self.handicap == other.handicap)

  def __ne__(self,other):
    return not self == other

  def __str__(self):
    return '{} {} ({}) handicap {}'.format(self._id, self.first_name, self.last_name, self.nick_name, self.handicap)
  
  def __repr__(self):
    return 'GolfPlayer(dct={})'.format(self.toDict())

