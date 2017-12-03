""" game_snake.py - Implement."""
from .game_putts import PuttGame


class SnakeGame(PuttGame):
  """3 putt game."""
  short_description = 'Snake'
  description = """
All 3 putts will punished.
"""
  def start(self):
    """Start the game."""
    for pl in self.scores:
      # putts
      pl._three_putts = [None for _ in range(len(self.golf_round.course.holes))]
      pl._in = 0
      pl._out = 0
      pl._total = 0
    # update header to scorecard
    self.dctScorecard['header'] = '{0:*^98}'.format(' Snake ')
    self.dctLeaderboard['hdr'] = 'Pos Name   Snakes Thru'
  
  def addPutts(self, index, lstPutts):
    """add putts for a hole.
    
    Args:
      index: hole index [0..holes-1]
      lstPutts: list of putts for all players.
    """
    for gs, putt in zip(self.scores, lstPutts):
      # update gross
      gs._three_putts[index] = -1 if putt > 2 else 0
      gs._out = sum([sc for sc in gs._three_putts[:9] if isinstance(sc, int)])
      gs._in = sum([sc for sc in gs._three_putts[9:] if isinstance(sc, int)])
      gs._total = gs._in + gs._out

  def getScorecard(self, **kwargs):
    """Scorecard with all players."""
    lstPlayers = []
    for n,score in enumerate(self.scores):
      dct = {'player': score.player }
      dct['in'] = score._in
      dct['out'] = score._out
      dct['total'] = score._total
      # build line for stdout
      line = '{:<6}'.format(score.player.nick_name)
      for putt in score._three_putts[:9]:
        line += ' {:>3}'.format(putt) if putt is not None else '    '
      line += ' {:>4}'.format(score._out)
      for putt in score._three_putts[9:]:
        line += ' {:>3}'.format(putt) if putt is not None else '    '
      line += ' {:>4} {:>4}'.format(score._in, score._total)
      dct['line'] = line
      lstPlayers.append(dct)
    self.dctScorecard['players'] = lstPlayers
    return self.dctScorecard

  def getLeaderboard(self, **kwargs):
    """Scorecard with all players."""
    board = []
    scores = sorted(self.scores, key=lambda score: score._total, reverse=True)
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
      for n,putt in enumerate(score._three_putts):
        if putt is None:
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
    """Scorecard with all players."""
    for n,putt in enumerate(self.scores[0]._three_putts):
      if putt is None:
        self.dctStatus['next_hole'] = n+1
        self.dctStatus['line'] = ''
        break
    else:
      # round complete
      self.dctStatus['next_hole'] = None
      self.dctStatus['line'] = 'Round complete'
    return self.dctStatus
