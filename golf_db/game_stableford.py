""" game_stableford.py - Stableford Golf Game class."""
from .game import GolfGame
from .exceptions import GolfException

class StablefordGame(GolfGame):
  """The Stableford game."""
  short_description = 'Stableford'
  dct_scoring = {
    'Classic': { -3: 8, -2: 5, -1: 2, 0: 0, 1: -1, 2:-2, 'min':8, 'max': -2},
    'British': { -3: 4, -2: 4, -1: 3, 0: 2, 1:  1, 2: 0, 'min':4, 'max': 0 },
    'Spanish': { -3: 4, -2: 4, -1: 3, 0: 2, 1:  1, 2: 0, 'min':8, 'max': 0 },
  }

  def __init__(self, golf_round, scores, **kwargs):
    self.stableford_type = kwargs.get('stableford_type', 'Classic')
    self.jokers = kwargs.get('jokers')
    super(StablefordGame, self).__init__(golf_round, scores, **kwargs)

  def validate(self):
    if self.stableford_type not in self.dct_scoring:
      raise GolfException('stableford_type {} not supported.'.format(self.stableford_type))
    if self.stableford_type == 'Spanish':
      if not self.jokers:
        raise GolfException('stableford_type Spanish needs jokers set.')
      if len(self.jokers) != len(self.scores):
        raise GolfException('stableford_type Spanish needs a joker set for each player.')
      for joker in self.jokers:
        if len(joker) != 2:
          raise GolfException('stableford_type Spanish jokers must have 2 values.')
        if joker[0] not in (1,2,3,4,5,6,7,8,9):
          raise GolfException('stableford_type Spanish joker[0] must be in 1-9.')
        if joker[1] not in (10,11,12,13,14,15,16,17,18):
          raise GolfException('stableford_type Spanish joker[1] must be in 10-18.')

  def start(self):
    self.dct_stableford = self.dct_scoring[self.stableford_type]
    # use full handicap for all players
    for n,pl in enumerate(self.scores):
      pl._score = [None for _ in range(len(self.golf_round.course.holes))]
      pl._bumps = self.golf_round.course.calcBumps(pl.course_handicap)
      pl._points = [None for _ in range(len(self.golf_round.course.holes))]
      pl._in = 0
      pl._out = 0
      pl._total = 0
      pl._jokers = self.jokers[n] if self.stableford_type == 'Spanish' else None
    self.dctScorecard['header'] = '{0:*^98}'.format(' Stableford ')
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
      net_score = gross - pl._bumps[index]
      pl._score[index] = net_score
      pl._points[index] = self._calc_score(net_score - self.golf_round.course.holes[index].par)
      if pl._jokers:
        if (index+1) in pl._jokers:
          pl._points[index] *= 2  
      pl._out = sum([pt for pt in pl._points[:9] if pt is not None])
      pl._in = sum([pt for pt in pl._points[9:] if pt is not None])
      pl._total = pl._in + pl._out
  
  def getScorecard(self, **kwargs):
    """Scorecard with all players."""
    lstPlayers = []
    for n,sc in enumerate(self.scores):
      dct = {'player': sc.player }
      dct['in'] = sc._in
      dct['out'] = sc._out
      dct['total'] = sc._total
      line = '{:<6}'.format(sc.player.nick_name)
      for i,point in enumerate(sc._points[:9]):
        s = '*' if sc._jokers and (i+1) in sc._jokers else ''
        s += '' if point is None else '{:d}'.format(point)
        line += ' {:>3}'.format(s)
      line += ' {:>4d}'.format(sc._out)
      for i,point in enumerate(sc._points[9:]):
        s = '*' if sc._jokers and (i+10) in sc._jokers else ''
        s += '' if point is None else '{:d}'.format(point)
        line += ' {:>3}'.format(s)
      line += ' {:>4d} {:>4d}'.format(sc._in, sc._total)
      dct['line'] = line
      lstPlayers.append(dct)
    self.dctScorecard['players'] = lstPlayers
    return self.dctScorecard
  
  def getLeaderboard(self, **kwargs):
    board = []
    scores = sorted(self.scores, key=lambda score: score._total, reverse=True)
    pos = 1
    prev_total = None
    for sc in scores:
      score_dct = {
        'player': sc.player,
        'total' : sc._total,
      }
      if prev_total != None and score_dct['total'] > prev_total:
        pos += 1

      prev_total = score_dct['total']
      score_dct['pos'] = pos
      for n,point in enumerate(sc._points):
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
    for n,net in enumerate(self.scores[0]._score):
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
          self.dctStatus['line'] += ' Bumps:{}'.format(','.join(bump_line))
        break
    else:
      # round complete
      self.dctStatus['next_hole'] = None
      self.dctStatus['par'] = self.golf_round.course.total
      self.dctStatus['handicap'] = None
      self.dctStatus['line'] = 'Round Complete'
    return self.dctStatus
