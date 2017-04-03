""" game_gross.py - GolfGame class."""
from .game import GolfGame


class GrossGame(GolfGame):
  """Basic gross game. Man's golf."""
  def start(self):
    """Start the game."""
    for pl in self.scores:
      # gross start
      pl.gross = {
        'score' : [0 for _ in range(len(self.golf_round.course.holes))], 
        'in' : 0,
        'out':  0,
        'total': 0,
        'esc': 0,
      }
    # add header to scorecard
    self.dctScorecard['course'] = self.golf_round.course.getScorecard(ESC=1)
    self.dctScorecard['header'] = '{0:*^98}'.format(' Gross ')
    self.dctLeaderboard['hdr'] = 'Pos Name   Gross Thru'
  
  def addScore(self, index, lstGross):
    """add scores for a hole.
    
    Args:
      index: hole index [0..holes-1]
      lstGross: list of gross scores for all players.
    """
    for gs, gross in zip(self.scores, lstGross):
      # update gross
      gs.gross['score'][index] = gross
      gs.gross['out'] = sum(gs.gross['score'][:9])
      gs.gross['in'] = sum(gs.gross['score'][9:])
      gs.gross['total'] = gs.gross['in'] + gs.gross['out']
      # update ESC score
      gs.gross['esc'] += self.golf_round.course.calcESC(index, gross, gs.course_handicap)

  def getScorecard(self, **kwargs):
    """Scorecard with all players."""
    lstPlayers = []
    for n,score in enumerate(self.scores):
      dct = {'player': score.player }
      line = '{:<6}'.format(score.player.nick_name)
      for gross in score.gross['score'][:9]:
        line += ' {:>3}'.format(gross) if gross > 0 else '    '
      line += ' {:>4}'.format(score.gross['out'])
      for gross in score.gross['score'][9:]:
        line += ' {:>3}'.format(gross) if gross > 0 else '    '
      line += ' {:>4} {:>4} {:>4}'.format(score.gross['in'], score.gross['total'], score.gross['esc'])
      dct['line'] = line
      dct['in'] = score.gross['in']
      dct['out'] = score.gross['out']
      dct['total'] = score.gross['total']
      dct['esc'] = score.gross['esc']
      lstPlayers.append(dct)
    self.dctScorecard['gross'] = lstPlayers
    return self.dctScorecard

  def getLeaderboard(self, **kwargs):
    """Scorecard with all players."""
    board = []
    scores = sorted(self.scores, key=lambda score: score.gross['total'])
    pos = 1
    prev_total = None
    for score in scores:
      score_dct = {
        'player': score.player,
        'total' : score.gross['total'],
      }
      if prev_total != None and score_dct['total'] > prev_total:
        pos += 1
      prev_total = score_dct['total']
      score_dct['pos'] = pos
      for n,gross in enumerate(score.gross['score']):
        if gross == 0:
          break
      else:
        n += 1
      score_dct['thru'] = n
      score_dct['line'] = '{:<3} {:<6} {:>5} {:>4}'.format(
        score_dct['pos'], score_dct['player'].nick_name, score_dct['total'], score_dct['thru'])
      board.append(score_dct)
    self.dctLeaderboard['leaderboard'] = board
    return self.dctLeaderboard
