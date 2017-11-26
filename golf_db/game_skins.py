""" game.py - GolfGame class."""
from .game import GolfGame

class SkinsGame(GolfGame):
  """The Skins game."""
  description = """
Skins is very much a match play format, but it is usually played between three or four players.
Each hole is played separately, and is won by the player with the lowest score on the hole -- that golfer wins 'the skin'.
The interesting part of the game happens when two or more players tie for the low score.
In this case there is 'no blood,' and the skin 'carries over' to the next hole, doubling its worth.
At the end of the game, each player settles up based on the number of skins they have. 

Skins games are played using handicaps by playing off of the lowest handicap golfer.
For example, imagine three golfers of handicaps 8, 16, and 28 were to play a game of skins.
In this match the lowest handicap golfer would play straight up,
the 16 handicap golfer would receive 8 strokes on the hardest 8 holes (as denoted by the HDCP number on the scorecard),
and the 28 handicap golfer would receive 2 strokes on the hardest two holes and a stroke on the rest of the holes.

Each person brings a skin to the hole, and the winner of the hole wins a skin from each of the losing players.
For a threesome this means that the winner wins two skins on a hole. For a foursome, this means three skins.
In both cases the other players each lose a skin. 
"""
  def start(self):
    """Start the skins game."""
    # find min handicap in all players
    min_handicap = min([gs.course_handicap for gs in self.scores])
    for pl in self.scores:
      # gross start
      # net start
      pl.net = {
        'score' : [None for _ in range(len(self.golf_round.course.holes))], 
        'bump': self.golf_round.course.calcBumps(pl.course_handicap - min_handicap),
      }
      pl.skins = {
        'skin': [0 for _ in range(len(self.golf_round.course.holes))],
        'in': 0,
        'out': 0,
        'total': 0,
     }
    # skins carryover set to 1
    self.carryover = 1
    self.dctScorecard['header'] = '{0:*^93}'.format(' Skins ')
    self.dctLeaderboard['hdr'] = 'Pos Name   Skins Thru'

  def addScore(self, index, lstGross):
    """add scores for a hole."""
    for gs, gross in zip(self.scores, lstGross):
      # update net
      gs.net['score'][index] = gross - gs.net['bump'][index]

    # Find net winner on this hole
    net_scores = [sc.net['score'][index] for sc in self.scores]
    net_scores.sort()
    if net_scores[0] < net_scores[1]:
      # we have a winner
      for sc in self.scores:
        if sc.net['score'][index] == net_scores[0]:
          win = self.carryover * (len(self.scores)-1)
          sc.skins['skin'][index] += win
        else:
          sc.skins['skin'][index] -= self.carryover
        sc.skins['out'] = sum(sc.skins['skin'][:9])
        sc.skins['in'] = sum(sc.skins['skin'][9:])
        sc.skins['total'] = sc.skins['in'] + sc.skins['out']
      self.carryover = 1
    else:
      self.carryover += 1
  
  def getScorecard(self, **kwargs):
    """Scorecard with all players."""
    lstPlayers = []
    for n,score in enumerate(self.scores):
      dct = {'player': score.player }
      line = '{:<6}'.format(score.player.nick_name)
      skins = score.skins
      for skin in skins['skin'][:9]:
        sk = '{:+d}'.format(skin) if skin != 0 else ''
        line += ' {:>3}'.format(sk)
      line += ' {:>+4d}'.format(skins['out'])
      for skin in skins['skin'][9:]:
        sk = '{:+d}'.format(skin) if skin != 0 else ''
        line += ' {:>3}'.format(sk)
      line += ' {:>+4d} {:>+4d}'.format(skins['in'], skins['total'])
      dct['line'] = line
      dct['in'] = skins['in']
      dct['out'] = skins['out']
      dct['total'] = skins['total']
      lstPlayers.append(dct)
    self.dctScorecard['players'] = lstPlayers
    return self.dctScorecard
  
  def getLeaderboard(self, **kwargs):
    board = []
    scores = sorted(self.scores, key=lambda score: score.skins['total'], reverse=True)
    pos = 1
    prev_total = None
    for score in scores:
      score_dct = {
        'player': score.player,
        'total' : score.skins['total'],
      }
      if prev_total != None and score_dct['total'] < prev_total:
        pos += 1

      prev_total = score_dct['total']
      score_dct['pos'] = pos
      for n,net in enumerate(score.net['score']):
        if net is None:
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
        self.dctStatus['line'] += ' Skins:{}'.format(self.carryover)
        break
    else:
      # round complete
      self.dctStatus['next_hole'] = None
      self.dctStatus['par'] = self.golf_round.course.total
      self.dctStatus['handicap'] = None
      self.dctStatus['line'] = 'Round Complete'
    return self.dctStatus
