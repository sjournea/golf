""" game_vegas.py - Vegas Golf Game class."""
from .game import GolfGame
from .exceptions import GolfException

class Team:
  MAX_HANDICAP = 18
  def __init__(self, name, players):
    self.name = name
    self.players = players[:]
    # calc handicap
    self.handicap = sum([pl.course_handicap for pl in self.players])
    self.total_bumps = 0

  def setup(self, course, min_handicap):
    print 'setup() - min_handicap:{}'.format(min_handicap)
    # calculate total bumps but limit to max allowed
    self.total_bumps = self.handicap - min_handicap
    self.total_bumps = min(self.total_bumps, self.MAX_HANDICAP)
    # apply bumps to course holes
    self.bumps = course.calcBumps(self.total_bumps)
    # initialize points
    self.score = [None for _ in range(len(course.holes))]
    self.points = [None for _ in range(len(course.holes))]
    self.points_in = 0
    self.points_out = 0
    self.points_total = 0

  def calculate_score(self, index):
    gross_scores = [player.gross[index] for player in self.players]
    # apply bump to lower score
    if self.bumps[index]:
      low_gross = min(gross_scores)
      for n,gross in enumerate(gross_scores):
        if gross == low_gross:
          gross_scores[n] -= 1
          break
    # calulate score - low score * 10 + high score
    low_index = 0 if gross_scores[0] < gross_scores[1] else 1
    self.score[index] = gross_scores[low_index]*10 + gross_scores[low_index ^ 1]

  def update_points(self, index, other_team):
    self.points[index] = self.score[index] - other_team.score[index]
    self.points_in = sum([pt for pt in self.points[9:] if pt is not None])
    self.points_out = sum([pt for pt in self.points[:9] if pt is not None])
    self.points_total = self.points_in + self.points_out
    
  def get_scorecard(self):
    """Scorecard for team."""
    dct = {'team': self.name }
    line = '{:<6}'.format(self.name)
    for i,score in enumerate(self.score[:9]):
      s = '*' if self.bumps[i] else ''
      s += '' if score is None else '{:d}'.format(score)
      line += ' {:>3}'.format(s)
    line += ' {:>4d}'.format(self.points_out)
    for i,score in enumerate(self.score[9:]):
      s = '*' if self.bumps[i+9] else ''
      s += '' if score is None else '{:d}'.format(score)
      line += ' {:>3}'.format(s)
    line += ' {:>4d} {:>4d}'.format(self.points_in, self.points_total)
    dct['line'] = line
    dct['in'] = self.points_in
    dct['out'] = self.points_out
    dct['total'] = self.points_total
    return dct

  def __str__(self):
    return '{} - points_total:{} handicap:{} total_bumps:{} bumps:{}'.format(self.name, self.points_total, self.handicap, self.total_bumps, self.bumps)


class VegasGame(GolfGame):
  """The Vegas golf game."""
  def __init__(self, golf_round, scores, **kwargs):
    self.teams = kwargs.get('teams', ((0,1),(2,3)))
    super(VegasGame, self).__init__(golf_round, scores, **kwargs)

  def validate(self):
    if len(self.scores) != 4:
      raise GolfException('Vegas game must have 4 players, {} found.'.format(len(self.scores)))
    if len(self.teams) != 2:
      raise GolfException('2 teams of 2 players must be set.')
    lst = [0 for n in range(4)]
    for team in self.teams:
      if len(team) != 2:
        raise GolfException('Teams must have 2 players.')
      lst[team[0]] += 1 
      lst[team[1]] += 1
    for cnt in lst:
      if cnt != 1:
        raise GolfException('Malformed team.')

  def start(self):
    # create teams
    self.team_list = [Team('Team{}'.format(n+1), [self.scores[i1], self.scores[i2]]) for n,(i1,i2) in enumerate(self.teams)]
    # calculate min handicap from team handicaps
    min_handicap = min([team.handicap for team in self.team_list])
    # setup players - initialize all bumps to 0    
    for player in self.scores:
      player.gross = [None for _ in range(len(self.golf_round.course.holes))]
    # setup teams
    for team in self.team_list:
      team.setup(self.golf_round.course, min_handicap)
    # setup responses 
    self.dctScorecard['header'] = '{0:*^93}'.format(' Vegas ')
    self.dctLeaderboard['hdr'] = 'Pos Name   Points Thru'

    for team in self.team_list:
      print team
      
  def addScore(self, index, lstGross):
    """add scores for a hole."""
    # update gross score for hole
    for player, gross in zip(self.scores, lstGross):
      player.gross[index] = gross
    # update team score
    for team in self.team_list:
      team.calculate_score(index)
    # update team points using other team score
    self.team_list[0].update_points(index, self.team_list[1])  
    self.team_list[1].update_points(index, self.team_list[0])  

  def getScorecard(self, **kwargs):
    """Scorecard with all players."""
    self.dctScorecard['players'] = [team.get_scorecard() for team in self.team_list]
    return self.dctScorecard
  
  def getLeaderboard(self, **kwargs):
    board = []
    teams = sorted(self.team_list, key=lambda team: team.points_total)
    pos = 1
    prev_total = None
    for team in teams:
      score_dct = {
        'team': team,
        'total' : team.points_total,
      }
      if prev_total != None and score_dct['total'] > prev_total:
        pos += 1

      prev_total = score_dct['total']
      score_dct['pos'] = pos
      for n,score in enumerate(team.score):
        if score is None:
          break
      else:
        n += 1
      score_dct['thru'] = n
      score_dct['line'] = '{:<3} {:<6} {:>5} {:>4}'.format(
        score_dct['pos'], score_dct['team'].name, score_dct['total'], score_dct['thru'])
      board.append(score_dct)
    self.dctLeaderboard['leaderboard'] = board
    return self.dctLeaderboard

  def getStatus(self, **kwargs):
    for n,score in enumerate(self.team_list[0].score):
      if score is None:
        self.dctStatus['next_hole'] = n+1
        self.dctStatus['par'] = self.golf_round.course.holes[n].par
        self.dctStatus['handicap'] = self.golf_round.course.holes[n].handicap
        bumps = []
        bump_line = []
        for team in self.team_list:
          if team.bumps[n] > 0:
            dct = {'team': team, 'bumps': team.bumps[n]}
            bumps.append(dct)
            bump_line.append('{}{}'.format(team.name, '({})'.format(dct['bumps']) if dct['bumps'] > 1 else ''))
        self.dctStatus['bumps'] = bumps
        self.dctStatus['line'] = 'Hole {} Par {} Hdcp {}'.format(
          self.dctStatus['next_hole'], self.dctStatus['par'], self.dctStatus['handicap'])
        if bumps:
          self.dctStatus['line'] += ' Bumps:{}'.format(','.join(bump_line))
        break
    else:
      # round complete
      self.dctStatus['next_hole'] = None
      self.dctStatus['par'] = self.golf_round.course.total
      self.dctStatus['handicap'] = None
      self.dctStatus['line'] = 'Round Complete'
    return self.dctStatus
