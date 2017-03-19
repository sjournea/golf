from .course import GolfCourse
from .score import GolfScore


class GolfRound(object):
  def __init__(self, dct):
    super(GolfRound, self).__init__()
    self.course = None
    self.date = None
    self.scores = None
    self.tee = None
    if dct:
      self.fromDict(dct)

  def fromDict(self, dct):
    self.course = GolfCourse(dct['course'])
    self.date = dct.get('date')
    self.scores = [GolfScore(player_dct) for player_dct in dct['players']]
    self.tee = dct.get('tee')

  def toDict(self):
    return { 'course': self.course.toDict(),
             'date': self.date,
             'players': [player.toDict() for player in self.scores],
             'tee': self.tee,
           }
  
  def getScorecard(self):
    """Scorecard with all players."""
    dct_scorecard = self.course.getScorecard()
    for n,score in enumerate(self.scores):
      dct = {'player': score.player }
      gross_line = '{:<6}'.format(score.player.nick_name)
      gross_out = 0
      gross_in = 0
      for gross in score.gross[:9]:
        gross_line += ' {:>3}'.format(gross)
        gross_out += gross
      gross_line += ' {:>4}'.format(gross_out)
      for gross in score.gross[9:]:
        gross_line += ' {:>3}'.format(gross)
        gross_in += gross
      gross_tot = gross_out + gross_in
      gross_line += ' {:>4} {:>4}'.format(gross_in, gross_tot)
      dct['gross_line'] = gross_line
      dct['gross_in'] = gross_in
      dct['gross_out'] = gross_out
      dct['gross_tot'] = gross_tot
      dct_scorecard['player_%d_gross' % n] = dct
      
    return dct_scorecard
  
  def __str__(self):
    return '{} - {:<25} - {:<25} - tee:{}'.format(
      self.date.date(), self.course.name, ','.join([score.player.nick_name for score in self.scores]),
      self.tee['name'] if self.tee else self.tee)
