""" game_greenie.py - GolfGame class."""
from collections import OrderedDict
from .sql_game import SqlGolfGame, GamePlayer

class GreeniePlayer(GamePlayer):
  def __init__(self, game, result):
    super(GreeniePlayer, self).__init__(game, result)
    self.dct_greens = [None for _ in range(len(self.game.golf_round.course.holes))],
    self.dct_points = self._init_dict()
    self.dct_money = self._init_dict(score_type=float) if game._wager else None

class SqlGameGreenie(SqlGolfGame):
  """Basic Par 3 games."""
  short_description = 'Greenie'
  description = """
Closest shot to the pin on par 3 (on the green) and makes a par or better wins the hole.

Options:
  double_birdie: Birdies are worth double points. 
  carry_over: If nobody wins a par 3 then carries over to next par 3.
  last_par_3_carry: If nobody wins last par 3 then carry over to next hole and on green in regulation quailifies.  
"""
  def __init__(self, game, golf_round, **kwargs):
    super(SqlGameGreenie, self).__init__(game, golf_round, **kwargs)
    self._carry_over = kwargs.get('carry_over', True)
    self._double_birdie = kwargs.get('double_birdie', True)
    self._last_par_3_carry = kwargs.get('last_par_3_carry', True)
    self._holes = [hole.num for hole in self.golf_round.course.get_holes_with_par(3)]
    if self._last_par_3_carry:
      self._last_par_3 = self._holes[-1]
      self._holes += [hole.num for hole in self.golf_round.course.holes[self._last_par_3:]]
    
  def _start(self):
    """Start the game."""
    self._players = [GreeniePlayer(self, result) for result in self.golf_round.results]
    self._carry = 0
    self._next_hole = 0
    self._use_green_in_regulation = False
    self._thru = 0
    # add header to scorecard
    self.dctScorecard['header'] = '{0:*^98}'.format(' '+ self.short_description + ' ')
  
  def update(self):
    """Update gross results for all scores so far."""
    self._start()
    dct_greens = {hole_num: None for hole_num in self._holes}
    for pl, result in zip(self._players, self.golf_round.results):
      for n, score in enumerate(result.scores):
        if n+1 in self._holes:
          if dct_greens[n+1] is None:
            dct_greens[n+1] = []
          par = self.golf_round.course.holes[n].par
          if score.gross <= par and score.gross - score.putts == 1:
            dct_greens[n+1].append((pl, score.gross))
    hole_nums = sorted(dct_greens.keys())
    for hole_num in hole_nums:
      lst_winners = dct_greens[hole_num]
      if lst_winners == None:
        break
      index = hole_num-1
      par = self.golf_round.course.holes[index].par
      if len(lst_winners) > 1:
        if hole_num in self.game._game_data:
          qualified = self.game._game_data[hole_num]['qualified']
          lst_winners = [w for w in lst_winners if str(w[0].player.nick_name) == qualified]
        else:
          raise Exception('Need to resolve multiple greenie winners')
      if len(lst_winners) == 1:
        winner, gross = lst_winners[0]
        # only get points on par 3
        value = 1 if par == 3 else 0
        winner.dct_points['holes'][index] = value + self._carry
        self._carry = 0
        if self._double_birdie and gross < par:
          # birdie or better
          winner.dct_points['holes'][index] *= 2
          pl.update_totals(winner.dct_points)
        if self._wager:
          winner.dct_money['holes'][index] = winner.dct_points['holes'][index]*len(self._players)
          pl.update_totals(winner.dct_money)
      else:
        if self._carry_over and par == 3:
          self._carry += 1
      
  def getScorecard(self, **kwargs):
    """Scorecard with all players."""
    lstPlayers = []
    for n,score in enumerate(self._players):
      dct = {'player': score.player }
      dct['in'] = score.dct_points['in']
      dct['out'] = score.dct_points['out']
      dct['total'] = score.dct_points['total']
      # build line for stdout
      line = '{:<6}'.format(score.player.nick_name)
      for point in score.dct_points['holes'][:9]:
        line += ' {:>3}'.format(point) if point is not None else '    '
      line += ' {:>4}'.format(dct['out'])
      for point in score.dct_points['holes'][9:]:
        line += ' {:>3}'.format(point) if point is not None else '    '
      line += ' {:>4} {:>4}'.format(dct['in'], dct['total'])
      dct['line'] = line
      lstPlayers.append(dct)
    self.dctScorecard['players'] = lstPlayers
    return self.dctScorecard

  def getLeaderboard(self, **kwargs):
    board = []
    sort_type = kwargs.get('sort_type', 'points')
    if sort_type == 'money' and self._wager:
      self.dctLeaderboard['hdr'] = 'Pos Name  Money  Thru'
      scores = sorted(self._players, key=lambda score: score.dct_money['total'], reverse=True)
      sort_by = 'money'
    else:
      self.dctLeaderboard['hdr'] = 'Pos Name  Points Thru'
      scores = sorted(self._players, key=lambda score: score.dct_points['total'], reverse=True)
      sort_by = 'total'
    pos = 1
    prev_total = None
    for sc in scores:
      score_dct = {
        'player': sc.player,
        'total' : sc.dct_points['total'],
        'money' : sc.dct_money['total'] if self._wager else None,
      }
      if prev_total != None and score_dct[sort_by] != prev_total:
        pos += 1
      prev_total = score_dct[sort_by]
      score_dct['pos'] = pos
      score_dct['thru'] = self._thru
      if sort_by == 'money':
        money = '--' if score_dct['money'] == 0.0 else '${:<2g}'.format(score_dct['money'])
        score_dct['line'] = '{:<3} {:<6} {:^5} {:>4}'.format(
          score_dct['pos'], score_dct['player'].nick_name, money, score_dct['thru'])
      else:
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
      if self._next_hole in self._holes:
        self.dctStatus['par'] = self.golf_round.course.holes[self._next_hole].par
        self.dctStatus['handicap'] = self.golf_round.course.holes[self._next_hole].handicap
        line = 'Hole {} Par {} Hdcp {} '.format(
            self.dctStatus['next_hole'], self.dctStatus['par'], self.dctStatus['handicap'])
      line += 'Carry:{}'.format(self._carry)
      if self._wager and self._carry:
        line += ' ${:<6g}'.format(self._carry*self._wager*len(self._players))
      if self._use_green_in_regulation:
        line += ' All greens in play'
      self.dctStatus['line'] = line
    return self.dctStatus

  @property
  def total_payout(self):
    """Overload to only count Par 3 holes."""
    # calc total payout, game only uses Par 3
    if self._wager:
      return len(self._par_3_holes)*self._wager*len(self._players)
    return None

