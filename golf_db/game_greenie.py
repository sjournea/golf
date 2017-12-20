""" game_greenie.py - GolfGame class."""
from .game import GolfGame


class GreenieGame(GolfGame):
  """Basic Par 3 games."""
  short_description = 'Greenie'
  description = """
Closest shot to the pin on par 3 (on the green) and makes a par or better wins the hole.

Options:
  double_birdie: Birdies are worth double points. 
  carry_over: If nobody wins a par 3 then carries over to next par 3.
  last_par_3_carry: If nobody wins last par 3 then carry over to next hole and on green in regulation quailifies.  
"""
  def __init__(self, golf_round, scores, **kwargs):
    super(GreenieGame, self).__init__(golf_round, scores, **kwargs)
    self._carry_over = kwargs.get('carry_over', True)
    self._double_birdie = kwargs.get('double_birdie', True)
    self._last_par_3_carry = kwargs.get('last_par_3_carry', True)

  def start(self):
    """Start the game."""
    for pl in self.scores:
      # points won
      pl._points = [None for _ in range(len(self.golf_round.course.holes))]
      pl._in = 0
      pl._out = 0
      pl._total = 0
      
    self._carry = 0
    self._next_hole = 0
    self._use_green_in_regulation = False
    # add header to scorecard
    self.dctScorecard['header'] = '{0:*^98}'.format(' '+ self.short_description + ' ')
    self.dctLeaderboard['hdr'] = 'Pos Name   Points Thru'
  
  def setOptions(self, options):
    """Additional options set for each add score."""
    super(GreenieGame, self).setOptions(options)
    self._closest_to_pin = options.get('closest_to_pin')

  def addScore(self, index, lstGross):
    """add scores for a hole.
    
    Args:
      index: hole index [0..holes-1]
      lstGross: list of gross scores for all players.
    """
    if self.golf_round.course.holes[index].isPar(3) or self._use_green_in_regulation:
      par = self.golf_round.course.holes[index].par
      if self._closest_to_pin is not None and lstGross[self._closest_to_pin] <= par:
        winner = self.scores[self._closest_to_pin]
        # only get points on par 3, not greens in regulation carryover
        value = 1 if par == 3 else 0
        winner._points[index] = value + self._carry
        self._carry = 0
        if self._double_birdie and lstGross[self._closest_to_pin] < par:
          # birdie or better
          winner._points[index] *= 2
        winner._out = sum([sc for sc in winner._points[:9] if isinstance(sc, int)])
        winner._in = sum([sc for sc in winner._points[9:] if isinstance(sc, int)])
        winner._total = winner._in + winner._out
      else:
        if self._carry_over and par == 3:
          self._carry += 1
          if self._last_par_3_carry and self.golf_round.course.lastPar(3) == index:
            self._use_green_in_regulation = True
  
    self._next_hole += 1
    if self._next_hole == 18:
      self._next_hole = None
      
  def getScorecard(self, **kwargs):
    """Scorecard with all players."""
    lstPlayers = []
    for n,score in enumerate(self.scores):
      dct = {'player': score.player }
      dct['in'] = score._in
      dct['out'] = score._out
      dct['total'] = score._total
      # build line for stdout
      line = '{:<6}'.format(score.player.nick_name)
      for point in score._points[:9]:
        line += ' {:>3}'.format(point) if point is not None else '    '
      line += ' {:>4}'.format(score._out)
      for point in score._points[9:]:
        line += ' {:>3}'.format(point) if point is not None else '    '
      line += ' {:>4} {:>4}'.format(score._in, score._total)
      dct['line'] = line
      lstPlayers.append(dct)
    self.dctScorecard['players'] = lstPlayers
    return self.dctScorecard

  def getLeaderboard(self, **kwargs):
    """Scorecard with all players."""
    board = []
    scores = sorted(self.scores, key=lambda score: score._total, reverse=True)
    pos = 1
    prev_total = None
    for score in scores:
      score_dct = {
        'player': score.player,
        'total' : score._total,
      }
      if prev_total != None and score_dct['total'] > prev_total:
        pos += 1
      prev_total = score_dct['total']
      score_dct['pos'] = pos
      for n,point in enumerate(score._points):
        if point is None:
          break
      else:
        n += 1
      score_dct['thru'] = n
      score_dct['line'] = '{:<3} {:<6} {:>5} {:>4}'.format(
        score_dct['pos'], score_dct['player'].nick_name, score_dct['total'], score_dct['thru'])
      board.append(score_dct)
    self.dctLeaderboard['leaderboard'] = board
    return self.dctLeaderboard

  def getStatus(self, **kwargs):
    """Scorecard with all players."""
    if self._next_hole is None:
      self.dctStatus['next_hole'] = None
      self.dctStatus['line'] = 'Round complete'
    else:
      self.dctStatus['next_hole'] = self._next_hole+1
      line = ''
      if self.golf_round.course.holes[self._next_hole].isPar(3):
        self.dctStatus['par'] = 3
        self.dctStatus['handicap'] = self.golf_round.course.holes[self._next_hole].handicap
        line = 'Hole {} Par {} Hdcp {}'.format(
            self.dctStatus['next_hole'], self.dctStatus['par'], self.dctStatus['handicap'])
      line += 'Carry:{}'.format(self._carry)
      if self._use_green_in_regulation:
        line += ' Use all greens'
      self.dctStatus['line'] = line
    return self.dctStatus
