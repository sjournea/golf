""" game.py - GolfGame class."""
from .exceptions import GolfException

class GolfGame(object):
  """Base class for all golf games."""
  def __init__(self, golf_round, scores, options=None):
    self.golf_round = golf_round
    self.scores = scores
    self.options = options if options else {}

  def validate(self):
    """Validate a game."""
    pass

  def start(self):
    """Start the game."""
    pass

  def addScore(self, hole_index, lstScores):
    """add scores for a hole."""
    pass

  def getScorecard(self, **kwargs):
    """Return scorecard dictionary for this game."""
    pass
  
  def getLeaderboard(self, **kwargs):
    """Return leaderboard dictionary for this game."""
    pass

  def complete(self):
    """Complete a game. Overload for process when a game is complete."""
    pass



