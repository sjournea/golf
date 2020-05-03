import datetime

from golf_db.round import GolfRound
from golf_db.player import GolfPlayer
from golf_db.course import GolfCourse
from golf_db.db import GolfDBAdmin

# from golf_db.game import GolfGame, SkinsGame, NetGame
from golf_db.game_match import MatchGame

# from golf_db.game_factory import GolfGameFactory
# from golf_db.exceptions import GolfException


class TestGolfMatchGame:
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
        g = MatchGame(self.gr, self.gr.scores)

    def test_game_start(self):
        g = MatchGame(self.gr, self.gr.scores)
        g.start()
        for pl in g.scores:
            assert pl._score == 18 * [None]
            assert len(pl._bumps) == 18
            assert pl._hole == 18 * [None]
            assert pl._score == 18 * [None]
            assert pl._in == 0
            assert pl._out == 0
            assert pl._total == 0

    def test_game_add_score(self):
        g = MatchGame(self.gr, self.gr.scores)
        g.start()
        g.addScore(1, [4, 4])

    def test_game_scorecard(self):
        g = MatchGame(self.gr, self.gr.scores)
        g.start()
        g.addScore(1, [4, 4])
        dct = g.getScorecard()
        assert "header" in dct
        assert "players" in dct

    def test_game_leaderboard(self):
        g = MatchGame(self.gr, self.gr.scores)
        g.start()
        g.addScore(1, [4, 4])
        dct = g.getLeaderboard()
        assert "hdr" in dct
        assert "leaderboard" in dct

    def test_game_status(self):
        g = MatchGame(self.gr, self.gr.scores)
        g.start()
        dct = g.getStatus()
        assert "line" in dct
        # self.assertIn('next_hole', dct)
        # self.assertIn('par', dct)
        # self.assertIn('handicap', dct)
        # self.assertEqual(dct['next_hole'], 1)
        # self.assertEqual(dct['par'], self.gr.course.holes[0].par)
        # self.assertEqual(dct['handicap'], self.gr.course.holes[0].handicap)
        # for index in range(18):
        # g.addScore(index, [4,4])
        # dct = g.getStatus()
        # self.assertIn('line', dct)
        # self.assertIn('next_hole', dct)
        # self.assertIn('par', dct)
        # self.assertIn('handicap', dct)
        # if index < 17:
        # self.assertEqual(dct['next_hole'], index+2)
        # self.assertEqual(dct['par'], self.gr.course.holes[index+1].par)
        # self.assertEqual(dct['handicap'], self.gr.course.holes[index+1].handicap)
        # else:
        # self.assertIsNone(dct['next_hole'])
        # self.assertIsNone(dct['handicap'])
        # self.assertEqual(dct['par'], self.gr.course.total)
