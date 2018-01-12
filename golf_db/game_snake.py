""" game_snake.py - Implement."""
from .game_putts import PuttGame


class SnakeGame(PuttGame):
  """3 putt game."""
  short_description = 'Snake'
  description = """
3 putt a green and you could lose.
"""
  def __init__(self, golf_round, scores, **kwargs):
    super(SnakeGame, self).__init__(golf_round, scores, **kwargs)
    self._snake_type = kwargs.get('snake_type', 'Points')
    
  def start(self):
    """Start the game."""
    for pl in self.scores:
      # putts
      pl.dct_points = self._init_dict()
      pl.dct_money = self._init_dict(score_type=float) if self._wager else None
    self._has_snake = None
    self._thru = 0
    # update header to scorecard
    title = ' Snake - {} '.format(self._snake_type)
    self.dctScorecard['header'] = '{0:*^98}'.format(title)
  
  def setOptions(self, options):
    """Additional options parsed by each test."""
    super(SnakeGame, self).setOptions(options)
    self._closest_to_pin = options.get('closest_to_pin')

  def addPutts(self, index, lstPutts, **kwargs):
    """add putts for a hole.
    
    Args:
      index: hole index [0..holes-1]
      lstPutts: list of putts for all players.
    """
    self._thru = index+1
    if self._snake_type == 'Hold':
      snake_winner = None
      lst_three_putts = []
      for gs, putt in zip(self.scores, lstPutts):
        gs.dct_points[index] = 0
        if putt > 2:
          lst_three_putts.append((gs, putt))
      if len(lst_three_putts) > 1:
        # Determine which 3 putt gets snake
        # 1st, is there a putt of a greater number (4 putt?)
        max_putts = max([tup[1] for tup in lst_three_putts])
        lst_three_putts = [tup for tup in lst_three_putts if tup[1] == max_putts]
        if len(lst_three_putts) > 1:
          # now we have at least 2 with same number of putts
          closest_to_pin = kwargs.get('closest_to_pin')
          if self._closest_to_pin is None:
            raise Exception('closest_to_pin needs to be set to determine who gets the snake.')
          snake_winner = self.scores[self._closest_to_pin]
      elif len(lst_three_putts) == 1:
        # we have a 3 putt winner (loser)
        snake_winner = lst_three_putts[0][0]
  
      if snake_winner:
        if self._has_snake and self._has_snake == snake_winner:
          # immediate payout and release snake
          self._has_snake.dct_points['holes'][index] = -1
          self._has_snake = None
          if self._wager:
            # payout all other players
            # pay all other players the wager
            for sc in self.scores:
              if sc == snake_winner:
                sc.dct_money['holes'][index] = -self._wager*(len(self.scores)-1)
              else:
                sc.dct_money['holes'][index] = self._wager
        else:
          self._has_snake = snake_winner
      # snake automatic payout on 9 and 18
      if index in (8, 17) and self._has_snake:
        self._has_snake.dct_points['holes'][index] = -1
        self._has_snake = None
    else:
      for gs, putt in zip(self.scores, lstPutts):
        if putt > 2:
          gs.dct_points['holes'][index] = -1 
    for pl in self.scores:
      self._update_totals(pl.dct_points)
      if self._wager:
        self._update_totals(pl.dct_money)
    
  def getScorecard(self, **kwargs):
    """Scorecard with all players."""
    lstPlayers = []
    for n,score in enumerate(self.scores):
      dct = {'player': score.player }
      dct['in'] = score.dct_points['in']
      dct['out'] = score.dct_points['out']
      dct['total'] = score.dct_points['total']
      # build line for stdout
      line = '{:<6}'.format(score.player.nick_name)
      for putt in score.dct_points['holes'][:9]:
        line += ' {:>3}'.format(putt) if putt is not None else '    '
      line += ' {:>4}'.format(dct['out'])
      for putt in score.dct_points['holes'][9:]:
        line += ' {:>3}'.format(putt) if putt is not None else '    '
      line += ' {:>4} {:>4}'.format(dct['in'], dct['total'])
      dct['line'] = line
      lstPlayers.append(dct)
    self.dctScorecard['players'] = lstPlayers
    return self.dctScorecard

  def getLeaderboard(self, **kwargs):
    board = []
    sort_type = kwargs.get('sort_type', 'points')
    if sort_type == 'money' and self._wager:
      self.dctLeaderboard['hdr'] = 'Pos Name   Money Thru'
      scores = sorted(self.scores, key=lambda score: score.dct_money['total'], reverse=True)
      sort_by = 'money'
    else:
      self.dctLeaderboard['hdr'] = 'Pos Name  Points Thru'
      scores = sorted(self.scores, key=lambda score: score.dct_points['total'], reverse=True)
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
        money = '---' if score_dct['money'] == 0.0 else '${:2g}'.format(score_dct['money'])
        score_dct['line'] = '{:<3} {:<6} {:>5} {:>4}'.format(
          score_dct['pos'], score_dct['player'].nick_name, money, score_dct['thru'])
      else:
        score_dct['line'] = '{:<3} {:<6} {:>5} {:>4}'.format(
          score_dct['pos'], score_dct['player'].nick_name, score_dct['total'], score_dct['thru'])
      board.append(score_dct)
    self.dctLeaderboard['leaderboard'] = board
    return self.dctLeaderboard

  def getStatus(self, **kwargs):
    """Scorecard with all players."""
    for n,putt in enumerate(self.scores[0].dct_points['holes']):
      if putt is None:
        self.dctStatus['next_hole'] = n+1
        line = ''
        if self._snake_type == 'Hold':
          if self._has_snake:
            line = '{} has the snake.'.format(self._has_snake.player.nick_name)
          else:
            line = 'snake is free.'
        self.dctStatus['line'] = line
        break
    else:
      # round complete
      self.dctStatus['next_hole'] = None
      self.dctStatus['line'] = 'Round complete'
    return self.dctStatus
