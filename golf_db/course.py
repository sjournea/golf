"""course.py - simple golf course class."""
from .doc import Doc

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
   
  def setStats(self):
    self.out_tot = sum([hole.par for hole in self.holes[:9]])
    self.in_tot  = sum([hole.par for hole in self.holes[9:]])
    self.total   = self.in_tot + self.out_tot

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
    return { 'hdr': hdr,
             'par': par,
             'hdcp': hdcp,
           }
      
  def __str__(self):
    return '{} - {} holes'.format(self.name, len(self.holes))
  
  def __repr__(self):
    return 'GolfCourse(dct={})'.format(self.toDict())
  

class GolfPlayer(Doc):
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


class GolfScore(object):
  """Golf Score for a player."""
  def __init__(self, dct=None):
    super(GolfScore, self).__init__()
    self.player = GolfPlayer()
    self.gross = []
    if dct:
      self.fromDict(dct)
      
  def toDict(self):
    dct['player'] = self.player.toDict()
    dct['gross'] = self.gross
    return dct
  
  def fromDict(self, dct):
    self.player.fromDict(dct['player'])
    self.gross = dct.get('gross', [])
    
  def __str__(self):
    return '{} - gross:{}'.format(self.player.nick_name, self.gross)
  
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
        gross_line += ' {:>2}'.format(gross)
        gross_out += gross
      gross_line += ' {:>3}'.format(gross_out)
      for gross in score.gross[9:]:
        gross_line += ' {:>2}'.format(gross)
        gross_in += gross
      gross_tot = gross_out + gross_in
      gross_line += ' {:>3} {:>3}'.format(gross_in, gross_tot)
      dct['gross_line'] = gross_line
      dct['gross_in'] = gross_in
      dct['gross_out'] = gross_out
      dct['gross_tot'] = gross_tot
      dct_scorecard['player_%d' % n] = dct
      
    return dct_scorecard
  
  def __str__(self):
    for pl in self.scores:
      print pl.player
    return '{} - {} - {}'.format(self.date.date(), self.course.name, ','.join([score.player.nick_name for score in self.scores]))
  
    