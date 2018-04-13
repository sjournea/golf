# coding: utf-8
"""RoundGames.py - view for setting/editing golf games."""
import ast
import console
import ui
import dialogs
import datetime 

from golf_db.db_sqlalchemy import Round,Game
from golf_db.sql_game_factory import SqlGolfGameList, SqlGolfGameFactory, SqlGolfGameOptions
from golf_view import GolfView

def options_dialog(view, game_class):
	def get_type(key, option):
		if option['type'] == 'bool':
			datatype = 'switch'
			value = option['value']
		elif option['type'] in ('tuple[2]', 'tuple[2][2]'):
			datatype = 'text'
			value = str(option['value'])				
		elif option['type'] in ('float', 'int'):
			datatype = 'number'			
			value = str(option['value'])
		else:
			datatype = 'text'
			value = str(option['value'])
		return datatype, value
	
	title = '{} options'.format(game_class.short_description)
	fields = []
	for key, option in game_class.game_options.items():
		data_type, value = get_type(key, option)
		dct = {
			'title': key,
			'type': data_type,
			'key': key,
			'value': value,
		}
		fields.append(dct)
	return title, fields
	
@ui.in_background
def do_dialog_background(title, fields):
	dct = dialogs.form_dialog(title=title, fields=fields)
	print('dct:{}'.format(dct))
	return dct

def do_dialog(title, fields):
	dct = dialogs.form_dialog(title=title, fields=fields)
	print('dct:{}'.format(dct))
	return dct
	
class GamesViewDataSource(object):
	def __init__(self, view):
		self.view = view
		self.games = view.games
		self.db = view.db

	def tableview_number_of_sections(self, tableview):
		# Return the number of sections (defaults to 1)
		print('tableview_number_of_sections()')
		return 1

	def tableview_number_of_rows(self, tableview, section):
		print('tableview_number_of_rows() section:{}'.format(section))
		# Return the number of rows in the section
		return len(self.games) 

	def tableview_cell_for_row(self, tableview, section, row):
		# Create and return a cell for the given section/row
		print('tableview_cell_for_row() section:{} row:{}'.format(section, row))
		cell = ui.TableViewCell()
		cell.text_label.text = self.games[row].short_description
		cell.accessory_type = 'disclosure_indicator' if self.games[row].game_options else 'none'
		return cell

	#def tableview_title_for_header(self, tableview, section):
		# Return a title for the given section.
		# If this is not implemented, no section headers will be shown.
		#return 'Some Section'

	def tableview_can_delete(self, tableview, section, row):
		# Return True if the user should be able to delete the given row.
		print('tableview_can_delete() section:{} row:{}'.format(section, row))
		return True

	def tableview_can_move(self, tableview, section, row):
		# Return True if a reordering control should be shown for the given row (in editing mode).
		print('tableview_can_move() section:{} row:{}'.format(section, row))
		return False

	def tableview_delete(self, tableview, section, row):
		# Called when the user confirms deletion of the given row.
		print('tableview_delete() section:{} row:{}'.format(section, row))

	#def tableview_move_row(self, tableview, from_section, from_row, to_section, to_row):
		# Called when the user moves a row with the reordering control (in editing mode).
		#print('tableview_move_row() tableview:{} from_section:{} from_row:{} to_section:{} to_row:{}'.format(tableview, from_section, from_row, #to_section, to_row))

	def tableview_did_select(self, tableview, section, row):
		# Called when a row was selected.
		print('tableview_did_select() section:{} row:{}'.format(section, row))
		if self.games[row].game_options:
			title, fields = options_dialog(self, self.games[row])
			do_dialog_background(title, fields)
			#if dct:
				#session = self.db.Session()
				#game = session.query(Game).filter(Game.game_id == game.game.game_id).one()
				#dct_data = rec.game_data
				#dct_data['options'] = dct
				#rec.game_data = dct_data
				#session.commit()
	
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
		lds = GamesViewDataSource(self)
		self.tvGames.data_source = lds
		self.tvGames.delegate = lds
		self.tvGames.editing = False
		self.tvGames.reload_data()

	def activate(self):
		"""Form activated. Load all defined games into tblGames."""
		print('{} - activate()'.format(self.__class__.__name__))
		self._update_games()

	def deactivate(self):
		print('{} - deactivate()'.format(self.__class__.__name__))
		
	def game_options(self, sender):
		print('game_options')

	def add_game(self, sender):
		# for now hard wire adding Gross and Net
		game_names = SqlGolfGameList()
		name = dialogs.list_dialog('Select Game', game_names)
		if name:
			game_class = SqlGolfGameFactory(name)
			if game_class.game_options:
				for dct in game_class.game_options.values():
					dct['value'] = dct['default']
				title, fields = options_dialog(self, game_class)
				dct = do_dialog(title, fields)
			else:
				dct = {}	
			round_id = self._mainView._round_id
			print 'round_id:{} dct:{}'.format(round_id, dct)
			session = self.db.Session()
			golf_round = session.query(Round).filter(Round.round_id == round_id).one()
			golf_round.addGame(session, name, dct)
			session.commit()
			self._update_games()
