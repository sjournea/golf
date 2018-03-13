""" game_snake.py - Implement."""
from .sql_game import SqlGolfGame,GamePlayer

class SnakePlayer(GamePlayer):
  def __init__(self, game, result):
    super(SnakePlayer, self).__init__(game, result)
    self.dct_points = self._init_dict()

class SqlGameSnake(SqlGolfGame):
  """3 putt game."""
  short_description = 'Snake'
  description = """
3 putt a green and you could lose.
"""
  def setup(self, **kwargs):
    """Start the game."""
    self._snake_type = kwargs.get('snake_type', 'Points')
    self._players = [SnakePlayer(self, result) for result in self.golf_round.results]
    self._has_snake = None
    # update header to scorecard
    title = ' Snake - {} '.format(self._snake_type)
    self.dctScorecard['header'] = '{0:*^98}'.format(title)
    self._thru = ''

  def update(self):
    """Update gross results for all scores so far."""
    dct_three_putts = {hole.num: None for hole in self.golf_round.course.holes}
    for pl, result in zip(self._players, self.golf_round.results):
      for n, score in enumerate(result.scores):
        if dct_three_putts[n+1] is None:
            dct_three_putts[n+1] = []
        if score.putts >= 3:
            dct_three_putts[n+1].append((pl, score.putts))
    hole_nums = sorted(dct_three_putts.keys())
    for hole_num in hole_nums:
      lst_losers = dct_three_putts[hole_num]
      if lst_losers == None:
        break
      self._thru = hole_num
      if lst_losers == []:
        continue
      index = hole_num-1
      if self._snake_type == 'Points':
        # all 3 putters lose a point
        for pl,putts in lst_losers:
          pl.dct_points['holes'][index] = -1
          pl.update_totals(pl.dct_points)
      elif self._snake_type == 'Hold':
        # only one loser allowed
        if len(lst_losers) > 1:
          # Determine which 3 putt gets snake
          # 1st, is there a largest putt
          max_putts = max([tup[1] for tup in lst_losers])
          print('max_putts', max_putts)
          lst_losers = [tup for tup in lst_losers if tup[1] == max_putts]
          if len(lst_losers) > 1:
            if hole_num in self.game._game_data:
              loser = self.game._game_data[hole_num]['closest_3_putt']
              lst_losers = [tup for tup in lst_losers if tup[0].player.nick_name == loser]
            else:
              raise Exception('Need to resolve multiple snake losers')
        #
        if len(lst_losers) == 1:
          # we have a 3 putt winner (loser)
          snake_winner = lst_losers[0][0]
        if snake_winner:
          if self._has_snake and self._has_snake == snake_winner:
            # immediate payout and release snake
            snake_winner.dct_points['holes'][index] = -1
            snake_winner.update_totals(snake_winner.dct_points)
            self._has_snake = None
          else:
            self._has_snake = snake_winner
        # snake automatic payout on 9 and 18
        if hole_num in (9, 18) and self._has_snake:
          self._has_snake.dct_points['holes'][index] = -1
          self._has_snake.update_totals(self._has_snake.dct_points)
          self._has_snake = None

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
    self.dctLeaderboard['hdr'] = 'Pos Name  Points Thru'
    scores = sorted(self._players, key=lambda score: score.dct_points['total'], reverse=True)
    sort_by = 'total'
    pos = 1
    prev_total = None
    for sc in scores:
      score_dct = {
        'player': sc.player,
        'total' : sc.dct_points['total'],
      }
      if prev_total != None and score_dct[sort_by] != prev_total:
        pos += 1
      prev_total = score_dct[sort_by]
      score_dct['pos'] = pos
      score_dct['thru'] = self._thru
      score_dct['line'] = '{:<3} {:<6} {:>5} {:>4}'.format(
        score_dct['pos'], score_dct['player'].nick_name, score_dct['total'], score_dct['thru'])
      board.append(score_dct)
    self.dctLeaderboard['leaderboard'] = board
    return self.dctLeaderboard

  def getStatus(self, **kwargs):
    """Scorecard with all players."""
    for n,putt in enumerate(self._players[0].dct_points['holes']):
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
