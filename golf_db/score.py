from .player import GolfPlayer

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

