""" game_match.py - GolfGame class."""
from .game import GolfGame
from .exceptions import GolfException


class MatchGame(GolfGame):
  """Match golf game."""
  def validate(self):
    if len(self.scores) != 2:
      raise GolfException('Match game must have 2 players, {} found.'.format(len(self.scores)))

  def start(self):
    """Start the match game."""
    # find min handicap in all players
    min_handicap = min([gs.course_handicap for gs in self.scores])
    for pl in self.scores:
      # net start
      pl.net = {
        'score' : [None for _ in range(len(self.golf_round.course.holes))], 
        'bump': self.golf_round.course.calcBumps(pl.course_handicap - min_handicap),
      }
      pl.match = {
        'hole': [None for _ in range(len(self.golf_round.course.holes))],
        'score': [None for _ in range(len(self.golf_round.course.holes))],
        'in': 0,
        'out': 0,
        'total': 0,
      }
    self.win = None
    self.final = False
    self.match_score = None
    self.dctScorecard['header'] = '{0:*^93}'.format(' Match ')

  def addScore(self, index, lstGross):
    """add scores for a hole."""
    for gs, gross in zip(self.scores, lstGross):
      # update net
      gs.net['score'][index] = gross - gs.net['bump'][index]

    if not self.final:
      # Find net winner on this hole
      net_scores = [sc.net['score'][index] for sc in self.scores]
      if net_scores[0] < net_scores[1]:
        # player 0 wins hole 
        self.scores[0].match['hole'][index] = 1
        self.scores[0].match['total'] += 1
        self.scores[0].match['score'][index] = self.scores[0].match['total']
        self.scores[1].match['hole'][index] = -1
        self.scores[1].match['total'] -= 1
        self.scores[1].match['score'][index] = self.scores[1].match['total']
      elif net_scores[0] > net_scores[1]:
        # player 1 wins hole
        self.scores[0].match['hole'][index] = -1
        self.scores[0].match['total'] -= 1
        self.scores[0].match['score'][index] = self.scores[0].match['total']
        self.scores[1].match['hole'][index] = 1
        self.scores[1].match['total'] += 1
        self.scores[1].match['score'][index] = self.scores[1].match['total']
      else: 
        # hole tied
        self.scores[0].match['hole'][index] = 0
        self.scores[0].match['score'][index] = self.scores[0].match['total']
        self.scores[1].match['hole'][index] = 0
        self.scores[1].match['score'][index] = self.scores[1].match['total']
  
      for gs in self.scores:
        gs.match['out'] = sum([sc for sc in gs.match['hole'][:9] if isinstance(sc, int)])
        gs.match['in'] = sum([sc for sc in gs.match['hole'][9:] if isinstance(sc, int)])
  
  def getScorecard(self, **kwargs):
    """Scorecard with all players."""
    lstPlayers = []
    for n,score in enumerate(self.scores):
      dct = {'player': score.player }
      line = '{:<6}'.format(score.player.nick_name)
      match = score.match
      for x,bump in zip(match['score'][:9], score.net['bump'][:9]):
        xs = '{:+d}'.format(x) if x is not None else ''
        xs = '{}{}'.format('*' if bump > 0 else '',xs)
        line += ' {:>3}'.format(xs)
      line += ' {:>+4d}'.format(match['out'])
      for x,bump in zip(match['score'][9:], score.net['bump'][9:]):
        xs = '{:+d}'.format(x) if x is not None else ''
        xs = '{}{}'.format('*' if bump > 0 else '',xs)
        line += ' {:>3}'.format(xs)
      line += ' {:>+4d} {:>+4d}'.format(match['in'], match['total'])
      dct['line'] = line
      dct['in'] = match['in']
      dct['out'] = match['out']
      dct['total'] = match['total']
      lstPlayers.append(dct)
    self.dctScorecard['players'] = lstPlayers
    return self.dctScorecard
  
  def getLeaderboard(self, **kwargs):
    if not self.final:
      for n,score in enumerate(self.scores[0].match['score']):
        if score == None:
          thru = n
          to_play = len(self.scores[0].match['score']) - thru
          break
      else:
        self.final = True
        thru = len(self.scores[0].match['score'])
        to_play = 0
      
      self.dctLeaderboard['thru'] = thru
      self.dctLeaderboard['to_play'] = to_play
      self.dctLeaderboard['final'] = self.final
      board = []
      for n,score in enumerate(self.scores):
        player = score.player
        dct = {'player': player }
        total = score.match['total']
        if total == 0:
          status = 'All Square'
        elif total > 0:
          if to_play > 0 and (total > to_play):
            self.final = True
            status = '{} & {}'.format(total, to_play)
            self.win = n
          else:
            status = '{} Up'.format(total)
            if to_play == 0:
              self.final = True
            elif to_play < 5:
              status += ' {} to play'.format(to_play)
        elif total < 0:
          status = '{} Down'.format(abs(total))
  
        line = '{:<20}'.format(player.getFullName())
        if total > 0 or (total == 0 and n == 0):
          line += status
  
        dct['total'] = total
        dct['status'] = status
        dct['line'] = line
        board.append(dct)
      self.dctLeaderboard['leaderboard'] = board
      self.dctLeaderboard['hdr'] = '{:<20}{}'.format('Match', 'Final' if self.final else 'Thru {}'.format(thru))
      if self.final:
        if self.win is not None:
          winner = self.dctLeaderboard['leaderboard'][self.win]
          self.match_score = winner['status']
        else:
          self.match_score = 'Draw'
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
          self.dctStatus['line'] += ' Bumps: {}'.format(','.join(bump_line))
        break
    else:
      # round complete
      self.dctStatus['next_hole'] = None
      self.dctStatus['par'] = self.golf_round.course.total
      self.dctStatus['handicap'] = None
      self.dctStatus['line'] = 'Round Complete'
    return self.dctStatus