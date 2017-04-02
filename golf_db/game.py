""" game.py - GolfGame class."""
from .exceptions import GolfException

class GolfGame(object):
  """Base class for all golf games."""
  def __init__(self, golf_round, scores, options=None):
    self.golf_round = golf_round
    self.scores = scores
    self.options = options if options else {}

  def validate(self):
    """Validate a game."""
    pass

  def start(self):
    """Start the game."""
    pass

  def addScore(self, hole_index, lstScores):
    """add scores for a hole."""
    pass

  def getScorecard(self, **kwargs):
    """Return scorecard dictionary for this game."""
    pass
  
  def getLeaderboard(self, **kwargs):
    """Return leaderboard dictionary for this game."""
    pass

  def complete(self):
    """Complete a game. Overload for process when a game is complete."""
    pass


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

  def complete(self):
    """a game is complete."""
    pass

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


class SkinsGame(GolfGame):
  """The Skins game."""
  
  def start(self):
    """Start the skins game."""
    # find min handicap in all players
    min_handicap = min([gs.course_handicap for gs in self.scores])
    for pl in self.scores:
      # gross start
      # net start
      pl.net = {
        'score' : [0 for _ in range(len(self.golf_round.course.holes))], 
        'bump': self.golf_round.course.calcBumps(pl.course_handicap - min_handicap),
        'in' : 0,
        'out':  0,
        'total': 0,
      }
      pl.skins = {
        'skin': [0 for _ in range(len(self.golf_round.course.holes))],
        'in': 0,
        'out': 0,
        'total': 0,
     }
    # skins carryover set to 1
    self.carryover = 1

  def addScore(self, index, lstGross):
    """add scores for a hole."""
    for gs, gross in zip(self.scores, lstGross):
      # update net
      gs.net['score'][index] = gross - gs.net['bump'][index]
      gs.net['out'] = sum(gs.net['score'][:9])
      gs.net['in'] = sum(gs.net['score'][9:])
      gs.net['total'] = gs.net['in'] + gs.net['out']

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
    dct_scorecard = self.golf_round.course.getScorecard()
    dct_scorecard['header'] = '{0:*^93}'.format(' Skins ')
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
    dct_scorecard['skins'] = lstPlayers
    return dct_scorecard
  
  def getLeaderboard(self, **kwargs):
    dct = { 'hdr': 'Pos Name   Skins Thru' }
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
        if net == 0:
          break
      else:
        n += 1
      score_dct['thru'] = n
      score_dct['line'] = '{:<3} {:<6} {:>+5} {:>4}'.format(
        score_dct['pos'], score_dct['player'].nick_name, score_dct['total'], score_dct['thru'])
      board.append(score_dct)
    dct['leaderboard'] = board
    return dct 
  
  def complete(self):
    """a game is complete."""
    pass


