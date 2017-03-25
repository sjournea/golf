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
    return {'player': self.player.toDict(),
            'gross':self.gross,
            'net': self.net,
            'course_handicap': self.course_handicap,
          }
  
  def fromDict(self, dct):
    self.player.fromDict(dct['player'])
    self.gross = dct.get('gross', [])
    self.net = dct.get('net', [])
    self.course_handicap = dct.get('course_handicap', 0)
    
  def calcCourseHandicap(self, slope):
    """Course Handicap = Handicap Index * Slope rating / 113."""
    self.course_handicap = round(self.player.handicap * slope / 113)

  def __eq__(self, other):
    return (self.player == other.player and
            self.gross == other.gross and
            self.net == other.net and
            self.course_handicap == other.course_handicap)

  def __ne__(self, other):
    return not self == other

  def __str__(self):
    return '{} - course_handicap:{} gross:{} net:{}'.format(
      self.player.nick_name, self.course_handicap, self.gross, self.net)
  
  def __repr__(self):
    return 'GolfScore(dct={})'.format(self.toDict())

