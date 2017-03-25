from .doc import DocValidateFail
from .hole import GolfHole
from .exceptions import GolfException


class GolfCourse(object):
  """Golf course object
  
  Members:
    name  - String - Golf course name
    holes - list of golf holes
    tees  - list of tees on course
  """
  def __init__(self, dct=None):
    super(GolfCourse, self).__init__()
    self.name = None
    self.holes = []
    self.tees = []
    if dct:
      self.fromDict(dct)
   
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

  def validate(self):
    if len(self.holes) != 18:
      raise DocValidateFail('Course must have 18 golf holes.')
    handicaps = [0 for n in range(len(self.holes))]
    for hole in self.holes:
      hole.validate()
      handicaps[hole.handicap-1] += 1
    for n,hdcp in enumerate(handicaps):
      if hdcp == 0:
        raise DocValidateFail('Handicap {} has not been set.'.format(n+1))
      if hdcp > 1:
        raise DocValidateFail('Handicap {} been set more then once.'.format(n+1))
        
  def setStats(self):
    """Par totals."""
    self.out_tot = sum([hole.par for hole in self.holes[:9]])
    self.in_tot  = sum([hole.par for hole in self.holes[9:]])
    self.total   = self.in_tot + self.out_tot

  def getTee(self, name, gender='mens'):
    """Return the matching tee dictionary or None."""
    for dct in self.tees:
      if dct['name'] == name and dct['gender'] == gender:
        return dct
    else:
      raise GolfException('course getTee() fail - name:{} gender:{} not found'.format(name, gender)) 
  
  def getScorecard(self):
    """Return hdr, par and hdcp lines for scorecard."""
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
  

  
    