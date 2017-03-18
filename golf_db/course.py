from .doc import Doc
from .hole import GolfHole
from .player import GolfPlayer
from .score import GolfScore

class GolfCourse(object):
  """Golf course object
  
  Members:
    name  - String - Golf course name
    holes - list of golf holes
  """
  def __init__(self, dct=None):
    super(GolfCourse, self).__init__()
    self.name = None
    self.holes = []
    self.tees = []
    if dct:
      self.fromDict(dct)
   
  def setStats(self):
    self.out_tot = sum([hole.par for hole in self.holes[:9]])
    self.in_tot  = sum([hole.par for hole in self.holes[9:]])
    self.total   = self.in_tot + self.out_tot

  def fromDict(self, dct):
    self.name = dct.get('name')
    self.holes = dct.get('holes', [])
    if self.holes:
      self.holes = [GolfHole(dct=hole_dct) for hole_dct in dct['holes']]
    self.tees = dct.get('tees', [])
  
  def toDict(self):
    return { 'name': self.name,
             'holes': [hole.toDict() for hole in self.holes],
             'tees': self.tees, }
  
  def __eq__(self, other):
    return (self.name == other.name and
            self.holes == other.holes and
            self.tees == other.tees
           )

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
      hdr += ' {:>3}'.format(n+1)
      par += ' {:>3}'.format(hole.par)
      hdcp += ' {:>3}'.format(hole.handicap)
    hdr += '  Out '
    par += ' {:>4} '.format(self.out_tot)
    hdcp += '      '
    for n,hole in enumerate(self.holes[9:]):
      hdr += '{:>3} '.format(n+10)
      par += '{:>3} '.format(hole.par)
      hdcp += '{:>3} '.format(hole.handicap)
    hdr += '  In  Tot'
    par += '{:>4} {:>4}'.format(self.in_tot, self.total)
    return { 'hdr': hdr,
             'par': par,
             'hdcp': hdcp,
           }
      
  def __str__(self):
    return '{:<20} - {} holes - {} tees'.format(self.name, len(self.holes), len(
      self.tees))
  
  def __repr__(self):
    return 'GolfCourse(dct={})'.format(self.toDict())
  

  
    