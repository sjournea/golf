""" game.py - GolfGame class."""
from .game import GolfGame
from .exceptions import GolfException


class SixPointGame(GolfGame):
  """Six point golf game.
  
  Game for a threesome. 6 points per hole, breakdown:
    Rank   Points
    ----   ------  
    1,2,3  4,2,0
    1,2,2  4,1,1
    1,1,2  3,3,0
    1,1,1  2,2,2
  """
  POINTS_WIN_1ST = 4
  POINTS_TIE_1ST = 3
  POINTS_WIN_2ND = 2
  POINTS_TIE_2ND = 1
  POINTS_ALL_TIE = 2
  POINTS_3RD     = 0
  
  def validate(self):
    if len(self.scores) != 3:
      raise GolfException('Six point game must have 3 players, {} found.'.format(len(self.scores)))

  def start(self):
    """Start the skins game."""
    self.validate()
    # find min handicap in all players
    min_handicap = min([gs.course_handicap for gs in self.scores])
    for sc in self.scores:
      # net start
      sc.net = {
        'score' : [0 for _ in range(len(self.golf_round.course.holes))], 
        'bump': self.golf_round.course.calcBumps(sc.course_handicap - min_handicap),
        'in' : 0,
        'out':  0,
        'total': 0,
      }
      sc.points = {
        'point': [None for _ in range(len(self.golf_round.course.holes))],
        'in': 0,
        'out': 0,
        'total': 0,
     }

  def addScore(self, index, lstGross):
    """add scores for a hole."""
    # update net values
    for gs, gross in zip(self.scores, lstGross):
      gs.net['score'][index] = gross - gs.net['bump'][index]
      gs.net['out'] = sum([score for score in gs.net['score'][:9] if isinstance(score, int)])
      gs.net['in'] = sum([score for score in gs.net['score'][9:] if isinstance(score, int)])
      gs.net['total'] = gs.net['in'] + gs.net['out']
    # Determine net standings on this hole
    net_scores = [[n, sc.net['score'][index], 0, 0] for n,sc in enumerate(self.scores)]
    net_scores = sorted(net_scores, key=lambda sc: sc[1])
    pos = 1
    prev_total = None
    for lst in net_scores:
      if prev_total != None and lst[1] > prev_total:
        pos += 1
      prev_total = lst[1]
      lst[2] = pos
    rank = [lst[2] for lst in net_scores]
    if rank.count(1) == 3:
      # 2,2,2
      for lst in net_scores:
        lst[3] = self.POINTS_ALL_TIE
    elif rank.count(1) == 2:
      # 3,3,0
      for lst in net_scores[:2]:
        lst[3] = self.POINTS_TIE_1ST
      net_scores[2][3] = self.POINTS_3RD
    else:
      # 1 winner
      net_scores[0][3] = self.POINTS_WIN_1ST
      # tie for 2nd
      if rank.count(2) == 2:
        for lst in net_scores[1:]:
          lst[3] = self.POINTS_TIE_2ND
      else:
        net_scores[1][3] = self.POINTS_WIN_2ND
        net_scores[2][3] = self.POINTS_3RD
    # put points
    for lst,sc in zip(net_scores, self.scores):
      #print lst
      self.scores[lst[0]].points['point'][index] = lst[3]        
    for sc in self.scores:
      sc.points['out'] = sum([point for point in sc.points['point'][:9] if isinstance(point, int)])
      sc.points['in'] = sum([point for point in sc.points['point'][9:] if isinstance(point, int)])
      sc.points['total'] = sc.points['in'] + sc.points['out']
  
  def getScorecard(self, **kwargs):
    """Scorecard with all players."""
    dct_scorecard = self.golf_round.course.getScorecard()
    dct_scorecard['header'] = '{0:*^93}'.format(' Six Points ')
    lstPlayers = []
    for n,score in enumerate(self.scores):
      dct = {'player': score.player }
      line = '{:<6}'.format(score.player.nick_name)
      points = score.points
      for point in points['point'][:9]:
        line += ' {:>3}'.format(point if point != None else '')
      line += ' {:>4d}'.format(points['out'])
      for point in points['point'][9:]:
        line += ' {:>3}'.format(point if point != None else '')
      line += ' {:>4d} {:>4d}'.format(points['in'], points['total'])
      dct['line'] = line
      dct['in'] = points['in']
      dct['out'] = points['out']
      dct['total'] = points['total']
      lstPlayers.append(dct)
    dct_scorecard['six_point'] = lstPlayers
    return dct_scorecard
  
  def getLeaderboard(self, **kwargs):
    dct = { 'hdr': 'Pos Name  Points Thru' }
    board = []
    scores = sorted(self.scores, key=lambda score: score.points['total'], reverse=True)
    pos = 1
    prev_total = None
    for score in scores:
      score_dct = {
        'player': score.player,
        'total' : score.points['total'],
      }
      if prev_total != None and score_dct['total'] < prev_total:
        pos += 1

      prev_total = score_dct['total']
      score_dct['pos'] = pos
      for n,point in enumerate(score.points['point']):
        if point is None:
          break
      else:
        n += 1
      score_dct['thru'] = n
      score_dct['line'] = '{:<3} {:<6} {:>+5} {:>4}'.format(
        score_dct['pos'], score_dct['player'].nick_name, score_dct['total'], score_dct['thru'])
      board.append(score_dct)
    dct['leaderboard'] = board
    return dct 

