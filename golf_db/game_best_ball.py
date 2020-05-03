"""game_best_ball.py - Best Ball Golf Game class."""
from .game import GolfGame, GolfTeam
from .exceptions import GolfException


class BestBallTeam(GolfTeam):
    def __init__(self, players, **kwargs):
        super(BestBallTeam, self).__init__(players, **kwargs)
        ## calc handicap
        # self.handicap = sum([pl.course_handicap for pl in self.players])
        # self.total_bumps = 0

    def setup(self, course):
        """Setup holes and scores for match play."""
        self.course = course
        self._net = [None for _ in range(len(self.course.holes))]
        self._hole = [None for _ in range(len(self.course.holes))]
        self._score = [None for _ in range(len(self.course.holes))]
        self._in = 0
        self._out = 0
        self._total = 0

    def calculate_score(self, index):
        # net scores have already set.
        self._net[index] = min([pl._net[index] for pl in self.players])

    def update_points(self, index, other_team):
        if self._net[index] < other_team._net[index]:
            # win hole
            self._hole[index] = 1
            self._total += 1
            self._score[index] = self._total
        elif self._net[index] > other_team._net[index]:
            # lose hole
            self._hole[index] = -1
            self._total -= 1
            self._score[index] = self._total
        else:
            # hole tied
            self._hole[index] = 0
            self._score[index] = self._total
        self._out = sum([sc for sc in self._hole[:9] if isinstance(sc, int)])
        self._in = sum([sc for sc in self._hole[9:] if isinstance(sc, int)])

    def get_scorecard(self):
        """Scorecard for team."""
        dct = {"team": self.name}
        dct["in"] = self._in
        dct["out"] = self._out
        dct["total"] = self._total
        line = "{:<6}".format(self.name)
        for i, score in enumerate(self._score[:9]):
            s = "" if score is None else "{:d}".format(score)
            line += " {:>3}".format(s)
        line += " {:>4d}".format(self._out)
        for i, score in enumerate(self._score[9:]):
            s = "" if score is None else "{:d}".format(score)
            line += " {:>3}".format(s)
        line += " {:>4d} {:>4d}".format(self._in, self._total)
        dct["line"] = line
        return dct


