from .course import GolfCourse
from .score import GolfScore
from .exceptions import GolfException

from util.tl_logger import TLLog

log = TLLog.getLogger('round')

class GolfRound(object):
  def __init__(self, dct=None):
    super(GolfRound, self).__init__()
    self.course = None
    self.date = None
    self.scores = []
    if dct:
      self.fromDict(dct)

  def fromDict(self, dct):
    self.course = GolfCourse(dct['course'])
    self.date = dct.get('date')
    self.scores = [GolfScore(player_dct) for player_dct in dct['players']]

  def toDict(self):
    return { 'course': self.course.toDict(),
             'date': self.date,
             'players': [player.toDict() for player in self.scores],
           }

  def __eq__(self, other):
    return (self.course == other.course and
            self.date == other.date and
            self.scores == other.scores)

  def __ne__(self, other):
    return not self == other

  def addPlayer(self, player, tee_name):
    """Add a player to this round."""
    gs = GolfScore()
    gs.player = player
    gender = 'mens' if gs.player.gender == 'man' else 'womens'
    gs.tee = self.course.getTee(tee_name, gender=gender )
    self.scores.append(gs)

  def start(self):
    """Start round.
    
    For each player:
      set course handicap.
      set 0's for gross and net.
    """
    for gs in self.scores:
      gs.start(self.course)
      
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
      
  def getScorecard(self):
    """Scorecard with all players."""
    dct_scorecard = self.course.getScorecard()
    for n,score in enumerate(self.scores):
      dct = {'player': score.player }
      gross_line = '{:<6}'.format(score.player.nick_name)
      for gross in score.gross['score'][:9]:
        gross_line += ' {:>3}'.format(gross) if gross > 0 else '    '
      gross_line += ' {:>4}'.format(score.gross['out'])
      for gross in score.gross['score'][9:]:
        gross_line += ' {:>3}'.format(gross) if gross > 0 else '    '
      gross_line += ' {:>4} {:>4}'.format(score.gross['in'], score.gross['total'])
      dct['gross_line'] = gross_line
      dct['gross_in'] = score.gross['in']
      dct['gross_out'] = score.gross['out']
      dct['gross_tot'] = score.gross['total']
      dct_scorecard['player_%d_gross' % n] = dct
      
    return dct_scorecard
  
  def getLeaderboard(self, game='gross'):
    """Return selected leaderboard.
    
    Args:
      game: game for leaderboard.
    Returns:
      dictionary of leaderboard current values.
    """
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
      score_dct['thru'] = n+1
      score_dct['line'] = '{:<3} {:<6} {:>5} {:>4}'.format(
        score_dct['pos'], score_dct['player'].nick_name, score_dct['total'], score_dct['thru'])
      board.append(score_dct)
    dct['leaderboard'] = board
    return dct 
  
  def __str__(self):
    return '{} - {:<25} - {:<25}'.format(
      self.date.date(), self.course.name, ','.join([score.player.nick_name for score in self.scores]))
