import pytest
import datetime

from golf_db.round import GolfRound
from golf_db.player import GolfPlayer
from golf_db.course import GolfCourse
from golf_db.db import GolfDBAdmin

# from golf_db.game import GolfGame, SkinsGame, NetGame
from golf_db.game_greenie import GreenieGame

# from golf_db.game_factory import GolfGa7meFactory
from golf_db.exceptions import GolfException


class TestGolfGameGreenie:
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
        g = GreenieGame(self.gr, self.gr.scores)
        assert g._carry_over
        assert g._double_birdie
        assert g._last_par_3_carry
        assert g._wager is None
        assert g.total_payout is None

        g = GreenieGame(
            self.gr,
            self.gr.scores,
            carry_over=False,
            double_birdie=False,
            last_par_3_carry=False,
        )
        assert not g._carry_over
        assert not g._double_birdie
        assert not g._last_par_3_carry
        assert g._wager is None
        assert g.total_payout is None

    def test_game_wager(self):
        with pytest.raises(GolfException):
            GreenieGame(self.gr, self.gr.scores, wager=0.0)

        with pytest.raises(GolfException):
            GreenieGame(self.gr, self.gr.scores, wager=-45.0)

        g = GreenieGame(self.gr, self.gr.scores, wager=1.0)
        assert g._wager == 1.0
        assert g.total_payout == 1 * 2 * 5

    def test_game_start(self):
        g = GreenieGame(self.gr, self.gr.scores)
        g.start()
        for pl in g.scores:
            assert pl.dct_points["holes"] == 18 * [None]
            assert pl.dct_points["in"] == 0
            assert pl.dct_points["out"] == 0
            assert pl.dct_points["total"] == 0
            assert pl.dct_money is None
        assert g._carry == 0
        assert g._next_hole == 0
        assert g._use_green_in_regulation == False
        assert "header" in g.dctScorecard

        g = GreenieGame(self.gr, self.gr.scores, wager=1.0)
        g.start()
        for pl in g.scores:
            assert pl.dct_money["holes"] == 18 * [None]
            assert pl.dct_money["in"] == 0.0
            assert pl.dct_money["out"] == 0.0
            assert pl.dct_money["total"] == 0.0
        assert "header" in g.dctScorecard

    def test_game_add_score(self):
        g = GreenieGame(self.gr, self.gr.scores)
        g.start()
        g.setGrossScore(0, [4, 4], options={"putts": [1, 1]})
        g.setGrossScore(1, [5, 5], options={"putts": [1, 1]})
        g.setGrossScore(2, [3, 3], {"putts": [1, 1], "closest_to_pin": 0})

        assert g.scores[0].dct_points["holes"][2] == 1
        assert g.scores[0].dct_points["out"] == 1
        assert g.scores[0].dct_points["in"] == 0
        assert g.scores[0].dct_points["total"] == 1

        g.setGrossScore(3, [4, 4], options={"putts": [1, 1]})
        g.setGrossScore(4, [3, 3], options={"putts": [1, 1], "closest_to_pin": 0})

        assert g.scores[0].dct_points["holes"][4] == 1
        assert g.scores[0].dct_points["out"] == 2
        assert g.scores[0].dct_points["in"] == 0
        assert g.scores[0].dct_points["total"] == 2

        g = GreenieGame(self.gr, self.gr.scores, wager=1.0)
        g.start()
        g.setGrossScore(0, [4, 4], options={"putts": [1, 1]})
        g.setGrossScore(1, [5, 5], options={"putts": [1, 1]})
        g.setGrossScore(2, [3, 3], {"putts": [1, 1], "closest_to_pin": 0})

        assert g.scores[0].dct_money["holes"][2] == 2.0
        assert g.scores[0].dct_money["out"] == 2.0
        assert g.scores[0].dct_money["in"] == 0
        assert g.scores[0].dct_money["total"] == 2

        g.setGrossScore(3, [4, 4], options={"putts": [1, 1]})
        g.setGrossScore(4, [3, 3], options={"putts": [1, 1], "closest_to_pin": 0})

        assert g.scores[0].dct_money["holes"][4] == 2.0
        assert g.scores[0].dct_money["out"] == 4.0
        assert g.scores[0].dct_money["in"] == 0
        assert g.scores[0].dct_money["total"] == 4

    def test_game_scorecard(self):
        g = GreenieGame(self.gr, self.gr.scores)
        g.start()
        for index in range(18):
            g.setGrossScore(1, [4, 4], options={"putts": [1, 1]})
            dct = g.getScorecard()
            assert "header" in dct
            assert "players" in dct

    def test_game_leaderboard(self):
        g = GreenieGame(self.gr, self.gr.scores)
        g.start()
        for index in range(18):
            g.setGrossScore(1, [4, 4], options={"putts": [1, 1]})
            dct = g.getLeaderboard()
            assert "hdr" in dct
            assert "leaderboard" in dct

    def test_game_status(self):
        g = GreenieGame(self.gr, self.gr.scores)
        g.start()
        dct = g.getStatus()
        assert "line" in dct
        assert "next_hole" in dct
        assert dct["next_hole"] == 1
        for index in range(18):
            g.setGrossScore(1, [4, 4], options={"putts": [1, 1]})
            dct = g.getStatus()
            assert "line" in dct
            assert "next_hole" in dct
            if index < 17:
                assert dct["next_hole"] == index + 2
            else:
                assert dct["next_hole"] is None