class BestBallGame(GolfGame):
    """The Best ball golf game."""

    short_description = "BestBall"
    description = """
Two-Person Best Ball: Two golfers play as a team, each with their own ball. The best score on each hole is taken as the 'Team' Score.
Best ball games can be played as match or as medal for 9 holes, 18 holes, or even as a Nassau. 

Three-Person Best Ball (a.k.a Canadian Best Ball): In Canadian Best Ball, two golfers team up and play against a third 
(usually the low handicapper). The two partners play their best ball against the third. 

Four-Person Best Ball: Here, the best ball team is composed of all four players. Again, the lowest score on each 
hole counts as the tam score. Games can also be played that use the best two scores or best three scores of the foursome. 

Allocating Handicap Strokes for Best Ball Games % of Course Handicap
Game	 	                        Men %	Women %
Two-Person Best Ball (stroke)	 	 90%	 95%
Two-Person Best Ball (match)	 	100%	100%
Four-Person Best Ball	 	         80%	 90%
Four-Person Best Two Balls	 	 90%	 95%
"""

    def __init__(self, golf_round, scores, **kwargs):
        self.teams = kwargs.get("teams", ((0, 1), (2, 3)))
        super(BestBallGame, self).__init__(golf_round, scores, **kwargs)

    def validate(self):
        if len(self.scores) != 4:
            raise GolfException(
                "Best ball game must have 4 players, {} found.".format(len(self.scores))
            )
        if len(self.teams) != 2:
            raise GolfException("2 teams of 2 players must be set.")
        lst = [0 for n in range(4)]
        for team in self.teams:
            if len(team) != 2:
                raise GolfException("Teams must have 2 players.")
            lst[team[0]] += 1
            lst[team[1]] += 1
        for cnt in lst:
            if cnt != 1:
                raise GolfException("Malformed team.")

    def start(self):
        """Start the match game."""
        # TODO - for stroke play will need to adjust handicap
        handicap_multiplier = 1
        # find min handicap in all players
        min_handicap = min(
            [gs.course_handicap * handicap_multiplier for gs in self.scores]
        )
        for pl in self.scores:
            pl._net = [None for _ in range(len(self.golf_round.course.holes))]
            pl._bumps = self.golf_round.course.calcBumps(
                pl.course_handicap * handicap_multiplier - min_handicap
            )
        # create teams
        self.team_list = [
            BestBallTeam([self.scores[i1], self.scores[i2]]) for (i1, i2) in self.teams
        ]
        for team in self.team_list:
            team.setup(self.golf_round.course)

        self.win = None
        self.final = False
        self.match_score = None
        self.dctScorecard["header"] = "{0:*^98}".format(" BestBall - Match Play")
        self.dctLeaderboard["hdr"] = "Pos Name   Points Thru"

    def addScore(self, index, lstGross):
        """add scores for a hole."""
        # update gross score for hole
        for pl, gross in zip(self.scores, lstGross):
            pl._net[index] = gross - pl._bumps[index]

        if not self.final:
            # update team score
            for team in self.team_list:
                team.calculate_score(index)
            # update team points using other team score
            self.team_list[0].update_points(index, self.team_list[1])
            self.team_list[1].update_points(index, self.team_list[0])

    def getScorecard(self, **kwargs):
        """Scorecard with all players."""
        self.dctScorecard["players"] = [team.get_scorecard() for team in self.team_list]
        return self.dctScorecard

    def getLeaderboard(self, **kwargs):
        if not self.final:
            for n, score in enumerate(self.team_list[0]._score):
                if score == None:
                    thru = n
                    to_play = len(self.team_list[0]._score) - thru
                    break
            else:
                self.final = True
                thru = len(self.team_list[0]._score)
                to_play = 0
            self.dctLeaderboard["thru"] = thru
            self.dctLeaderboard["to_play"] = to_play
            self.dctLeaderboard["final"] = self.final
            board = []
            for n, team in enumerate(self.team_list):
                dct = {"team": team}
                total = team._total
                if total == 0:
                    status = "All Square"
                elif total > 0:
                    if to_play > 0 and (total > to_play):
                        self.final = True
                        status = "{} & {}".format(total, to_play)
                        self.win = n
                    else:
                        status = "{} Up".format(total)
                        if to_play == 0:
                            self.final = True
                        elif to_play < 5:
                            status += " {} to play".format(to_play)
                elif total < 0:
                    status = "{} Down".format(abs(total))
                line = "{:<10}".format(team.name)
                if total > 0 or (total == 0 and n == 0):
                    line += status
                dct["total"] = total
                dct["status"] = status
                dct["line"] = line
                board.append(dct)
            self.dctLeaderboard["leaderboard"] = board
            self.dctLeaderboard["hdr"] = "{:<10}{}".format(
                "Match", "Final" if self.final else "Thru {}".format(thru)
            )
            if self.final:
                if self.win is not None:
                    winner = self.dctLeaderboard["leaderboard"][self.win]
                    self.match_score = winner["status"]
                else:
                    self.match_score = "Draw"
        return self.dctLeaderboard

    def getStatus(self, **kwargs):
        for n, score in enumerate(self.team_list[0]._score):
            if score is None:
                self.dctStatus["next_hole"] = n + 1
                self.dctStatus["par"] = self.golf_round.course.holes[n].par
                self.dctStatus["handicap"] = self.golf_round.course.holes[n].handicap
                bumps = []
                bump_line = []
                for pl in self.scores:
                    if pl._bumps[n] > 0:
                        dct = {"player": pl.player, "bumps": pl._bumps[n]}
                        bumps.append(dct)
                        bump_line.append(
                            "{}{}".format(
                                pl.player.nick_name,
                                "({})".format(dct["bumps"]) if dct["bumps"] > 1 else "",
                            )
                        )
                self.dctStatus["bumps"] = bumps
                self.dctStatus["line"] = "Hole {} Par {} Hdcp {}".format(
                    self.dctStatus["next_hole"],
                    self.dctStatus["par"],
                    self.dctStatus["handicap"],
                )
                if bumps:
                    self.dctStatus["line"] += " Bumps:{}".format(",".join(bump_line))
                break
        else:
            # round complete
            self.dctStatus["next_hole"] = None
            self.dctStatus["par"] = self.golf_round.course.total
            self.dctStatus["handicap"] = None
            self.dctStatus["line"] = "Round Complete"
        return self.dctStatus
