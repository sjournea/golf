from .player import GolfPlayer

class GolfScore(object):
  """Golf Score for a player."""
  def __init__(self, dct=None):
    super(GolfScore, self).__init__()
    self.player = GolfPlayer()
    self.tee = None
    self.gross = {}
    self.net = {}
    self.course_handicap = 0
    self.games = {}
    if dct:
      self.fromDict(dct)
      
  def toDict(self):
    return {'player': self.player.toDict(),
            'gross':self.gross,
            'net': self.net,
            'tee': self.tee,
            'course_handicap': self.course_handicap,
            'games': self.games,
          }
  
  def fromDict(self, dct):
    self.player.fromDict(dct['player'])
    self.gross = dct.get('gross', {})
    self.net = dct.get('net', {})
    self.tee = dct.get('tee')
    self.course_handicap = dct.get('course_handicap', 0)
    self.games = dct.get('games', {})
    
  def __eq__(self, other):
    return (self.player == other.player and
            self.gross == other.gross and
            self.net == other.net and
            self.course_handicap == other.course_handicap and
            self.games == other.games and
            self.tee == other.tee)

  def __ne__(self, other):
    return not self == other

  def addGame(self, game):
    self.games[game] = {}
    
  def start(self, course, min_handicap):
    """Start a round initialization.
    
    Args:
      course: GolfCourse
      min_handicap: minumum handicap from all players.
    """
    # gross start
    self.gross['score'] = [0 for _ in range(len(course.holes))]
    self.gross['in'] = 0
    self.gross['out'] = 0
    self.gross['total'] = 0
    # net start
    self.net['score'] = [0 for _ in range(len(course.holes))]
    self.net['bump'] = course.calcBumps(self.course_handicap - min_handicap)
    self.net['in'] = 0
    self.net['out'] = 0
    self.net['total'] = 0
    # start all games
    for key, dct in self.games.items():
      if key == 'skins':
        dct['skin'] = [0 for _ in range(len(course.holes))]
        dct['in'] = 0
        dct['out'] = 0
        dct['total'] = 0
      
  def calcCourseHandicap(self):
    """Course Handicap = Handicap Index * Slope rating / 113."""
    self.course_handicap = int(round(self.player.handicap * self.tee['slope'] / 113))

  def updateGross(self, hole, gross):
    """Add a gross score."""
    index = hole - 1
    self.gross['score'][index] = gross
    self.gross['out'] = sum(self.gross['score'][:9])
    self.gross['in'] = sum(self.gross['score'][9:])
    self.gross['total'] = self.gross['in'] + self.gross['out']

    self.net['score'][index] = gross - self.net['bump'][index]
    self.net['out'] = sum(self.net['score'][:9])
    self.net['in'] = sum(self.net['score'][9:])
    self.net['total'] = self.net['in'] + self.net['out']

  def updateGames(self):
    for key, dct in self.games.items():
      if key == 'skins':
        dct['out'] = sum(dct['skin'][:9])
        dct['in'] = sum(dct['skin'][9:])
        dct['total'] = dct['in'] + dct['out']
    

  def __str__(self):
    return '{} - course_handicap:{} tee:{}' .format(
      self.player.nick_name, self.course_handicap, self.tee['name'])
  
  def __repr__(self):
    return 'GolfScore(dct={})'.format(self.toDict())

