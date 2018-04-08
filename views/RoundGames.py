# coding: utf-8
"""app_main.py - golf app entry point."""
import console
import ui
import dialogs
import datetime 

from golf_db.db_sqlalchemy import Round
from golf_db.sql_game_factory import SqlGolfGameList, SqlGolfGameFactory, SqlGolfGameOptions
from golf_view import GolfView

class GameDataSource(object):
	pass

class GamesViewDelegate(object):
	def tableview_did_select(self, tableview, section, row):
		# Called when a row was selected.
		print('tableview_did_select() section:{} row:{}'.format(section, row))

	def tableview_did_deselect(self, tableview, section, row):
		# Called when a row was de-selected (in multiple selection mode).
		pass

	def tableview_title_for_delete_button(self, tableview, section, row):
		# Return the title for the 'swipe-to-***' button.
		return 'Remove'

class RoundGames(GolfView):
	def __init__(self):
		pass

	def did_load(self):
		self.name = "Setup Games"
		
		self.btnAddGame = self['btnAddGame']
		self.tvGames = self['tvGames']
				
		self.btnAddGame.action = self.add_game
		
	def _update_games(self):
		"""Load all defined games into tvGames."""
		session = self.db.Session()
		self.golf_round = session.query(Round).filter(Round.round_id == self._mainView._round_id).one()	
		self.games = [game.CreateGame() for game in self.golf_round.games]
		items = []
		for game in self.games:
			dct = {'title': game.short_description}
			if game.game_options:
				dct['accessory_type'] = 'detail_button'
			items.append(dct)	
		lds = ui.ListDataSource(items=items)
		lds.accessory_action = self.game_options
		self.tvGames.data_source = lds
		self.tvGames.delegate = GamesViewDelegate()
		self.tvGames.editing = False
		self.tvGames.reload_data()

	def activate(self):
		"""Form activated. Load all defined games into tblGames."""
		self._update_games()

	def deactivate(self):
		pass
		
	def game_options(self, sender):
		print('game_options')

	def add_game(self, sender):
		# for now hard wire adding Gross and Net
		game_names = SqlGolfGameList()
		name = dialogs.list_dialog('Select Game', game_names)
		if name:
			options = SqlGolfGameOptions(name)
			round_id = self._mainView._round_id
			print 'round_id:{} options:{}'.format(round_id, options)
			session = self.db.Session()
			golf_round = session.query(Round).filter(Round.round_id == round_id).one()
			dct = {}
			golf_round.addGame(session, name, dct)
			session.commit()
			self._update_games()

