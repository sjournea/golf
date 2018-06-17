""" game_gross.py - GolfGame class."""
from .sql_game_gross import SqlGameGross,GrossPlayer

class RewardsPlayer(GrossPlayer):
  def __init__(self, game, result):
    super(RewardsPlayer, self).__init__(game, result)
    self.dct_rewards = self._init_dict()
    self.dct_rewards['total'] = 0

  def update_rewards(self):
    self.dct_rewards['out'] = self.dct_rewards['holes'][:9].count('P') + self.dct_rewards['holes'][:9].count('B')
    self.dct_rewards['in']  = self.dct_rewards['holes'][9:].count('P') + self.dct_rewards['holes'][9:].count('B')
    self.dct_rewards['total'] = self.dct_rewards['in'] + self.dct_rewards['out']
    self.dct_rewards['pars'] = self.dct_rewards['holes'].count('P')
    self.dct_rewards['birdies'] = self.dct_rewards['holes'].count('B')

class SqlGameRewards(SqlGameGross):
  """Rewards game."""
  short_description = 'Rewards'
  description = """
Which ever player gets the most natural birdies and pars wins. If there are no birdies then pars win entire wager.
"""
  def setup(self, **kwargs):
    """Start the game."""
    kwargs['player_class'] = RewardsPlayer
    super(SqlGameRewards, self).setup(**kwargs)
    self.pars = [hole.par for hole in self.golf_round.course.holes]
    self.thru = 0    
    # add header to scorecard
    self.dctScorecard['course'] = self.golf_round.course.getScorecard()
    self.dctScorecard['header'] = '{0:*^98}'.format(' Rewards ')
    self.dctLeaderboard['hdr'] = 'Pos Name  Rewards Thru'
  
  def update(self):
    """Update gross results for all scores so far."""
    super(SqlGameRewards, self).update()
    self.thru = self.golf_round.get_completed_holes()    
    for pl, result in zip(self._players, self.golf_round.results):
      for score in result.scores:
        n = score.num-1
        # update birdies and pars
        gross = pl.dct_gross['holes'][n]
        if gross <= self.pars[n]-1:
          pl.dct_rewards['holes'][n] = 'B'
        elif gross == self.pars[n]:
          pl.dct_rewards['holes'][n] = 'P'
      pl.update_rewards()
    
  def getScorecard(self, **kwargs):
    """Scorecard with all players."""
    lstPlayers = []
    for n,score in enumerate(self._players):
      dct = {'player': score.result.player }
      dct['in'] = score.dct_rewards['in']
      dct['out'] = score.dct_rewards['out']
      dct['total'] = score.dct_rewards['total']
      dct['holes'] = score.dct_rewards['holes']
      # build line for stdout
      line = '{:<6}'.format(score.player.nick_name)
      for rewards in score.dct_rewards['holes'][:9]:
        line += ' {:>3}'.format(rewards) if rewards is not None else '    '
      line += ' {:>4}'.format(dct['out'])
      for rewards in score.dct_rewards['holes'][9:]:
        line += ' {:>3}'.format(rewards) if rewards is not None else '    '
      line += ' {:>4} {:>4}'.format(dct['in'], dct['total'])
      dct['line'] = line
      lstPlayers.append(dct)
    self.dctScorecard['players'] = lstPlayers
    return self.dctScorecard

  def getLeaderboard(self, **kwargs):
    """Scorecard with all players."""
    board = []
    scores = sorted(self._players, key=lambda score: score.dct_rewards['total'], reverse=True)
    pos = 1
    prev_total = None
    for score in scores:
      score_dct = {
        'player': score.player,
        'total' : score.dct_rewards['total'],
      }
      if prev_total != None and score_dct['total'] > prev_total:
        pos += 1
      prev_total = score_dct['total']
      score_dct['pos'] = pos
      for n,gross in enumerate(score.dct_rewards['holes']):
        if gross is None:
          break
      else:
        n += 1
      score_dct['thru'] = n
      score_dct['line'] = '{:<3} {:<2} {:>5} {:>4}'.format(
        score_dct['pos'], score_dct['player'].getInitials(), score_dct['total'], score_dct['thru'])
      board.append(score_dct)
    self.dctLeaderboard['leaderboard'] = board
    return self.dctLeaderboard

  def getStatus(self, **kwargs):
    """Scorecard with all players."""
    for n,gross in enumerate(self._players[0].dct_rewards['holes']):
      if gross is None:
        self.dctStatus['next_hole'] = n+1
        self.dctStatus['par'] = self.golf_round.course.holes[n].par
        self.dctStatus['handicap'] = self.golf_round.course.holes[n].handicap
        self.dctStatus['line'] = 'Hole {} Par {} Hdcp {}'.format(
          self.dctStatus['next_hole'], self.dctStatus['par'], self.dctStatus['handicap'])
        break
    else:
      # round complete
      self.dctStatus['next_hole'] = None
      self.dctStatus['par'] = self.golf_round.course.total
      self.dctStatus['handicap'] = None
      self.dctStatus['line'] = 'Round complete'
    return self.dctStatus

