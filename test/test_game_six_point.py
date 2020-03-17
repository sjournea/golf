import pytest
import datetime

from golf_db.round import GolfRound
from golf_db.course import GolfCourse
from golf_db.data.test_data import TestGolfPlayers
from golf_db.db import GolfDBAdmin
from golf_db.game_six_point import SixPointGame
from golf_db.player import GolfPlayer
from golf_db.exceptions import GolfException


class TestGolfSixPointGamePlayers:
    @classmethod
    def setup_class(cls):
        cls.db = GolfDBAdmin(database="golf_game_test")
        cls.db.create()

    def test_wrong_number_of_players(self):
        course_name = "Canyon Lakes"
        tee_name = "Blue"
        date_of_round = datetime.datetime(2017, 3, 23)
        lstPlayers = ["sjournea", "snake", "spanky", "reload"]

        gr = GolfRound()
        gr.course = self.db.courseFind(course_name, dbclass=GolfCourse)[0]
        gr.date = date_of_round
        for email in lstPlayers:
            pl = self.db.playerFind(email, dbclass=GolfPlayer)[0]
            gr.addPlayer(pl, tee_name)

        with pytest.raises(GolfException):
            SixPointGame(gr, gr.scores)

        gr2 = GolfRound()
        gr2.course = self.db.courseFind(course_name, dbclass=GolfCourse)[0]
        gr2.date = date_of_round
        for email in lstPlayers[:2]:
            pl = self.db.playerFind(email, dbclass=GolfPlayer)[0]
            gr2.addPlayer(pl, tee_name)
        with pytest.raises(GolfException):
            SixPointGame(gr, gr.scores)

    def test_right_number_of_players(self):
        course_name = "Canyon Lakes"
        tee_name = "Blue"
        date_of_round = datetime.datetime(2017, 3, 23)
        lstPlayers = ["sjournea", "snake", "spanky"]

        gr = GolfRound()
        gr.course = self.db.courseFind(course_name, dbclass=GolfCourse)[0]
        gr.date = date_of_round
        for email in lstPlayers:
            pl = self.db.playerFind(email, dbclass=GolfPlayer)[0]
            gr.addPlayer(pl, tee_name)

        g = SixPointGame(gr, gr.scores)
        g.start()


class TestGolfSixPointGame:
    @classmethod
    def setup_class(cls):
        cls.db = GolfDBAdmin(database="golf_game_test")
        cls.db.create()

    def setup_method(self):
        course_name = "Canyon Lakes"
        tee_name = "Blue"
        date_of_round = datetime.datetime(2017, 3, 23)

        self.gr = GolfRound()
        self.gr.course = self.db.courseFind(course_name, dbclass=GolfCourse)[0]
        self.gr.date = date_of_round
        for dct in TestGolfPlayers[:3]:
            pl = GolfPlayer(dct=dct)
            self.gr.addPlayer(pl, tee_name)

    def test_game_init(self):
        g = SixPointGame(self.gr, self.gr.scores)

    def test_game_start(self):
        g = SixPointGame(self.gr, self.gr.scores)
        g.start()
        for pl in g.scores:
            assert pl._score == 18 * [None]
            assert pl._points == 18 * [None]
            assert pl._in == 0
            assert pl._out == 0
            assert pl._total == 0

    def test_game_add_score(self):
        g = SixPointGame(self.gr, self.gr.scores)
        g.start()

        g.addScore(0, [4, 4, 4])

        assert g.scores[0]._points[0] == 2
        assert g.scores[1]._points[0] == 2
        assert g.scores[2]._points[0] == 2

        g.addScore(1, [3, 4, 4])

        assert g.scores[0]._points[1] == 4
        assert g.scores[1]._points[1] == 1
        assert g.scores[2]._points[1] == 1
        g.addScore(2, [3, 3, 4])
        assert g.scores[0]._points[2] == 3
        assert g.scores[1]._points[2] == 3
        assert g.scores[2]._points[2] == 0
        g.addScore(3, [3, 4, 5])
        assert g.scores[0]._points[3] == 4
        assert g.scores[1]._points[3] == 2
        assert g.scores[2]._points[3] == 0

    def test_game_scorecard(self):
        g = SixPointGame(self.gr, self.gr.scores)
        g.start()
        dct = g.getScorecard()
        assert "course" in dct
        assert "header" in dct
        assert "players" in dct
        players = dct["players"]
        for player in players:
            assert "line" in player
            assert player["in"] == 0
            assert player["out"] == 0
            assert player["total"] == 0

        g.addScore(0, [4, 4, 4])
        dct = g.getScorecard()
        assert "course" in dct
        assert "header" in dct
        assert "players" in dct
        for player in dct["players"]:
            assert "line" in player
            assert player["in"] == 0
            assert player["out"] == 2
            assert player["total"] == 2

        g.addScore(1, [3, 4, 4])
        dct = g.getScorecard()
        assert "course" in dct
        assert "header" in dct
        assert "players" in dct
        for player in dct["players"]:
            assert "line" in player
            assert "in" in player
            assert "out" in player
            assert "total" in player

    def test_game_leaderboard(self):
        g = SixPointGame(self.gr, self.gr.scores)
        g.start()
        dct = g.getLeaderboard()
        assert "hdr" in dct
        assert "leaderboard" in dct
        players = dct["leaderboard"]
        for player in players:
            assert "player" in player
            assert "total" in player
            assert "line" in player
            assert "pos" in player
            assert "thru" in player

        g.addScore(1, [4, 4, 4])
        dct = g.getLeaderboard()
        assert "hdr" in dct
        assert "leaderboard" in dct
        players = dct["leaderboard"]
        for player in players:
            assert "player" in player
            assert "total" in player
            assert "line" in player
            assert "pos" in player
            assert "thru" in player
