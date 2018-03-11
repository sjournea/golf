""" game.py - GolfGame class."""
from abc import ABCMeta, abstractmethod
from .exceptions import GolfException
from .score import GolfScore
from util.proto import Proto
from util.tl_logger import TLLog

log = TLLog.getLogger('sqlgame')

class SqlGolfGame(object):
  """Base class for all golf games."""
  __metaclass__ = ABCMeta
  description = '<Description not set>'
  short_description = '<Not set>'
  
  def __init__(self, game, golf_round, **kwargs):
    self.game = game
    self.golf_round = golf_round
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

  @abstractmethod
  def update(self):
    """Overload to update the game."""
    pass


  @abstractmethod
  def getScorecard(self, **kwargs):
    """Return scorecard dictionary for this game."""
    pass
  
  @abstractmethod
  def getLeaderboard(self, **kwargs):
    """Return leaderboard for this game.
    
    Returns:
      list of dictionaries sorted in the order of 1st to last.
    """
    pass

  @abstractmethod
  def getStatus(self, **kwargs):
    """Return simple status for state of game."""
    pass


class GamePlayer(object):
  def __init__(self, game, result):
    self.game = game
    self.result = result
    self.player = result.player

  def _init_dict(self, score_type=int):
    """Create and initialize scoring dictionary.
      
      add holes, in, out, total.
    """
    return {
      'holes': [None for _ in range(len(self.game.golf_round.course.holes))],
      'in' : score_type(0),
      'out': score_type(0),
      'total': score_type(0),
    }

  def update_totals(self, dct):
    """Update totals in a dictionary. If a value is None it is not added.

       dct must contain the following keys:
         holes: list of number scores
         in: total for holes 10..18
         out: total for holes 1..9
         total: in + out + overall (if set).
    """
    dct['out'] = sum([sc for sc in dct['holes'][:9] if sc is not None])
    dct['in']  = sum([sc for sc in dct['holes'][9:] if sc is not None])
    dct['total'] = dct['in'] + dct['out'] + dct.get('overall', 0)

  def calc_bumps(self, min_handicap):
    return self.game.golf_round.course.calcBumps(self.result.course_handicap - min_handicap)


class SqlGolfTeam(object):
  """Base class for all golf teams."""
  __metaclass__ = ABCMeta
  def __init__(self, game, players, **kwargs):
    self.game = game
    self.name = kwargs.get('name')
    self.players = players[:]
    if not self.name:
      self.name = '/'.join([pl.player.getInitials() for pl in self.players])

  @abstractmethod
  def setup(self, min_handicap):
    pass

  @abstractmethod
  def calculate_score(self, index):
    pass

  @abstractmethod
  def update_points(self, index, other_team):
    pass
