from .course import GolfCourse
from .score import GolfScore
from .exceptions import GolfException

from util.tl_logger import TLLog

log = TLLog.getLogger('round')

class GolfRound(object):
  legalGames = ('skins')
  
  def __init__(self, dct=None):
    super(GolfRound, self).__init__()
    self.course = None
    self.date = None
    self.scores = []
    self.games = {}
    if dct:
      self.fromDict(dct)

  def fromDict(self, dct):
    self.course = GolfCourse(dct['course'])
    self.date = dct.get('date')
    self.scores = [GolfScore(player_dct) for player_dct in dct['players']]
    self.games = dct.get('games', {})

  def toDict(self):
    return { 'course': self.course.toDict(),
             'date': self.date,
             'players': [player.toDict() for player in self.scores],
             'games': self.games,
           }

  def __eq__(self, other):
    return (self.course == other.course and
            self.date == other.date and
            self.scores == other.scores and
            self.games == other.games)

  def __ne__(self, other):
    return not self == other

  def addPlayer(self, player, tee_name):
    """Add a player to this round."""
    gs = GolfScore()
    gs.player = player
    gender = 'mens' if gs.player.gender == 'man' else 'womens'
    gs.tee = self.course.getTee(tee_name, gender=gender)
    gs.calcCourseHandicap()
    self.scores.append(gs)

  def addGame(self, game, options):
    """Add a game to this round.
    
    Args:
      game: Game to add.
      options: dictionary of game options.
    """
    if game not in self.legalGames:
      raise GolfException('Game {} not supported.'.format(game))
    self.games[game] = { 'options': options }
    for score in self.scores:
      score.addGame(game)
    
  def start(self):
    """Start round.
    
    For each player:
      set course handicap.
      set 0's for gross and net.
    """
    min_handicap = min([gs.course_handicap for gs in self.scores])
    for gs in self.scores:
      gs.start(self.course, min_handicap)
    for key, dct in self.games.items():
      if key == 'skins':
        dct['carryover'] = 1

  def addScores(self, hole, lstGross):
    """Add some scores for this round.

    Args:
      hole : hole number, 1-18.
      lstGross : gross score for each player.
    """
    if hole < 1 or hole > len(self.course.holes):
      raise GolfException('hole number must be in 1-{}'.format(len(self.course.holes)))
    if len(lstGross) != len(self.scores):
      raise GolfException('gross scores do not match number of players')
    for gs, gross in zip(self.scores, lstGross):
      gs.updateGross(hole, gross)
    # update all games
    for key, dct in self.games.items():
      if key == 'skins':
        # Find net winner on this hole
        index = hole - 1
        net_scores = [sc.net['score'][index] for sc in self.scores]
        net_scores.sort()
        print 'net_scores', net_scores
        if net_scores[0] < net_scores[1]:
          # we have a winner
          carryover = dct['carryover']
          for sc in self.scores:
            skins = sc.games['skins']
            if sc.net['score'][index] == net_scores[0]:
              win = carryover * (len(self.scores)-1)
              skins['skin'][index] += win
            else:
              skins['skin'][index] -= carryover
          dct['carryover'] = 1
        else:
          dct['carryover'] += 1
    for gs in self.scores:
      gs.updateGames()

  def getScorecard(self, game='gross'):
    """Scorecard with all players."""
    dct_scorecard = self.course.getScorecard()
    dct_scorecard['header'] = '***** ' + game.capitalize()+ ' *****'
    if game == 'gross':
      lstPlayers = []
      for n,score in enumerate(self.scores):
        dct = {'player': score.player }
        line = '{:<6}'.format(score.player.nick_name)
        for gross in score.gross['score'][:9]:
          line += ' {:>3}'.format(gross) if gross > 0 else '    '
        line += ' {:>4}'.format(score.gross['out'])
        for gross in score.gross['score'][9:]:
          line += ' {:>3}'.format(gross) if gross > 0 else '    '
        line += ' {:>4} {:>4}'.format(score.gross['in'], score.gross['total'])
        dct['line'] = line
        dct['in'] = score.gross['in']
        dct['out'] = score.gross['out']
        dct['total'] = score.gross['total']
        lstPlayers.append(dct)
      dct_scorecard['gross'] = lstPlayers
    elif game == 'net':
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
    elif game == 'skins':
      lstPlayers = []
      for n,score in enumerate(self.scores):
        dct = {'player': score.player }
        line = '{:<6}'.format(score.player.nick_name)
        skins = score.games['skins']
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
    else:
      raise GolfException('game "{}" not supported'.format(game))
    return dct_scorecard
  
  def getLeaderboard(self, game='gross'):
    """Return selected leaderboard.
    
    Args:
      game: game for leaderboard.
    Returns:
      dictionary of leaderboard current values.
    """
    if game == 'gross':
      dct = { 'hdr': 'Pos Name   Gross Thru' }
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
    elif game == 'net':
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
    elif game == 'skins':
      dct = { 'hdr': 'Pos Name   Skins Thru' }
      board = []
      scores = sorted(self.scores, key=lambda score: score.games['skins']['total'], reverse=True)
      pos = 1
      prev_total = None
      for score in scores:
        score_dct = {
          'player': score.player,
          'total' : score.games['skins']['total'],
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
        score_dct['line'] = '{:<3} {:<6} {:>5} {:>4}'.format(
          score_dct['pos'], score_dct['player'].nick_name, score_dct['total'], score_dct['thru'])
        board.append(score_dct)
    else:
      raise GolfException('game "{}" not supported'.format(game))

    dct['leaderboard'] = board
    return dct 
  
  def __str__(self):
    return '{} - {:<25} - {:<25} - {}'.format(
      self.date.date(), self.course.name,
      ','.join([score.player.nick_name for score in self.scores]),
      ','.join(self.games.keys()))
