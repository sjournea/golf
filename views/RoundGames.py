# coding: utf-8
"""app_main.py - golf app entry point."""
import console
import ui
import dialogs
import datetime 

from golf_db.db_sqlalchemy import Round

class RoundGames(ui.View):
	def __init__(self):
		pass

	def did_load(self):
		self.name = "Setup Games"
		
		self.btnAddGame = self['btnAddGame']
		self.btnPlay = self['btnPlay']
		self.tblGames = self['tblGames']
				
		self.btnAddGame.action = self.add_game
		self.btnPlay.action = self.play
		
	def activate(self):
		pass
		
	def add_game(self, sender):
		# for now hard wire adding Gross and Net
		round_id = self._mainView._round_id
		print 'round_id:{}'.format(round_id)
		session = self.db.Session()
		golf_round = session.query(Round).filter(Round.round_id == round_id).one()
		dct = {}
		golf_round.addGame(session, 'gross', dct)
		golf_round.addGame(session, 'net', dct)
		session.commit()
	
	def play(self, sender):
		self._mainView.goto_leaderboard()

