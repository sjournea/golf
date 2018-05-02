# coding: utf-8
"""app_main.py - golf app entry point."""
import console
import ui
import dialogs
import datetime 

from golf_db.db_sqlalchemy import Round
from .golf_view import GolfView

class RoundScorecard(GolfView):
  def __init__(self):
    self._controls = []
    self._display_front = True

  def did_load(self):
    self.name = "Scorecard"
    self.segGames = self['segGames']
    self.segGames.action = self.select_game
    self.segGames.selected_index = 0

    height = self.height * 0.12
    widthPos = self.width*0.08
    width = 60
    lbl = ui.Label(text='Hole', alignment=ui.ALIGN_LEFT, center=(widthPos, height), font=('<system>', 20), width=width)
    self.add_subview(lbl)
    height += self.height*0.040
    lbl = ui.Label(text='Par', alignment=ui.ALIGN_LEFT, center=(widthPos, height), font=('<system>', 20), width=width)
    self.add_subview(lbl)
    height += self.height*0.040
    lbl = ui.Label(text='Hdcp', alignment=ui.ALIGN_LEFT, center=(widthPos, height), font=('<system>', 20), width=width)
    self.add_subview(lbl)
    # add player name labels
    self.lstPlayerLabels = []
    for n in range(4):
      height += self.height*0.040
      lbl = ui.Label(text='P{}'.format(n+1), alignment=ui.ALIGN_LEFT, center=(widthPos, height), font=('<system>', 20), width=width)
      self.lstPlayerLabels.append(lbl)
      self.add_subview(lbl)
    width = 50
    # create ScrollView
    self.cardView = ui.ScrollView(x=self.width*0.15, y=self.height*0.10, width=self.width*0.85, height=self.height*0.30)
    # content width is double wide! with the same width it won't scroll.
    self.cardView.content_size = (2.2*self.width, self.height*0.30)
    self.cardView.directional_lock_enabled = True
    lstHoles = [str(hole) for hole in range(1,10)] + ['Out'] + [str(hole) for hole in range(10,19)] + ['In', 'Total', 'ESC']
    lstWidths = 22*[50]
    widthOffsets = [n*self.width*0.09 + 20 for n in range(22)]
    height = 13
    for widthPos,text,width in zip(widthOffsets, lstHoles, lstWidths):
      #print 'widthPos:{} text:{} width:{}'.format(widthPos, text, width)
      font = '<system-bold>' if text in ('In', 'Out', 'Total', 'ESC') else '<system>'
      lbl = ui.Label(text=text, alignment=ui.ALIGN_RIGHT, center=(widthPos, height), font=(font, 20), width=width)
      self.cardView.add_subview(lbl)
    self.dctPars = {}
    height += self.height*0.04
    for widthPos,text,width in zip(widthOffsets, lstHoles, lstWidths):
      #print 'widthPos:{} text:{} width:{}'.format(widthPos, text, width)
      font = '<system-bold>' if text in ('In', 'Out', 'Total') else '<system>'
      lbl = ui.Label(text='', alignment=ui.ALIGN_RIGHT, center=(widthPos, height), font=(font, 20), width=width)
      self.dctPars[text] = lbl
      self.cardView.add_subview(lbl)
    self.dctHdcps = {}
    height += self.height*0.04
    for widthPos,text,width in zip(widthOffsets, lstHoles, lstWidths):
      #print 'widthPos:{} text:{} width:{}'.format(widthPos, text, width)
      lbl = ui.Label(text='', alignment=ui.ALIGN_RIGHT, center=(widthPos, height), font=('<system>', 20), width=width)
      self.dctHdcps[text] = lbl
      self.cardView.add_subview(lbl)
    self.lstPlayers = []
    for n in range(4):
      dct = {}
      height += self.height*0.04
      for widthPos,text,width in zip(widthOffsets, lstHoles, lstWidths):
        #print 'widthPos:{} text:{} width:{}'.format(widthPos, text, width)
        font = '<system-bold>' if text in ('In', 'Out', 'Total', 'ESC') else '<system>'
        lbl = ui.Label(text='', alignment=ui.ALIGN_RIGHT, center=(widthPos, height), font=(font, 20), width=width)
        dct[text] = lbl
        self.cardView.add_subview(lbl)
      self.lstPlayers.append(dct)
    self.add_subview(self.cardView)

  def _update_course_controls(self):
    """Build controls for course display."""
    course = self.golf_round.course
    course.setStats()
    for hole in course.holes:
      hole_num = str(hole.num)
      self.dctPars[hole_num].text = str(hole.par)
      self.dctHdcps[hole_num].text = str(hole.handicap)
    self.dctPars['In'].text = str(course.in_tot)
    self.dctPars['Out'].text = str(course.out_tot)
    self.dctPars['Total'].text = str(course.total)

  def _update_controls(self):
    """Add controls to view."""
    if self.game.game.game_type in ('gross', 'net', 'putts', 'stableford', 'greenie', 'snake', 'skins'): 
      for n in range(4):
        dctLabels = self.lstPlayers[n]
        if n < len(self.dctScorecard['players']): 
          hidden = False
          dct = self.dctScorecard['players'][n]
          self.lstPlayerLabels[n].text = dct['player'].getInitials()
          self.lstPlayerLabels[n].hidden = False
          for n,value in enumerate(dct['holes']):
            dctLabels[str(n+1)].text = str(value) if value is not None else ''
          dctLabels['In'].text = str(dct['in'])
          dctLabels['Out'].text = str(dct['out'])
          dctLabels['Total'].text = str(dct['total'])
          dctLabels['ESC'].text = str(dct['esc']) if 'esc' in dct else ''
        else:
          self.lstPlayerLabels[n].hidden = True
          hidden = True
        for lbl in dctLabels.values():
          lbl.hidden = hidden
    elif self.game.game.game_type in ('bestball'):
      for n in range(4):
        dctLabels = self.lstPlayers[n]
        if n < len(self.dctScorecard['players']): 
          hidden = False
          dct = self.dctScorecard['players'][n]
          self.lstPlayerLabels[n].text = dct['team']
          self.lstPlayerLabels[n].hidden = False
          for n,value in enumerate(dct['holes']):
            dctLabels[str(n+1)].text = str(value) if value is not None else ''
          dctLabels['In'].text = str(dct['in'])
          dctLabels['Out'].text = str(dct['out'])
          dctLabels['Total'].text = str(dct['total'])
        else:
          self.lstPlayerLabels[n].hidden = True
          hidden = True
        for lbl in dctLabels.values():
          lbl.hidden = hidden

  def activate(self):
    session = self.db.Session()
    self.golf_round = session.query(Round).filter(Round.round_id == self._mainView._round_id).one()	
    self.segGames.segments = [game.game_type for game in self.golf_round.games]
    self.games = [game.CreateGame() for game in self.golf_round.games]
    self.segGames.selected_index = 0
    self._update_course_controls()
    self.select_game(None)

  def select_game(self, sender):
    self.game = self.games[self.segGames.selected_index]
    self.dctScorecard = self.game.getScorecard()
    self._update_controls()


