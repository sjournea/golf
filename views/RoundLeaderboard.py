# coding: utf-8
"""app_main.py - golf app entry point."""
import console
import ui
import dialogs
import datetime 

from golf_db.db_sqlalchemy import Round
from .golf_view import GolfView

class RoundLeaderboard(GolfView):
	def __init__(self):
		self._controls = []

	def did_load(self):
		self.name = "Leaderboard"
		self.segGames = self['segGames']
		self.segGames.action = self.select_game
		self.segGames.selected_index = 0
	
	def _add_control(self, control):
		"""Add the control as a sub view and add to controls list."""
		self.add_subview(control)
		self._controls.append(control)
	
	def _remove_all_controls(self):
		"""Remove all controls in the controls list."""
		for control in self._controls:
			self.remove_subview(control)
		self._controls = []
		
	def _update_controls(self):
		"""Add controls to view."""
		self._remove_all_controls()
		hdrHeight = self.height * 0.11
		if self.game.game.game_type in ('gross', 'net', 'putts', 'stableford', 'greenie', 'snake'): 
			# header
			alignments = [ui.ALIGN_RIGHT, ui.ALIGN_CENTER, ui.ALIGN_RIGHT, ui.ALIGN_RIGHT]
			widthPositions = [self.width * 0.1, self.width * 0.3, self.width * 0.6,self.width * 0.8]
			widths = [60, 150, 60, 60]
			headers = self.dctLeaderboard['hdr'].split()
			for widthPos,hdr,alignment,width in zip(widthPositions, headers, alignments, widths):
				lblHdr = ui.Label(text=hdr, alignment=alignment, center=(widthPos, hdrHeight), font=('<system-bold>', 20), width=width)
				self._add_control(lblHdr)
			# players
			playerHeights = [hdrHeight*(n+2) for n in range(len(self.dctLeaderboard['leaderboard']))]
			keys = ['pos', 'player', 'total', 'thru']
			alignments = [ui.ALIGN_RIGHT, ui.ALIGN_LEFT, ui.ALIGN_RIGHT, ui.ALIGN_RIGHT]
			for n,dct in enumerate(self.dctLeaderboard['leaderboard']):
				playerHeight = (n+1)*self.height*0.05 + hdrHeight
				for widthPos,key,alignment,width in zip(widthPositions, keys, alignments, widths):
					text = dct['player'].getFullName() if key == 'player' else str(dct[key])
					lbl = ui.Label(text=text, alignment=alignment, center=(widthPos, playerHeight), width=width)
					self._add_control(lbl)			
		elif self.game.game.game_type in ('bestball'):
			# header
			alignments = [ui.ALIGN_LEFT, ui.ALIGN_CENTER, ui.ALIGN_CENTER]
			widthPositions = [self.width*0.2, self.width*0.5, self.width*0.8]
			headers = ['Team', 'Status', 'Thru']
			widths = [150, 60, 60]
			for widthPos,hdr,alignment,width in zip(widthPositions, headers, alignments, widths):
				lblHdr = ui.Label(text=hdr, alignment=alignment, center=(widthPos, hdrHeight), font=('<system-bold>', 20), width=width)
				self._add_control(lblHdr)
			# players
			playerHeights = [hdrHeight*(n+2) for n in range(len(self.dctLeaderboard['leaderboard']))]
			keys = ['team', 'status', 'thru']
			alignments = [ui.ALIGN_LEFT, ui.ALIGN_CENTER, ui.ALIGN_CENTER]
			for n,dct in enumerate(self.dctLeaderboard['leaderboard']):
				playerHeight = (n+1)*self.height*0.05 + hdrHeight
				for widthPos,key,alignment, width in zip(widthPositions, keys, alignments, widths):
					text = None
					if key == 'thru' and n == 0:
						text = str(self.dctLeaderboard['thru'])
					elif key == 'team':
						text = dct['team'].name
					elif key == 'status':
						if dct['team']._total > 0 or (dct['team']._total == 0 and n == 0):
							text = dct['status']
					if text:
						lbl = ui.Label(text=text, alignment=alignment, center=(widthPos, playerHeight), width=width)
						self._add_control(lbl)						
	
	def activate(self):
		session = self.db.Session()
		self.golf_round = session.query(Round).filter(Round.round_id == self._mainView._round_id).one()	
		self.segGames.segments = [game.game_type for game in self.golf_round.games]
		self.games = [game.CreateGame() for game in self.golf_round.games]
		self.segGames.selected_index = 0
		self.select_game(None)
			
	def select_game(self, sender):
		self.game = self.games[self.segGames.selected_index]
		self.dctLeaderboard = self.game.getLeaderboard()
		self._update_controls()
	

