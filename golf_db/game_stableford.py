""" game_stableford.py - Stableford Golf Game class."""
from .game import GolfGame
from .exceptions import GolfException

class StablefordGame(GolfGame):
  """The Stableford game."""
  dct_scoring = {
    'Classic': { -3: 8, -2: 5, -1: 2, 0: 0, 1: -1, 2:-2, 'min':8, 'max': -2},
    'British': { -3: 4, -2: 4, -1: 3, 0: 2, 1:  1, 2: 0, 'min':4, 'max': 0 },
    #'Spanish': { -3: 4, -2: 4, -1: 3, 0: 2, 1:  1, 2: 0, 'min':8, 'max': 0 },
  }

  def __init__(self, golf_round, scores, **kwargs):
    self.stableford_type = kwargs.get('stableford_type', 'Classic')
    super(StablefordGame, self).__init__(golf_round, scores, **kwargs)
  
  def validate(self):
    if self.stableford_type not in self.dct_scoring:
      raise GolfException('stableford_type {} not supported.'.format(self.stableford_type))

  def start(self):
    self.dct_stableford = self.dct_scoring[self.stableford_type]
    # use full handicap for all players
    for pl in self.scores:
      pl.net = {
        'score' : [None for _ in range(len(self.golf_round.course.holes))], 
        'bump': self.golf_round.course.calcBumps(pl.course_handicap),
      }
      pl.points = {
        'point': [None for _ in range(len(self.golf_round.course.holes))],
        'in': 0,
        'out': 0,
        'total': 0,
     }
    self.dctScorecard['header'] = '{0:*^93}'.format(' Stableford ')
    self.dctLeaderboard['hdr'] = 'Pos Name   Points Thru'

  def _calc_score(self, net_score):
    if net_score in self.dct_stableford:
      return self.dct_stableford[net_score]
    if net_score < 0:
      return self.dct_stableford['min']
    else:
      return self.dct_stableford['max']

  def addScore(self, index, lstGross):
    """add scores for a hole."""
    for pl, gross in zip(self.scores, lstGross):
      # update net
      net_score = gross - pl.net['bump'][index]
      pl.net['score'][index] = net_score
      pl.points['point'][index] = self._calc_score(net_score - self.golf_round.course.holes[index].par) 
      pl.points['out'] = sum([pt for pt in pl.points['point'][:9] if pt is not None])
      pl.points['in'] = sum([pt for pt in pl.points['point'][9:] if pt is not None])
      pl.points['total'] = pl.points['in'] + pl.points['out']
  
  def getScorecard(self, **kwargs):
    """Scorecard with all players."""
    lstPlayers = []
    for n,score in enumerate(self.scores):
      dct = {'player': score.player }
      line = '{:<6}'.format(score.player.nick_name)
      points = score.points
      for point in points['point'][:9]:
        s = '' if point is None else '{:d}'.format(point)
        line += ' {:>3}'.format(s)
      line += ' {:>4d}'.format(points['out'])
      for point in points['point'][9:]:
        s = '' if point is None else '{:d}'.format(point)
        line += ' {:>3}'.format(s)
      line += ' {:>4d} {:>4d}'.format(points['in'], points['total'])
      dct['line'] = line
      dct['in'] = points['in']
      dct['out'] = points['out']
      dct['total'] = points['total']
      lstPlayers.append(dct)
    self.dctScorecard['players'] = lstPlayers
    return self.dctScorecard
  
  def getLeaderboard(self, **kwargs):
    board = []
    scores = sorted(self.scores, key=lambda score: score.points['total'], reverse=True)
    pos = 1
    prev_total = None
    for score in scores:
      score_dct = {
        'player': score.player,
        'total' : score.points['total'],
      }
      if prev_total != None and score_dct['total'] > prev_total:
        pos += 1

      prev_total = score_dct['total']
      score_dct['pos'] = pos
      for n,point in enumerate(score.points['point']):
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
    for n,net in enumerate(self.scores[0].net['score']):
      if net is None:
        self.dctStatus['next_hole'] = n+1
        self.dctStatus['par'] = self.golf_round.course.holes[n].par
        self.dctStatus['handicap'] = self.golf_round.course.holes[n].handicap
        bumps = []
        bump_line = []
        for sc in self.scores:
          if sc.net['bump'][n] > 0:
            dct = {'player': sc.player, 'bumps': sc.net['bump'][n]}
            bumps.append(dct)
            bump_line.append('{}{}'.format(sc.player.nick_name, '({})'.format(dct['bumps']) if dct['bumps'] > 1 else ''))
        self.dctStatus['bumps'] = bumps
        self.dctStatus['line'] = 'Hole {} Par {} Hdcp {}'.format(
          self.dctStatus['next_hole'], self.dctStatus['par'], self.dctStatus['handicap'])
        if bumps:
          self.dctStatus['line'] += ' Bumps:{}'.format(','.join(bump_line))
        break
    else:
      # round complete
      self.dctStatus['next_hole'] = None
      self.dctStatus['par'] = self.golf_round.course.total
      self.dctStatus['handicap'] = None
      self.dctStatus['line'] = 'Round Complete'
    return self.dctStatus
