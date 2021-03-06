""" game.py - GolfGame class."""
from abc import ABC, abstractmethod
from .exceptions import GolfException
from .score import GolfScore
from util.tl_logger import TLLog

log = TLLog.getLogger("golfgame")


class GolfGame(ABC):
    """Base class for all golf games."""

    description = "<Description not set>"
    short_description = "<Not set>"

    def __init__(self, golf_round, scores, **kwargs):
        self.golf_round = golf_round
        self.players = kwargs.get("players")
        if not self.players:
            self.players = [n for n in range(len(scores))]
        self.scores = [GolfScore(dct=scores[n].toDict()) for n in self.players]
        self.dctScorecard = {"course": self.golf_round.course.getScorecard()}
        self.dctLeaderboard = {}
        self.dctStatus = {}
        self._wager = kwargs.get("wager")
        self.validate()

    def validate(self):
        """Validate a game."""
        if self._wager is not None:
            self._wager = float(self._wager)
            if self._wager <= 0:
                raise GolfException("Wager must be float value > 0")

    def setGrossScore(self, hole_index, lstScores, options):
        """set gross scores for a hole.

    Args:
      hole_index: [0..17]
      lstScores: list of the gross scores.
      options: doctionary of additional values for this hole_index.
    """
        self.setOptions(options if options else {})
        lst = [lstScores[n] for n in self.players]
        self.addScore(hole_index, lst)

    @abstractmethod
    def start(self):
        """Start the game."""
        pass

    @abstractmethod
    def addScore(self, hole_index, lstScores):
        """add scores for a hole."""
        pass

    def setOptions(self, options):
        """Additional options parsed by each test."""
        pass

    def addPutts(self, hole_index, lstPutts, **kwargs):
        """add putts for a hole."""
        pass

    @abstractmethod
    def getScorecard(self, **kwargs):
        """Return scorecard dictionary for this game."""
        pass

    @abstractmethod
    def getLeaderboard(self, **kwargs):
        """Return leaderboard for this game.
    
    Returns:
      list of dictionaries sorted in the order of 1st to last.
    """
        pass

    @abstractmethod
    def getStatus(self, **kwargs):
        """Return simple status for state of game."""
        pass

    def complete(self):
        """Complete a game. Overload for process when a game is complete."""
        pass

    def _init_dict(self, score_type=int):
        """Create and initialize scoring dictionary.
      
      add holes, in, out, total.
    """
        return {
            "holes": [None for _ in range(len(self.golf_round.course.holes))],
            "in": score_type(0),
            "out": score_type(0),
            "total": score_type(0),
        }

    def _update_totals(self, dct):
        """Update totals in a dictionary. If a value is None it is not added.

       dct must contain the following keys:
         holes: list of number scores
         in: total for holes 10..18
         out: total for holes 1..9
         total: in + out + overall (if set).
    """
        dct["out"] = sum([sc for sc in dct["holes"][:9] if sc is not None])
        dct["in"] = sum([sc for sc in dct["holes"][9:] if sc is not None])
        dct["total"] = dct["in"] + dct["out"] + dct.get("overall", 0)

    @property
    def total_payout(self):
        """Return total payout if wager is set."""
        return (
            len(self.golf_round.course.holes) * self._wager * len(self.scores)
            if self._wager
            else None
        )

    def _calc_money_from_points(self):
        """Determine the money totals from points.

       Currently supports payment methods.
        2-2-2: 1/3 front 9, 1/3 back 9, 1/3 overall.
    """

        def sort_calc(points_key, money_key, split):
            scores = sorted(
                self.scores,
                key=lambda score: score.dct_points[points_key],
                reverse=True,
            )
            scores = [
                sc
                for sc in scores
                if sc.dct_points[points_key] == scores[0].dct_points[points_key]
            ]
            pay = (self.total_payout / split) / len(scores)
            log.info(
                "_calc_money_from_points() - {} - pay:{} scores:{}".format(
                    points_key, pay, [sc.player.nick_name for sc in scores]
                )
            )
            for sc in scores:
                sc.dct_money[money_key] = pay

        log.info(
            "_calc_money_from_points() - total_payout:{}".format(self.total_payout)
        )
        # assumes dct_points is already updated.
        for sc in self.scores:
            sc.dct_money = {"in": 0, "out": 0, "total": 0, "overall": 0}
        if self._thru >= 9:
            sort_calc("out", "out", 3)
        if self._thru == 18:
            sort_calc("in", "in", 3)
            sort_calc("total", "overall", 3)
        # update money total
        for sc in self.scores:
            dct = sc.dct_money
            dct["total"] = dct["in"] + dct["out"] + dct.get("overall", 0)


class GolfTeam(ABC):
    """Base class for all golf teams."""

    def __init__(self, players, **kwargs):
        self.name = kwargs.get("name")
        self.players = players[:]
        if not self.name:
            self.name = "/".join([pl.getInitials() for pl in self.players])

    @abstractmethod
    def setup(self, course, min_handicap):
        pass

    @abstractmethod
    def calculate_score(self, index):
        pass

    @abstractmethod
    def update_points(self, index, other_team):
        pass
