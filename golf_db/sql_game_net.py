""" game_net.py - NetGame class.

Implements a Net golf game calculates the Net scores.
"""
from .sql_game import SqlGolfGame, GamePlayer

class NetPlayer(GamePlayer):
  def __init__(self, game, result, min_handicap):
    super(NetPlayer, self).__init__(game, result)
    self.dct_net = self._init_dict()
    self._bumps = self.calc_bumps(min_handicap)


class SqlGameNet(SqlGolfGame):
  """Basic net golf game. For us weekenders."""
  short_description = 'Net'
  description = """
One purpose of a golf handicap is to help players of different skill levels to create a fair match.
Take the difference between each handicap (e.g. 25 - 13 = 12) and that is the number of strokes given to the higher handicap player.
The bumps will be added to the lowest handicap holes on the course being played.
"""
  def setup(self, **kwargs):
    """Start the game."""
    self.use_full_net = kwargs.get('use_full_net', False)
    # find min handicap in all players
    if self.use_full_net:
      min_handicap = 0
    else:
      min_handicap = min([result.course_handicap for result in self.golf_round.results])
    self._players = [NetPlayer(self, result, min_handicap) for result in self.golf_round.results]
    # add header to scorecard
    self.dctScorecard['header'] = '{0:*^98}'.format(' Net ')
    self.dctLeaderboard['hdr'] = 'Pos Name     Net Thru'

  def update(self):
    """Update gross results for all scores so far."""
    for pl, result in zip(self._players, self.golf_round.results):
      for n,score in enumerate(result.scores):
        # update net 
        pl.dct_net['holes'][n] = score.gross - pl._bumps[n]
      pl.update_totals(pl.dct_net)

  def getScorecard(self, **kwargs):
    """Scorecard with all players."""
    lstPlayers = []
    for n,sc in enumerate(self._players):
      dct = {
        'player': sc.player,
        'in': sc.dct_net['in'],
        'out': sc.dct_net['out'],
        'total': sc.dct_net['total'],
      }
      line = '{:<6}'.format(sc.player.nick_name)
      for net,bump in zip(sc.dct_net['holes'][:9], sc._bumps[:9]):
        nets = '{}{}'.format(bump*'*', net if net > 0 else '')
        line += ' {:>3}'.format(nets)
      line += ' {:>4}'.format(dct['out'])
      for net,bump in zip(sc.dct_net['holes'][9:], sc._bumps[9:]):
        nets = '{}{}'.format(bump*'*', net if net > 0 else '')
        line += ' {:>3}'.format(nets)
      line += ' {:>4} {:>4}'.format(dct['in'], dct['total'])
      dct['line'] = line
      lstPlayers.append(dct)
    self.dctScorecard['players'] = lstPlayers
    return self.dctScorecard

  def getLeaderboard(self, **kwargs):
    """Scorecard with all players."""
    board = []
    scores = sorted(self._players, key=lambda score: score.dct_net['total'])
    pos = 1
    prev_total = None
    for sc in scores:
      score_dct = {
        'player': sc.player,
        'total' : sc.dct_net['total'],
      }
      if prev_total != None and score_dct['total'] > prev_total:
        pos += 1
      prev_total = score_dct['total']
      score_dct['pos'] = pos
      for n,net in enumerate(sc.dct_net['holes']):
        if net == None:
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
    """."""
    for n,net in enumerate(self._players[0].dct_net['holes']):
      if net is None:
        self.dctStatus['next_hole'] = n+1
        self.dctStatus['par'] = self.golf_round.course.holes[n].par
        self.dctStatus['handicap'] = self.golf_round.course.holes[n].handicap
        bumps = []
        bump_line = []
        for sc in self._players:
          if sc._bumps[n] > 0:
            dct = {'player': sc.player, 'bumps': sc._bumps[n]}
            bumps.append(dct)
            bump_line.append('{}{}'.format(sc.player.nick_name, '({})'.format(dct['bumps']) if dct['bumps'] > 1 else ''))
        self.dctStatus['bumps'] = bumps
        self.dctStatus['line'] = 'Hole {} Par {} Hdcp {}'.format(
          self.dctStatus['next_hole'], self.dctStatus['par'], self.dctStatus['handicap'])
        if bumps:
          self.dctStatus['line'] += ' bumps: ' + ','.join(bump_line)
        break
    else:
      # round complete
      self.dctStatus['next_hole'] = None
      self.dctStatus['par'] = self.golf_round.course.total
      self.dctStatus['handicap'] = None
      self.dctStatus['line'] = 'Round Complete'
    return self.dctStatus
