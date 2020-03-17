from .player import GolfPlayer


class GolfScore(object):
    """Golf Score for a player in a round.
  
  player - GolfPlayer
  tee - which tee used on course.
  course_handicap - 
  """

    def __init__(self, dct=None):
        super(GolfScore, self).__init__()
        self.player = GolfPlayer()
        self.tee = None
        self.course_handicap = 0
        if dct:
            self.fromDict(dct)

    def getFullName(self):
        return self.player.getFullName()

    def getInitials(self):
        return self.player.getInitials()

    def toDict(self):
        return {
            "player": self.player.toDict(),
            "tee": self.tee,
            "course_handicap": self.course_handicap,
        }

    def fromDict(self, dct):
        self.player.fromDict(dct["player"])
        self.tee = dct.get("tee")
        self.course_handicap = dct.get("course_handicap", 0)

    def __eq__(self, other):
        return (
            self.player == other.player
            and self.course_handicap == other.course_handicap
            and self.tee == other.tee
        )

    def __ne__(self, other):
        return not self == other

    def calcCourseHandicap(self):
        """Course Handicap = Handicap Index * Slope rating / 113."""
        self.course_handicap = int(
            round(self.player.handicap * self.tee["slope"] / 113)
        )

    def __str__(self):
        return "{} - course_handicap:{} tee:{}".format(
            self.player.nick_name, self.course_handicap, self.tee["name"]
        )

    def __repr__(self):
        return "GolfScore(dct={})".format(self.toDict())
