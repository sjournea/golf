""" game_putts.py - GolfGame class."""
from .game import GolfGame
from .exceptions import GolfException

class PuttGame(GolfGame):
  """Who has the fewest putts."""
  short_description = 'Putts'
  description = """
Who has the fewest putts in the round. Who has the best short game.
"""
  def start(self):
    """Start the game."""
    for pl in self.scores:
      # putts
      pl.dct_putts = self._init_dict()
    # add header to scorecard
    self.dctScorecard['header'] = '{0:*^98}'.format(' Putts ')
    self.dctLeaderboard['hdr'] = 'Pos Name   Putts Thru'
  
  def setOptions(self, options):
    """Additional options parsed by each test."""
    super(PuttGame, self).setOptions(options)
    self._lst_putts = options.get('putts')
    if not self._lst_putts:
      raise GolfException('{} - must set putts in options'.format(self.__class__.__name__))

  def addScore(self, index, lstGross):
    """PuttGame just uses putts that is set with setOptions."""
    self.addPutts(index, self._lst_putts)
  
  def addPutts(self, index, lstPutts):
    """add putts for a hole.
    
    Args:
      index: hole index [0..holes-1]
      lstPutts: list of putts for all players.
    """
    for gs, putt in zip(self.scores, lstPutts):
      # update gross
      gs.dct_putts['holes'][index] = putt
      self._update_totals(gs.dct_putts)

  def getScorecard(self, **kwargs):
    """Scorecard with all players."""
    lstPlayers = []
    for n,sc in enumerate(self.scores):
      dct = {'player': sc.player }
      dct['in'] = sc.dct_putts['in']
      dct['out'] = sc.dct_putts['out']
      dct['total'] = sc.dct_putts['total']
      # build line for stdout
      line = '{:<6}'.format(sc.player.nick_name)
      for putt in sc.dct_putts['holes'][:9]:
        line += ' {:>3}'.format(putt) if putt is not None else '    '
      line += ' {:>4}'.format(dct['out'])
      for putt in sc.dct_putts['holes'][9:]:
        line += ' {:>3}'.format(putt) if putt is not None else '    '
      line += ' {:>4} {:>4}'.format(dct['in'], dct['total'])
      dct['line'] = line
      lstPlayers.append(dct)
    self.dctScorecard['players'] = lstPlayers
    return self.dctScorecard

  def getLeaderboard(self, **kwargs):
    """Scorecard with all players."""
    board = []
    scores = sorted(self.scores, key=lambda score: score.dct_putts['total'])
    pos = 1
    prev_total = None
    for sc in scores:
      score_dct = {
        'player': sc.player,
        'total' : sc.dct_putts['total'],
      }
      if prev_total != None and score_dct['total'] > prev_total:
        pos += 1
      prev_total = score_dct['total']
      score_dct['pos'] = pos
      for n,putt in enumerate(sc.dct_putts['holes']):
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
    for n,putt in enumerate(self.scores[0].dct_putts['holes']):
      if putt is None:
        self.dctStatus['next_hole'] = n+1
        self.dctStatus['line'] = ''
        break
    else:
      # round complete
      self.dctStatus['next_hole'] = None
      self.dctStatus['line'] = 'Round complete'
    return self.dctStatus
