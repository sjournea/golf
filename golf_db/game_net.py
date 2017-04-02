""" game_net.py - NetGame class.

Implements a Net golf game calculates the Net scores.
"""
from .game import GolfGame


class NetGame(GolfGame):
  """Basic net golf game. For us weekenders."""
  def start(self):
    """Start the game."""
    # find min handicap in all players
    min_handicap = min([gs.course_handicap for gs in self.scores])
    for pl in self.scores:
      # net start
      pl.net = {
        'score' : [0 for _ in range(len(self.golf_round.course.holes))], 
        'bump': self.golf_round.course.calcBumps(pl.course_handicap - min_handicap),
        'in' : 0,
        'out':  0,
        'total': 0,
      }

  def addScore(self, index, lstGross):
    """add scores for a hole.
    
    Args:
      index: hole index [0..holes-1]
      lstGross: list of gross scores for all players.
    """
    for gs, gross in zip(self.scores, lstGross):
      # update net
      gs.net['score'][index] = gross - gs.net['bump'][index]
      gs.net['out'] = sum(gs.net['score'][:9])
      gs.net['in'] = sum(gs.net['score'][9:])
      gs.net['total'] = gs.net['in'] + gs.net['out']

  def getScorecard(self, **kwargs):
    """Scorecard with all players."""
    dct_scorecard = self.golf_round.course.getScorecard()
    dct_scorecard['header'] = '{0:*^93}'.format(' Net ')
    lstPlayers = []
    for n,score in enumerate(self.scores):
      dct = {'player': score.player }
      line = '{:<6}'.format(score.player.nick_name)
      for net,bump in zip(score.net['score'][:9], score.net['bump'][:9]):
        nets = '{}{}'.format('*' if bump > 0 else '', net if net > 0 else '')
        line += ' {:>3}'.format(nets)
      line += ' {:>4}'.format(score.net['out'])
      for net,bump in zip(score.net['score'][9:], score.net['bump'][9:]):
        nets = '{}{}'.format('*' if bump > 0 else '', net if net > 0 else '')
        line += ' {:>3}'.format(nets)
      line += ' {:>4} {:>4}'.format(score.net['in'], score.net['total'])
      dct['line'] = line
      dct['in'] = score.net['in']
      dct['out'] = score.net['out']
      dct['total'] = score.net['total']
      lstPlayers.append(dct)
    dct_scorecard['net'] = lstPlayers
    return dct_scorecard

  def getLeaderboard(self, **kwargs):
    """Scorecard with all players."""
    dct = { 'hdr': 'Pos Name     Net Thru' }
    board = []
    scores = sorted(self.scores, key=lambda score: score.net['total'])
    pos = 1
    prev_total = None
    for score in scores:
      score_dct = {
        'player': score.player,
        'total' : score.net['total'],
      }
      if prev_total != None and score_dct['total'] > prev_total:
        pos += 1
      prev_total = score_dct['total']
      score_dct['pos'] = pos
      for n,net in enumerate(score.net['score']):
        if net == 0:
          break
      else:
        n += 1
      score_dct['thru'] = n
      score_dct['line'] = '{:<3} {:<6} {:>5} {:>4}'.format(
        score_dct['pos'], score_dct['player'].nick_name, score_dct['total'], score_dct['thru'])
      board.append(score_dct)
    dct['leaderboard'] = board
    return dct 

