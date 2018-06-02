# coding: utf-8
"""app_main.py - golf app entry point."""
import console
import ui
import dialogs
import datetime 

from golf_db.db_sqlalchemy import Round,Score,Game
from golf_db.exceptions import GolfGameException
from golf_view import GolfView

class PlayerForm:
    def __init__(self, result_id, btnGross, btnPutts):
        self.result_id = result_id
        self.btnGross = btnGross
        self.btnPutts = btnPutts

MAX_PLAYERS = 4

class RoundScores(GolfView):
    def __init__(self):
        self._hole_num = 1
        self._dirty = False
        self.golf_round = None

    def did_load(self):
        self.name = "Update Scores"
        self.players = []

        self.btnPrev = ui.Button(title='Prev')
        self.btnPrev.center = (self.width * 0.1, self.height * 0.05)
        self.btnPrev.flex = 'LRTB'
        self.btnPrev.action = self.prev_hole
        self.add_subview(self.btnPrev)

        self.lblHole = ui.Label(text='Hole Desc', center=(self.width * 0.5, self.height * 0.05), width=self.width*0.4)
        self.add_subview(self.lblHole)

        self.btnNext = ui.Button(title='Next')
        self.btnNext.center = (self.width * 0.9, self.height * 0.05)
        self.btnNext.flex = 'LRTB'
        self.btnNext.action = self.next_hole
        self.add_subview(self.btnNext)

        self.lblPlayers = []
        self.btnGross = []
        self.btnPutts = []
        height = self.height * 0.15
        for n in range(MAX_PLAYERS):
            lbl = ui.Label(text='Player {}'.format(n+1), center=(self.width*0.25, height), width=self.width*0.4)
            height += self.height*0.05
            self.add_subview(lbl)
            self.lblPlayers.append(lbl)

            btnGross = ui.Button(title='<not set>')
            btnGross.center = (self.width * 0.5, height)
            btnGross.flex = 'LRTB'
            btnGross.action = self.set_gross
            self.add_subview(btnGross)
            self.btnGross.append(btnGross)

            btnPutts = ui.Button(title='<not set>')
            btnPutts.center = (self.width * 0.7, height)
            btnPutts.flex = 'LRTB'
            btnPutts.action = self.set_putts
            self.add_subview(btnPutts)
            self.btnPutts.append(btnPutts)

        # add the label for hole status updates
        height += self.height*0.05
        self.lblStatus = ui.Label(text='Game Status', center=(self.width*0.25, height), width=self.width*0.4)
        self.add_subview(lbl)

    def deactivate(self):
        print('{} deactivate()'.format(self.__class__.__name__))
        if self.golf_round:
            self._save()

    def activate(self):
        #print('{} activate()'.format(self.__class__.__name__))
        for n in range(MAX_PLAYERS):
            self.lblPlayers[n].hidden = True
            self.btnGross[n].hidden = True
            self.btnPutts[n].hidden = True

        session = self.db.Session()
        self.golf_round = session.query(Round).filter(Round.round_id == self._mainView._round_id).one()
        self.players = []
        for n, result in enumerate(self.golf_round.results):
            self.lblPlayers[n].hidden = False
            self.btnGross[n].hidden = False
            self.btnPutts[n].hidden = False
            self.lblPlayers[n].text = result.player.getFullName()
            self.players.append(PlayerForm(result.result_id, self.btnGross[n], self.btnPutts[n]))

        self._set_hole_number(self._hole_num)
        self._get(session)

    def _set_hole_number(self, hole_num):
        #print('{} _set_hole_num() hole_num:{}'.format(self.__class__.__name__, hole_num))
        hole_num = max(hole_num, 1)
        hole_num = min(hole_num, len(self.golf_round.course.holes)) 
        self._current_hole = self.golf_round.course.holes[hole_num-1]
        self.lblHole.text = 'Hole {} Par {} Hdcp {}'.format(
                    hole_num, self.golf_round.course.holes[hole_num-1].par,
                        self.golf_round.course.holes[hole_num-1].handicap)
        self._hole_num = hole_num
        self.btnPrev.enabled = hole_num > 1
        self.btnNext.enabled = hole_num < len(self.golf_round.course.holes)

    def _get(self, session):
        """Read values from database and set into form"""
        print('{} _get() _hole_num:{}'.format(self.__class__.__name__, self._hole_num))
        for player in self.players:
            score = session.query(Score).filter(Score.result_id == player.result_id, Score.num == self._hole_num).first()
            #print('_get() score:{}'.format(score))
            if score:
                #print('_get() score.gross:{}'.format(score.gross))
                player.btnGross.title = str(score.gross)
                player.btnPutts.title = str(score.putts)
            else:
                player.btnGross.title = '<not set>'
                player.btnPutts.title = '<not set>'
        # get all game status
        all_game_status = ''
        golf_round = session.query(Round).filter(Round.round_id == self._mainView._round_id).one()
        for game in golf_round.games:
            try:
                game.CreateGame()
                all_game_status += game.getStatus() + '\n'
            except GolfGameException, ex:
                print('{} Game - {} - {}'.format(ex.dct['game'].short_description, ex.dct['msg'], ','.join([pl.nick_name for pl in ex.dct['players']])))
        self.lblStatus = all_game_status

    def _save(self, session=None):
        """Save the from values to the database."""
        print('{} _save() _hole_num:{}'.format(self.__class__.__name__, self._hole_num))
        if not session:
            session = self.db.Session()
        for player in self.players:
            try:
                gross = int(player.btnGross.title)
                putts = int(player.btnPutts.title)
            except Exception, ex:
                print('_save() error - {}'.format(ex))
                continue
            score = session.query(Score).filter(Score.result_id == player.result_id, Score.num == self._hole_num).first()
            if score:
                score.gross = gross
                score.putts = putts
            else:
                score = Score(result_id=player.result_id, gross=gross, putts=putts, num=self._hole_num)
                session.add(score)
        session.commit()
        # now validate scores
        lst_game_more_info_needed = []
        golf_round = session.query(Round).filter(Round.round_id == self._mainView._round_id).one()
        for game in golf_round.games:
            try:
                game.CreateGame()
            except GolfGameException, ex:
                print('{} Game - {} - {}'.format(ex.dct['game'].short_description, ex.dct['msg'], ','.join([pl.nick_name for pl in ex.dct['players']])))
                lst_game_more_info_needed.append(ex)

        if lst_game_more_info_needed:
            for ex in lst_game_more_info_needed:
                player_nick_names = [pl.nick_name for pl in ex.dct['players']]
                name = dialogs.list_dialog(ex.dct['msg'], player_nick_names)
                if name:
                    game = session.query(Game).filter(Game.game_id == ex.dct['game'].game.game_id).one()
                    game.add_hole_dict_data(ex.dct['hole_num'], {ex.dct['key'] : name})
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
        par_3_scores = [
            '1 - Ace',
            '2 - Birdie',
            '3 - Par',
            '4 - Bogey',
            '5 - Double Bogey',
            '6 - Triple Bogey',
            '7 - Quadruple Bogey',
        ]
        par_4_scores = [
            '1 - Ace',
            '2 - Eagle',
            '3 - Birdie',
            '4 - Par',
            '5 - Bogey',
            '6 - Double Bogey',
            '7 - Triple Bogey',
            '8 - Quadruple Bogey',
        ]	
        par_5_scores = [
            '1 - Ace',
            '2 - Double Eagle',
            '3 - Eagle',
            '4 - Birdie',
            '5 - Par',
            '6 - Bogey',
            '7 - Double Bogey',
            '8 - Triple Bogey',
            '9 - Quadruple Bogey',
        ]
        par_6_scores = [
            '1 - Ace',
            '2 - Triple Eagle',
            '3 - Double Eagle',
            '4 - Eagle',
            '5 - Birdie',
            '6 - Par',
            '7 - Bogey',
            '8 - Double Bogey',
            '9 - Triple Bogey',
            '10 - Quadruple Bogey',
        ]
        dct_scores = {
            3: par_3_scores + ['{}'.format(n) for n in range(8,21)],
            4: par_4_scores + ['{}'.format(n) for n in range(9,21)],
            5: par_5_scores + ['{}'.format(n) for n in range(10,21)],		
            6: par_6_scores + ['{}'.format(n) for n in range(11,21)],		
        }
        title = 'Hole {} Par {} - Gross'.format(self._current_hole.num, self._current_hole.par)
        gross = dialogs.list_dialog(title, dct_scores[self._current_hole.par])
        if gross:
            sender.title = gross.split()[0]

    def set_putts(self, sender):
        putt_scores = [str(n) for n in range(11)]
        title = 'Hole {} Par {} - Putts'.format(self._current_hole.num, self._current_hole.par)
        putts = dialogs.list_dialog(title, putt_scores)
        if putts:
            sender.title = putts
