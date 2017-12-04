""" game_net.py - NetGame class.

Implements a Net golf game calculates the Net scores.
"""
from .game import GolfGame


class NetGame(GolfGame):
  """Basic net golf game. For us weekenders."""
  short_description = 'Net'
  description = """
One purpose of a golf handicap is to help players of different skill levels to create a fair match.
Take the difference between each handicap (e.g. 25 - 13 = 12) and that is the number of strokes given to the higher handicap player.
The bumps will be added to the lowest handicap holes on the course being played.
"""
  def __init__(self, golf_round, scores, **kwargs):
    self.use_full_net = kwargs.get('use_full_net', False)
    super(NetGame, self).__init__(golf_round, scores, **kwargs)

  def _calc_bumps(self, pl, min_handicap):
    if self.use_full_net:
      min_handicap = 0
    bumps = self.golf_round.course.calcBumps(pl.course_handicap - min_handicap)
    return bumps

  def start(self):
    """Start the game."""
    # find min handicap in all players
    min_handicap = min([gs.course_handicap for gs in self.scores])
    for pl in self.scores:
      # net start
      pl._net = [None for _ in range(len(self.golf_round.course.holes))]
      pl._bumps = self._calc_bumps(pl, min_handicap)
      pl._in = 0
      pl._out = 0
      pl._total = 0
    # add header to scorecard
    self.dctScorecard['header'] = '{0:*^98}'.format(' Net ')
    self.dctLeaderboard['hdr'] = 'Pos Name     Net Thru'

  def addScore(self, index, lstGross):
    """add scores for a hole.
    
    Args:
      index: hole index [0..holes-1]
      lstGross: list of gross scores for all players.
    """
    for gs, gross in zip(self.scores, lstGross):
      # update net
      gs._net[index] = gross - gs._bumps[index]
      gs._out = sum([sc for sc in gs._net[:9] if isinstance(sc, int)])
      gs._in = sum([sc for sc in gs._net[9:] if isinstance(sc, int)])
      gs._total = gs._in + gs._out

  def getScorecard(self, **kwargs):
    """Scorecard with all players."""
    lstPlayers = []
    for n,score in enumerate(self.scores):
      dct = {
        'player': score.player,
        'in': score._in,
        'out': score._out,
        'total': score._total,
      }
      line = '{:<6}'.format(score.player.nick_name)
      for net,bump in zip(score._net[:9], score._bumps[:9]):
        nets = '{}{}'.format(bump*'*', net if net > 0 else '')
        line += ' {:>3}'.format(nets)
      line += ' {:>4}'.format(score._out)
      for net,bump in zip(score._net[9:], score._bumps[9:]):
        nets = '{}{}'.format(bump*'*', net if net > 0 else '')
        line += ' {:>3}'.format(nets)
      line += ' {:>4} {:>4}'.format(score._in, score._total)
      dct['line'] = line
      lstPlayers.append(dct)
    self.dctScorecard['players'] = lstPlayers
    return self.dctScorecard

  def getLeaderboard(self, **kwargs):
    """Scorecard with all players."""
    board = []
    scores = sorted(self.scores, key=lambda score: score._total)
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
      for n,net in enumerate(score._net):
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
    for n,net in enumerate(self.scores[0]._net):
      if net is None:
        self.dctStatus['next_hole'] = n+1
        self.dctStatus['par'] = self.golf_round.course.holes[n].par
        self.dctStatus['handicap'] = self.golf_round.course.holes[n].handicap
        bumps = []
        bump_line = []
        for sc in self.scores:
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
