""" game.py - GolfGame class."""
from abc import ABCMeta, abstractmethod
from .exceptions import GolfException
from .score import GolfScore

class GolfGame(object):
  """Base class for all golf games."""
  __metaclass__ = ABCMeta
  description = '<Description not set>'
  short_description = '<Not set>'
  
  def __init__(self, golf_round, scores, **kwargs):
    self.golf_round = golf_round
    self.players = kwargs.get('players')
    if not self.players:
      self.players = [n for n in xrange(len(scores))]
    self.scores = [GolfScore(dct=scores[n].toDict()) for n in self.players]
    self.dctScorecard = {'course': self.golf_round.course.getScorecard() }
    self.dctLeaderboard = {}
    self.dctStatus = {}
    self._wager = kwargs.get('wager')
    self.validate()
    
  def validate(self):
    """Validate a game."""
    if self._wager is not None:
      self._wager = float(self._wager)
      if self._wager <= 0:
        raise GolfException('Wager must be float value > 0')

  def setGrossScore(self, hole_index, lstScores, options):
    """set gross scores for a hole."""
    self.setOptions(options if options else {})
    lst = [lstScores[n] for n in self.players]
    self.addScore(hole_index, lst)

  @abstractmethod
  def start(self):
    """Start the game."""
    pass

  @abstractmethod
  def addScore(self, hole_index, lstScores):
    """add scores for a hole."""
    pass

  def setOptions(self, options):
    """Additional options parsed by each test."""
    pass
  
  def addPutts(self, hole_index, lstPutts, **kwargs):
    """add putts for a hole."""
    pass

  @abstractmethod
  def getScorecard(self, **kwargs):
    """Return scorecard dictionary for this game."""
    pass
  
  @abstractmethod
  def getLeaderboard(self, **kwargs):
    """Return leaderboard for this game.
    
    Will be list of dictionaries sorted in the order of 1st to last.
    """
    pass

  @abstractmethod
  def getStatus(self, **kwargs):
    """Return simple status for state of game."""
    pass

  def complete(self):
    """Complete a game. Overload for process when a game is complete."""
    pass


class GolfTeam:
  """Base class for all golf teams."""
  __metaclass__ = ABCMeta
  def __init__(self, players, **kwargs):
    self.name = kwargs.get('name')
    self.players = players[:]
    if not self.name:
      self.name = '/'.join([pl.getInitials() for pl in self.players])

  @abstractmethod
  def setup(self, course, min_handicap):
    pass

  @abstractmethod
  def calculate_score(self, index):
    pass

  @abstractmethod
  def update_points(self, index, other_team):
    pass
