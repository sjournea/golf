from .doc import Doc
from .hole import GolfHole
from .player import GolfPlayer

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
  

class GolfScore(object):
  """Golf Score for a player."""
  def __init__(self, dct=None):
    super(GolfScore, self).__init__()
    self.player = GolfPlayer()
    self.gross = []
    self.net = []
    self.course_handicap = 0
    if dct:
      self.fromDict(dct)
      
  def toDict(self):
    dct['player'] = self.player.toDict()
    dct['gross'] = self.gross
    dct['net'] = self.net
    dct['course_handicap'] = self.course_handicap
    return dct
  
  def fromDict(self, dct):
    self.player.fromDict(dct['player'])
    self.gross = dct.get('gross', [])
    self.net = dct.get('net', [])
    self.course_handicap = dct.get('course_handicap', 0)
    
  def calcCourseHandicap(self, slope):
    """Course Handicap = Handicap Index * Slope rating / 113."""
    self.course_handicap = round(self.player.handicap * slope / 113)

  def __str__(self):
    return '{} - course_handicap:{} gross:{} net:{}'.format(
      self.player.nick_name, self.course_handicap, self.gross, self.net)
  
  def __repr__(self):
    return 'GolfScore(dct={})'.format(self.toDict())

class GolfRound(object):
  def __init__(self, dct):
    super(GolfRound, self).__init__()
    self.course = None
    self.date = None
    self.scores = None
    if dct:
      self.fromDict(dct)

  def fromDict(self, dct):
    self.course = GolfCourse(dct['course'])
    self.date = dct.get('date')
    self.scores = [GolfScore(player_dct) for player_dct in dct['players']]
    
  def toDict(self):
    return { 'course': self.course.toDict(),
             'date': self.date,
             'scores': [player.toDict() for player in self.players],
           }
  
  def getScorecard(self):
    """Scorecard with all players."""
    dct_scorecard = self.course.getScorecard()
    for n,score in enumerate(self.scores):
      dct = {'player': score.player }
      gross_line = '{:<6}'.format(score.player.nick_name)
      gross_out = 0
      gross_in = 0
      for gross in score.gross[:9]:
        gross_line += ' {:>3}'.format(gross)
        gross_out += gross
      gross_line += ' {:>4}'.format(gross_out)
      for gross in score.gross[9:]:
        gross_line += ' {:>3}'.format(gross)
        gross_in += gross
      gross_tot = gross_out + gross_in
      gross_line += ' {:>4} {:>4}'.format(gross_in, gross_tot)
      dct['gross_line'] = gross_line
      dct['gross_in'] = gross_in
      dct['gross_out'] = gross_out
      dct['gross_tot'] = gross_tot
      dct_scorecard['player_%d_gross' % n] = dct
      
    return dct_scorecard
  
  def __str__(self):
    return '{} - {:<25} - {}'.format(self.date.date(), self.course.name, ','.join([score.player.nick_name for score in self.scores]))
  
    