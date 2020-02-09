import pytest
import datetime

from golf_db.round import GolfRound
from golf_db.player import GolfPlayer
from golf_db.course import GolfCourse
from golf_db.db import GolfDBAdmin

# from golf_db.game import GolfGame, SkinsGame, NetGame
from golf_db.game_gross import GrossGame

# from golf_db.game_factory import GolfGameFactory
# from golf_db.exceptions import GolfException


class TestGolfGrossGame:
    @classmethod
    def setup_class(cls):
        cls.db = GolfDBAdmin(database="golf_game_test")
        cls.db.create()

    def setup_method(self):
        course_name = "Canyon Lakes"
        tee_name = "Blue"
        date_of_round = datetime.datetime(2017, 3, 23)
        lstPlayers = ["sjournea", "snake"]

        self.gr = GolfRound()
        self.gr.course = self.db.courseFind(course_name, dbclass=GolfCourse)[0]
        self.gr.date = date_of_round
        for email in lstPlayers:
            pl = self.db.playerFind(email, dbclass=GolfPlayer)[0]
            self.gr.addPlayer(pl, tee_name)

    def test_game_init(self):
        g = GrossGame(self.gr, self.gr.scores)

    def test_game_start(self):
        g = GrossGame(self.gr, self.gr.scores)
        g.start()
        for pl in g.scores:
            assert pl.dct_gross["holes"] == 18 * [None]
            assert pl.dct_gross["in"] == 0
            assert pl.dct_gross["out"] == 0
            assert pl.dct_gross["total"] == 0
            assert pl._esc == 0

    def test_game_add_score(self):
        g = GrossGame(self.gr, self.gr.scores)
        g.start()
        g.addScore(1, [4, 4])

    def test_game_scorecard(self):
        g = GrossGame(self.gr, self.gr.scores)
        g.start()
        for index in range(18):
            g.addScore(index, [4, 4])
            dct = g.getScorecard()
            assert "header" in dct
            assert "players" in dct

    def test_game_leaderboard(self):
        g = GrossGame(self.gr, self.gr.scores)
        g.start()
        for index in range(18):
            g.addScore(index, [4, 4])
            dct = g.getLeaderboard()
            assert "hdr" in dct
            assert "leaderboard" in dct

    def test_game_status(self):
        g = GrossGame(self.gr, self.gr.scores)
        g.start()
        dct = g.getStatus()
        assert "line" in dct
        assert "next_hole" in dct
        assert "par" in dct
        assert "handicap" in dct
        assert dct["next_hole"] == 1
        assert dct["par"] == self.gr.course.holes[0].par
        assert dct["handicap"] == self.gr.course.holes[0].handicap
        for index in range(18):
            g.addScore(index, [4, 4])
            dct = g.getStatus()
            assert "line" in dct
            assert "next_hole" in dct
            assert "par" in dct
            assert "handicap" in dct
            if index < 17:
                assert dct["next_hole"] == index + 2
                assert dct["par"] == self.gr.course.holes[index + 1].par
                assert dct["handicap"] == self.gr.course.holes[index + 1].handicap

            else:
                assert dct["next_hole"] is None
                assert dct["handicap"] is None
                assert dct["par"] == self.gr.course.total
