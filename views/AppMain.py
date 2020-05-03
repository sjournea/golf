# coding: utf-8
"""AppMain.py - golf app entry point view."""
import console
import ui
import dialogs
import datetime
from golf_db.db_sqlalchemy import Round
from RoundCreate import RoundCreate
from RoundGames import RoundGames
from RoundScores import RoundScores
from RoundLeaderboard import RoundLeaderboard
from RoundScorecard import RoundScorecard


def make_button_item(action, image_name=None, title=None):
    if image_name:
        return ui.ButtonItem(action=action, image=ui.Image.named(image_name))
    if title:
        return ui.ButtonItem(action=action, title=title)
    raise Exception("make_button_item() fail - title or image_name must be set.")


class MainView(ui.View):
    def __init__(self):
        self._round_id = None

    def set_golf_round(self, golf_round):
        self._round_id = golf_round.round_id

    def setup(self):
        self.view_names = [
            "RoundCreate",
            "RoundGames",
            "RoundScores",
            "RoundLeaderboard",
            "RoundScorecard",
        ]
        self.view_index = -1
        self.view_array = []

        # load and hide views
        for i in range(len(self.view_names)):
            self.view_index += 1
            self.view_array.append(
                ui.load_view("views/" + self.view_names[self.view_index])
            )
            self.add_subview(self.view_array[self.view_index])
            self.view_array[self.view_index].hidden = True
            self.view_array[self.view_index]._mainView = self
            self.view_array[self.view_index].db = self.db

        # self.view = ui.load_view('views/RoundCreate')
        self.scores = make_button_item(self.goto_scores, title="Scores")
        self.games = make_button_item(self.goto_games, title="Games")
        self.leaderboard = make_button_item(self.goto_leaderboard, title="Leaderboard")
        self.scorecard = make_button_item(self.goto_scorecard, title="Scorecard")
        self.title_buttons = [self.games, self.scores, self.leaderboard, self.scorecard]
        self.left_button_items = [self.games, self.scores]
        self.right_button_items = [self.scorecard, self.leaderboard]
        for button in self.title_buttons:
            button.enabled = False
        self.btnStartRound = self["btnStartRound"]
        self.btnStartRound.action = self.start_round
        self.goto_main()

    def did_load(self):
        self.btnSelectRound = self["btnSelectRound"]
        self.btnSelectRound.action = self.select_round

    def select_round(self, sender):
        """Select an existing round to use with app"""
        session = self.db.Session()
        rounds = session.query(Round).all()
        rrounds = list(reversed(rounds))
        golf_round = dialogs.list_dialog("Select Round", rrounds)
        if golf_round:
            self.set_golf_round(golf_round)
            self.goto_leaderboard()

    def switch_views(self):
        for i in range(len(self.view_array)):
            self.view_array[i].hidden = True
            self.view_array[i].deactivate()
        if self.view_index == -1:
            self.name = "Leaderboard"
            self.bring_to_front()
        else:
            self.view_array[self.view_index].hidden = False
            self.view_array[self.view_index].activate()
            self.view_array[self.view_index].bring_to_front()

    def enable_title_buttons(self, enabled=True):
        for button in self.title_buttons:
            button.enabled = enabled

    def goto_games(self, sender=None):
        self.enable_title_buttons()
        self.view_index = 1
        self.switch_views()

    def goto_scores(self, sender=None):
        self.enable_title_buttons()
        self.view_index = 2
        self.switch_views()

    def goto_leaderboard(self, sender=None):
        self.enable_title_buttons()
        self.view_index = 3
        self.switch_views()

    def goto_scorecard(self, sender):
        self.enable_title_buttons()
        self.view_index = 4
        self.switch_views()

    def goto_main(self):
        self.view_index = -1
        self.switch_views()

    def start_round(self, sender):
        # Start the round
        self.view_index = 0
        self.switch_views()
