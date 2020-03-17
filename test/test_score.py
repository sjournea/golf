from golf_db.score import GolfScore
from golf_db.player import GolfPlayer
from golf_db.data.test_data import CanyonLake_Players


class TestGolfScore:
    def test_init_empty(self):
        # check default parameters
        score = GolfScore()
        assert isinstance(score.player, GolfPlayer)
        assert score.tee is None
        assert score.course_handicap == 0

    def test_init_from_dict(self):
        for dct in CanyonLake_Players:
            score = GolfScore(dct=dct)
            assert dct["player"] == score.player.toDict()

    def test_calc_handicap(self):
        for dct in CanyonLake_Players:
            score = GolfScore(dct=dct)
            score.calcCourseHandicap()
