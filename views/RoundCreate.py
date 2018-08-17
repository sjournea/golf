# coding: utf-8
"""app_main.py - golf app entry point."""
import console
import ui
import dialogs
import datetime 

from golf_db.db_sqlalchemy import Database, Round, Course, Player, Result
from golf_view import GolfView

class RoundCreate(GolfView):
  def __init__(self):
    pass

  def did_load(self):
    self.name = "Let's Play Golf"

    self.btnSelectDate = self['btnSelectDate']
    self.btnSelectCourse = self['btnSelectCourse']
    self.btnSelectTee = self['btnSelectTee']
    self.btnPlayers = [self['btnPlayer{}'.format(n+1)] for n in range(4)]
    self.btnStartRound = self['btnStartRound']

    self.btnSelectDate.action = self.select_date
    self._date_played = datetime.datetime.now()
    self.btnSelectDate.title = self._date_played.strftime('%A %B %d, %Y')

    self.btnSelectCourse.action = self.select_course
    self._course = None
    self.btnSelectTee.action = self.select_tee
    self.btnSelectTee.enabled = False
    self._tee = None

    for player in self.btnPlayers:
      player.action = self.add_player
      player._player = None

    self.btnStartRound.action = self.start_round

  def select_date(self, sender):
    date_played = dialogs.date_dialog()
    if date_played:
      sender.title = date_played.strftime('%A %B %d, %Y')
      self._date_played = date_played

  def add_player(self, sender):
    session = self.db.Session()
    players = session.query(Player).all()
    names = sorted([player.getFullName() for player in players])
    names += ['<Remove Player>']
    name = dialogs.list_dialog('Select Player', names)
    if name:
      if name == '<Remove Player>':
        sender.title = '<Add Player>'
        sender._player = None
      else:
        sender.title = name
        sender._player = [player for player in players if name == player.getFullName()][0]

  def select_course(self, sender):
    session = self.db.Session()
    courses = session.query(Course).all()
    course_names = sorted([course.name for course in courses])
    name = dialogs.list_dialog('Select Course', course_names)
    if name:
      sender.title = name
      self._course = [course for course in courses if name == course.name][0]
      self._tee = None
      self['btnSelectTee'].title = '<Select Tee>'			
      self['btnSelectTee'].enabled = True

  def select_tee(self, sender):
    if not self._course:
      return
    tees = [tee for tee in self._course.tees if tee.gender == 'mens']
    names = [tee.name for tee in tees]
    name = dialogs.list_dialog('Select Tee', names)
    if name:
      sender.title = name
      self._tee = [tee for tee in tees if name == tee.name][0]

  @ui.in_background
  def console_alert(self, msg):
    console.alert(msg)

  def start_round(self, sender):
    lst_errors = []
    if self._date_played is None:
      lst_errors.append('Date played must be set.')
    if self._course is None:
      lst_errors.append('Course must be selected.')
    if self._tee is None:
      lst_errors.append('Tee must be selected.')
    for player in self.btnPlayers:
      if player._player is not None:
        break
    else:
      lst_errors.append('At least one player must be selected.')
    if lst_errors:
      self.console_alert('\n'.join(lst_errors))
      return
    # Start the round
    session = self.db.Session()
    golf_round = Round(course_id=self._course.course_id, date_played=self._date_played)
    session.add(golf_round)
    session.commit()
    # HARDWIRED to simple
    # golf_round.set_option('calc_course_handicap', 'simple')
    session.commit()
    # add players
    for pl in self.btnPlayers:
      if pl._player is not None:
        result = Result(round=golf_round, player_id=pl._player.player_id, tee_id=self._tee.tee_id, handicap=pl._player.handicap)
        result.calcCourseHandicap(self._tee)
        session.add(result)
    session.commit()
    # switch back to main view
    self._mainView.set_golf_round(golf_round)
    self._mainView.goto_games()

