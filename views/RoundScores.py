# coding: utf-8
"""app_main.py - golf app entry point."""
import console
import ui
import dialogs
import datetime 

from golf_db.db_sqlalchemy import Round,Score
from golf_view import GolfView

class PlayerForm:
  def __init__(self, result_id, txtGross, txtPutts):
    self.result_id = result_id
    self.txtGross = txtGross
    self.txtPutts = txtPutts
    self.txtGross.keyboard_type = ui.KEYBOARD_NUMBER_PAD
    self.txtPutts.keyboard_type = ui.KEYBOARD_NUMBER_PAD

class RoundScores(GolfView):
  def __init__(self):
    self._hole_num = 1
    self._dirty = False

  def did_load(self):
    self.name = "Update Scores"

    self.btnPrev = self['btnPrev']
    self.btnNext = self['btnNext']
    self.lblHole = self['lblHole']
    self.btnNext.action = self.next_hole
    self.btnPrev.action = self.prev_hole
    self.lblPlayers = []
    self.txtGross = []
    self.txtPutts = []
    for n in range(4):
      self.lblPlayers.append(self['lblPlayer{}'.format(n+1)])
      self.txtGross.append(self['txtGross{}'.format(n+1)])
      self.txtPutts.append(self['txtPutts{}'.format(n+1)])
    self.players = []

  def deactivate(self):
    print('{} deactivate()'.format(self.__class__.__name__))
    self._save()

  def activate(self):
    #print('{} activate()'.format(self.__class__.__name__))
    for n in range(4):
      self.lblPlayers[n].hidden = True
      self.txtGross[n].hidden = True
      self.txtPutts[n].hidden = True

    session = self.db.Session()
    self.golf_round = session.query(Round).filter(Round.round_id == self._mainView._round_id).one()
    self.players = []
    for n, result in enumerate(self.golf_round.results):
      self.lblPlayers[n].hidden = False
      self.txtGross[n].hidden = False
      self.txtPutts[n].hidden = False
      self.lblPlayers[n].text = result.player.getFullName()
      self.txtGross[n].action = self.set_gross
      self.txtPutts[n].action = self.set_putts
      self.players.append(PlayerForm(result.result_id, self.txtGross[n], self.txtPutts[n]))

    self._set_hole_number(self._hole_num)
    self._get(session)

  def _set_hole_number(self, hole_num):
    #print('{} _set_hole_num() hole_num:{}'.format(self.__class__.__name__, hole_num))
    hole_num = max(hole_num, 1)
    hole_num = min(hole_num, len(self.golf_round.course.holes)) 
    self.lblHole.text = 'Hole {} Par {} Hdcp {}'.format(hole_num,
                                                                    self.golf_round.course.holes[hole_num-1].par,
                    self.golf_round.course.holes[hole_num-1].handicap)
    self._hole_num = hole_num
    self.btnPrev.enabled = True
    self.btnNext.enabled = True
    if hole_num == 1:
      self.btnPrev.enabled = False
    elif hole_num == len(self.golf_round.course.holes):
      self.btnNext.enabled = False

  def _get(self, session):
    """Read values from database and set into form"""
    #print('{} _get() _hole_num:{}'.format(self.__class__.__name__, self._hole_num))
    for player in self.players:
      player.score = session.query(Score).filter(Score.result_id == player.result_id, Score.num == self._hole_num).first()
      if player.score:
        player.txtGross.text = str(player.score.gross)
        player.txtPutts.text = str(player.score.putts)
      else:
        player.txtGross.text = ''
        player.txtPutts.text = ''

  def _save(self, session=None):
    """Save the from values to the database."""
    print('{} _save() _hole_num:{}'.format(self.__class__.__name__, self._hole_num))
    if not session:
      session = self.db.Session()
    for player in self.players:
      try:
        gross = int(player.txtGross.text)
        putts = int(player.txtPutts.text)
      except Exception, ex:
        print('_save() error - {}'.format(ex))
        continue
      player.score = session.query(Score).filter(Score.result_id == player.result_id, Score.num == self._hole_num).first()
      if player.score:
        player.score.gross = gross
        player.score.putts = putts
      else:
        player.score = Score(result_id=player.result_id, gross=gross, putts=putts, num=self._hole_num)
        session.add(player.score)
    session.commit()
    # now validate scores
    lst_game_more_info_needed = []
    golf_round = session.query(Round).filter(Round.round_id == self._round_id).one()
    for game in golf_round.games:
      try:
        game.CreateGame()
      except GolfGameException, ex:
        print('{} Game - {} - {}'.format(ex.dct['game'].short_description, ex.dct['msg'], ','.join([pl.nick_name for pl in ex.dct['players']])))
        lst_game_more_info_needed.append(ex)
      
    if lst_game_more_info_needed:
      for ex in lst_game_more_info_needed:
        player_nick_names = [pl.nick_name for pl in ex.dct['players'])
        name = dialogs.list_dialog(ex.dct['msg'], player_nick_names)
        if name:
          game = session.query(Game).filter(Game.game_id == ex.dct['game'].game.game_id).one()
          game.add_hole_dict_data(ex.dct['hole_num'], {ex.dct['key'] : ex.dct['players'][i].nick_name})
          session.commit()

  def next_hole(self, sender):
    session = self.db.Session()
    self._save(session)
    self._set_hole_number(self._hole_num + 1)
    self._get(session)		

  def prev_hole(self, sender):
    session = self.db.Session()
    self._save(session)
    self._set_hole_number(self._hole_num - 1)
    self._get(session)

  def set_gross(self, sender):
    pass

  def set_putts(self, sender):
    pass


