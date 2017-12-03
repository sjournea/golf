""" game.py - GolfGame class."""
from .game import GolfGame
from .exceptions import GolfException


class SixPointGame(GolfGame):
  """Six point golf game."""
  description = """
In the Six Point Game, three players compete for six points per hole.
Before the game, the players should agree to how much each point is worth
(consider that a player who never wins a point on any hole will owe about 100 points to his/her friends).

Handicaps are used in this game - the best player plays as scratch, and the other two players receive the
same number of strokes as the difference between their and the best player's course handicap. 

On each hole, the points can break down in four ways (as mentioned above, the scores on each hole are adjusted by the players' handicaps):
If there is a clear winner on the hole, that player wins 4 points. The golfer who finishes second receives 2 points, and the last place golfer receives nothing (4-2-0).
If two golfers tie for second they each receive 1 point, and the clear winner receives 4 points. (4-1-1).
If two golfers tie for lowest score, they win 3 points each, and the golfer with the high score receives nothing (3-3-0).
If all three golfers tie the hole, they each receive 2 points (2-2-2).
At the end of the match, all the points are totaled, with the low-point-total player paying both the other players a sum based on the difference between their final point totals. The player with the second highest point total also pays the high-point player based on the difference between their point totals.
"""
  POINTS_WIN_1ST = 4
  POINTS_TIE_1ST = 3
  POINTS_WIN_2ND = 2
  POINTS_TIE_2ND = 1
  POINTS_ALL_TIE = 2
  POINTS_3RD     = 0
  TITLE = 'Six Point'  
  NAME = 'six_point'
  
  def validate(self):
    if len(self.scores) != 3:
      raise GolfException('Six point game must have 3 players, {} found.'.format(len(self.scores)))

  def start(self):
    """Start the skins game."""
    # find min handicap in all players
    min_handicap = min([gs.course_handicap for gs in self.scores])
    for sc in self.scores:
      # net start
      sc._score = [None for _ in range(len(self.golf_round.course.holes))]
      sc._bumps = self.golf_round.course.calcBumps(sc.course_handicap - min_handicap)
      sc._points = [None for _ in range(len(self.golf_round.course.holes))]
      sc._in = 0
      sc._out = 0
      sc._total = 0
    self.dctScorecard['header'] = '{0:*^98}'.format(' {} '.format(self.TITLE))
    self.dctLeaderboard['hdr'] = 'Pos Name  Points Thru'

  def addScore(self, index, lstGross):
    """add scores for a hole."""
    # update net values
    for gs, gross in zip(self.scores, lstGross):
      gs._score[index] = gross - gs._bumps[index]
    # Determine net standings on this hole
    net_scores = [[n, sc._score[index], 0, 0] for n,sc in enumerate(self.scores)]
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
      self.scores[lst[0]]._points[index] = lst[3]        
    for sc in self.scores:
      sc._out = sum([point for point in sc._points[:9] if isinstance(point, int)])
      sc._in = sum([point for point in sc._points[9:] if isinstance(point, int)])
      sc._total = sc._in + sc._out
  
  def getScorecard(self, **kwargs):
    """Scorecard with all players."""
    lstPlayers = []
    for n,sc in enumerate(self.scores):
      dct = {'player': sc.player }
      dct['in'] = sc._in
      dct['out'] = sc._out
      dct['total'] = sc._total
      line = '{:<6}'.format(sc.player.nick_name)
      for point in sc._points[:9]:
        line += ' {:>3}'.format(point if point != None else '')
      line += ' {:>4d}'.format(sc._out)
      for point in sc._points[9:]:
        line += ' {:>3}'.format(point if point != None else '')
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
      if prev_total != None and score_dct['total'] < prev_total:
        pos += 1

      prev_total = score_dct['total']
      score_dct['pos'] = pos
      for n,point in enumerate(sc._points):
        if point is None:
          break
      else:
        n += 1
      score_dct['thru'] = n
      score_dct['line'] = '{:<3} {:<6} {:>+5} {:>4}'.format(
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
        self.dctStatus['line'] += ' Points:{},{},{}'.format(
          self.POINTS_WIN_1ST, self.POINTS_WIN_2ND, self.POINTS_3RD)
        break
    else:
      # round complete
      self.dctStatus['next_hole'] = None
      self.dctStatus['par'] = self.golf_round.course.total
      self.dctStatus['handicap'] = None
      self.dctStatus['line'] = 'Round Complete'
    return self.dctStatus
