"""course.py - simple golf course class."""

class DB(object):
  """Abstract - fields MUST be defined."""
  def __init__(self, dct=None):
    super(DB, self).__init__()
    # Add _id field
    self.fields.append('_id')

  def put(self, collection):
    collection.save(self.toDict(), safe=True)


class Doc(object):
  """Abstract fields MUST be defined."""
  def __init__(self, dct=None):
    super(Doc, self).__init__()
    # initiaze all fields to None
    for field in self.fields:
      setattr(self, field, None)
    # initialize from dictionary
    if dct:
      self.fromDict(dct)
  
  def fromDict(self, dct):
    for field in self.fields:
      setattr(self, field, dct.get(field))
  
  def toDict(self):
    dct = {}
    for field in self.fields:
      dct[field] = getattr(self, field)
    return dct
    
  def __eq__(self, other):
    for field in self.fields:
      if getattr(self, field) != getattr(other, field):
        return False
    return True

  def __ne__(self,other):
    return not self == other


class GolfHole(Doc):
  """Golf hole
  
  Members:
    par      - Int - Usually 3, 4, or 5.
    handicap - Int - 1 to 18.
  """
  fields = ['par', 'handicap']
  def __init__(self, dct=None):
    super(GolfHole, self).__init__(dct)

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
  
  def setStats(self):
    self.out_tot = sum([hole.par for hole in self.holes[:9]])
    self.in_tot  = sum([hole.par for hole in self.holes[9:]])
    self.total   = self.in_tot + self.out_tot

  def toDict(self):
    return { 'name': self.name,
             'holes': [hole.toDict() for hole in self.holes] }
  
  def __eq__(self, other):
    return (self.name == other.name and
            self.holes == other.holes)

  def __ne__(self, other):
    return not self == other

  def getScorecard(self):
    """
    <Name>    
          1  2  3  4  5  6  7  8  9 Out  10 11 12 13 14 15 16 17 18 In Total
    Par
    Hdcp 
    """
    self.setStats()
    hdr  = 'Hole  '
    par  = 'Par   '
    hdcp = 'Hdcp  '
    for n,hole in enumerate(self.holes[:9]):
      hdr += ' {:>2}'.format(n+1)
      par += ' {:>2}'.format(hole.par)
      hdcp += ' {:>2}'.format(hole.handicap)
    hdr += ' Out '
    par += ' {:>3} '.format(self.out_tot)
    hdcp += '     '
    for n,hole in enumerate(self.holes[9:]):
      hdr += '{:>2} '.format(n+10)
      par += '{:>2} '.format(hole.par)
      hdcp += '{:>2} '.format(hole.handicap)
    hdr += ' In Tot'
    par += ' {:>2} {:>3}'.format(self.in_tot, self.total)
    return [self.name, hdr, par, hdcp]
      
  def __str__(self):
    return '{} - {} holes'.format(self.name, len(self.holes))
  
  def __repr__(self):
    return 'GolfCourse(dct={})'.format(self.toDict())
  

class GolfPlayer(Doc, DB):
  """Golf player
  
  Members:
    first_name - string
    last_name  - string
    nick_name  - string
    handicap   - float
  """
  fields = ['first_name',
            'last_name',
            'nick_name',
            'handicap']
  def __init__(self, dct=None):
    super(GolfPlayer, self).__init__(dct=dct)

  def __str__(self):
    return '{} {} ({}) handicap {}'.format(self.first_name, self.last_name, self.nick_name, self.handicap)
  
  def __repr__(self):
    return 'GolfPlayer(dct={})'.format(self.toDict())

