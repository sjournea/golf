"""db_sqlalchemy.py"""
import ast
import datetime

from sqlalchemy import Table, Column, ForeignKey
from sqlalchemy import Integer, Float, String, Enum, Text, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker, relationship, backref

from .sql_game_factory import SqlGolfGameFactory
from .exceptions import GolfDBException
from util.tl_logger import TLLog

log = TLLog.getLogger("alchemy")

Base = declarative_base()


class Player(Base):
    __tablename__ = "players"
    player_id = Column(Integer(), primary_key=True)
    email = Column(String(132), nullable=False, unique=True)
    first_name = Column(String(20))
    last_name = Column(String(20))
    nick_name = Column(String(20))
    handicap = Column(Float())
    gender = Column(Enum("man", "woman", name="gender"))

    def getFullName(self):
        return "{} {}".format(self.first_name, self.last_name)

    def getInitials(self):
        return self.first_name[0] + self.last_name[0]

    dct_plural_gender = {"man": "mens", "woman": "womens"}

    @property
    def genderPlural(self):
        return self.dct_plural_gender[self.gender]

    def __str__(self):
        return "{:<15} - {:<6} {:<10} {:<8} {:<5} handicap {:.1f}".format(
            self.email,
            self.first_name,
            self.last_name,
            self.nick_name,
            self.gender,
            self.handicap,
        )


class Hole(Base):
    __tablename__ = "holes"
    hole_id = Column(Integer(), primary_key=True)
    course_id = Column(Integer(), ForeignKey("courses.course_id"), nullable=False)
    num = Column(Integer(), nullable=False)
    par = Column(Integer(), nullable=False)
    handicap = Column(Integer(), nullable=False)
    course = relationship("Course", back_populates="holes")

    valid_pars = [3, 4, 5, 6]
    valid_handicaps = [n + 1 for n in range(18)]

    def validate(self):
        if self.par not in self.valid_pars:
            raise Exception("par must be {}".format(self.valid_pars))
        if self.handicap not in self.valid_handicaps:
            raise Exception("handicap must be {}".format(self.valid_handicaps))

    def isPar(self, par):
        return self.par == par

    def __str__(self):
        return "par {} handicap {}".format(self.par, self.handicap)


class Tee(Base):
    __tablename__ = "tees"
    tee_id = Column(Integer(), primary_key=True)
    course_id = Column(Integer(), ForeignKey("courses.course_id"), nullable=False)
    gender = Column(Enum("mens", "womens", name="gender"))
    name = Column(String(32), nullable=False)
    rating = Column(Float(), nullable=False)
    slope = Column(Integer(), nullable=False)
    course = relationship("Course", back_populates="tees")


class Course(Base):
    __tablename__ = "courses"
    course_id = Column(Integer(), primary_key=True)
    name = Column(String(132), nullable=False, unique=True)
    holes = relationship("Hole", order_by=Hole.hole_id, back_populates="course")
    tees = relationship("Tee", order_by=Tee.tee_id, back_populates="course")
    round = relationship("Round", back_populates="course")

    def setStats(self):
        """Par totals."""
        self.out_tot = sum([hole.par for hole in self.holes[:9]])
        self.in_tot = sum([hole.par for hole in self.holes[9:]])
        self.total = self.in_tot + self.out_tot

    def getScorecard(self, **kwargs):
        """Return hdr, par and hdcp lines for scorecard."""
        self.setStats()
        hdr = "Hole  "
        par = "Par   "
        hdcp = "Hdcp  "
        ESC = kwargs.get("ESC", False)
        for n, hole in enumerate(self.holes[:9]):
            hdr += " {:>3}".format(n + 1)
            par += " {:>3}".format(hole.par)
            hdcp += " {:>3}".format(hole.handicap)
        hdr += "  Out "
        par += " {:>4} ".format(self.out_tot)
        hdcp += "      "
        for n, hole in enumerate(self.holes[9:]):
            hdr += "{:>3} ".format(n + 10)
            par += "{:>3} ".format(hole.par)
            hdcp += "{:>3} ".format(hole.handicap)
        hdr += "  In  Tot"
        par += "{:>4} {:>4}".format(self.in_tot, self.total)
        if ESC:
            hdr += "  ESC"
        return {
            "title": "{0:*^98}".format(" " + self.name + " "),
            "hdr": hdr,
            "par": par,
            "hdcp": hdcp,
        }

    def course_par(self):
        return sum([hole.par for hole in self.holes])

    def calcESC(self, hole_index, gross, course_handicap):
        """Determine ESC post value for this gross score."""
        esc = gross
        if course_handicap < 10:
            # Max double bogey
            max_gross = self.holes[hole_index].par + 2
            esc = gross if gross < max_gross else max_gross
        elif course_handicap < 20:
            # Max value of 7
            esc = gross if gross < 7 else 7
        elif course_handicap < 30:
            # Max value of 8
            esc = gross if gross < 8 else 8
        elif course_handicap < 40:
            # Max value of 9
            esc = gross if gross < 9 else 9
        else:
            # course_handicap >= 40
            # Max value of 10
            esc = gross if gross < 10 else 10
        return esc

    def calcBumps(self, handicap):
        """Determine bumps basid in this handicap.

    Args:
      handicap: course handicap.
    Returns:
      list of bumps for each hole.
    """
        bumps = [0 for _ in range(len(self.holes))]
        # handicap > 18 will bump all holes
        while handicap > 17:
            bumps = [x + 1 for x in bumps]
            handicap -= 18
        # now handicaps < 18
        if handicap > 0:
            for bp in range(handicap % 18, 0, -1):
                for n, hole in enumerate(self.holes):
                    if hole.handicap == bp:
                        bumps[n] += 1
                        break
        return bumps

    def get_holes_with_par(self, par):
        """Return list of holes with par argument."""
        return [hole for hole in self.holes if hole.par == par]

    def __str__(self):
        return "{:<40} - {} holes - {} tees par:{}".format(
            self.name, len(self.holes), len(self.tees), self.course_par()
        )


class Score(Base):
    """Player score for a single hole."""

    __tablename__ = "scores"
    score_id = Column(Integer(), primary_key=True)
    result_id = Column(Integer(), ForeignKey("results.result_id"), nullable=False)
    num = Column(Integer(), nullable=False)
    gross = Column(Integer(), nullable=False)
    putts = Column(Integer())
    # ADD text field for score options; snake_closest_3_putt, greenie_closest
    result = relationship("Result", back_populates="scores")


class Result(Base):
    """Player score for a round. References Score records."""

    __tablename__ = "results"
    result_id = Column(Integer(), primary_key=True)
    round_id = Column(Integer(), ForeignKey("rounds.round_id"), nullable=False)
    player_id = Column(Integer(), ForeignKey("players.player_id"), nullable=False)
    tee_id = Column(Integer(), ForeignKey("tees.tee_id"), nullable=False)
    handicap = Column(Float())
    course_handicap = Column(Integer())
    scores = relationship("Score", order_by=Score.num, back_populates="result")
    round = relationship("Round", back_populates="results")
    # player = relationship("Player", uselist=False, back_populates="result")
    player = relationship("Player", uselist=False)

    def calcCourseHandicap(self, tee):
        """Course Handicap = Handicap Index * Slope rating / 113."""
        type = self.round.get_option("calc_course_handicap")
        if type == "simple":
            self.course_handicap = round(self.handicap)
        else:  # type == 'USTA':
            self.course_handicap = int(round(self.handicap * tee.slope / 113))
        print(
            "calcCourseHandicap() type:{} handicap:{} slope:{} course_handicap:{}".format(
                type, self.handicap, tee.slope, self.course_handicap
            )
        )

    def get_completed_holes(self):
        return len(self.scores)


class Game(Base):
    """Games played in a round."""

    __tablename__ = "games"
    game_id = Column(Integer(), primary_key=True)
    round_id = Column(Integer(), ForeignKey("rounds.round_id"), nullable=False)
    game_type = Column(String(32), nullable=False)
    dict_data = Column(Text, default="{}")
    round = relationship("Round", back_populates="games")

    def CreateGame(self):
        game_class = SqlGolfGameFactory(self.game_type)
        self._game_data = self.game_data
        game = game_class(self, self.round, **self._game_data["options"])
        game.validate()
        game.update()
        return game

    @property
    def game_data(self):
        return ast.literal_eval(self.dict_data)

    @game_data.setter
    def game_data(self, value):
        self.dict_data = str(value)

    def add_hole_dict_data(self, hole_num, dct_data):
        dct = self.game_data
        dct[hole_num] = dct_data
        self.game_data = dct


class Round(Base):
    __tablename__ = "rounds"
    round_id = Column(Integer(), primary_key=True)
    course_id = Column(Integer(), ForeignKey("courses.course_id"), nullable=False)
    date_played = Column(Date(), nullable=False, default=datetime.date.today())
    dict_options = Column(Text, default="{}")
    course = relationship("Course", uselist=False)
    results = relationship("Result", order_by=Result.result_id, back_populates="round")
    games = relationship("Game", order_by=Game.game_id, back_populates="round")

    OPTIONS = {"calc_course_handicap": {"type": "enum", "values": ("USGA", "simple")}}

    def get_option(self, name):
        dct = ast.literal_eval(self.dict_options)
        return dct.get(name)

    def set_option(self, name, value):
        if name not in self.OPTIONS:
            raise GolfDBException('option name "{}" not supported'.format(name))
        option = self.OPTIONS[name]
        if option["type"] == "enum":
            if value not in option["values"]:
                raise GolfDBException(
                    'option {} value "{}" illegal. Must be in {}'.format(
                        name, value, option["values"]
                    )
                )
        else:
            raise GolfDBException(
                'option type "{}" not supported'.format(option["type"])
            )
        # set option value
        dct = ast.literal_eval(self.dict_options)
        dct[name] = value
        self.dict_options = str(dct)

    def addScores(self, session, hole, dct_scores):
        """Add some scores for this round.

    Args:
      session: sqalchemy session.
      hole : hole number, 1-number of holes on course.
      dct_scores: dictionary of scare data.
        lstGross - list of gross scores per player (required)
        lstPutts - list of putts per player.
    """
        if hole < 1 or hole > len(self.course.holes):
            raise GolfDBException(
                "hole number must be in 1-{}".format(len(self.course.holes))
            )
        lstGross = dct_scores["lstGross"]
        lstPutts = dct_scores.get("lstPutts")
        if len(lstGross) != len(self.results):
            raise GolfDBException("gross scores do not match number of players")
        if lstPutts and len(lstPutts) != len(self.results):
            raise GolfDBException("putts do not match number of players")
        # update scores
        for n, result in enumerate(self.results):
            score = Score(num=hole, gross=lstGross[n], result=result)
            if lstPutts:
                score.putts = lstPutts[n]
            session.add(score)
        # print('dct_scores:{}'.format(dct_scores))
        options = dct_scores.get("options")
        if options:
            for game in self.games:
                if game.game_type in options:
                    golf_game = (
                        session.query(Game)
                        .filter(Game.round == self, Game.game_type == game.game_type)
                        .one()
                    )
                    golf_game.add_hole_dict_data(hole, options[game.game_type])
                    session.commit()

    def addGame(self, session, game_type, options=None):
        # Create Game
        dict_data = {"options": options}
        game_class = SqlGolfGameFactory(game_type)
        # game_instance = game_class(round, )
        game = Game(round=self, game_type=game_type, dict_data=str(dict_data))
        session.add(game)

    def get_completed_holes(self):
        return max([result.get_completed_holes() for result in self.results])

    def getScorecard(self, ESC=True):
        dct = self.course.getScorecard(ESC=ESC)
        dct["title"] = "{0:*^98}".format(
            " " + self.course.name + " " + str(self.date_played) + " "
        )
        return dct

    def __str__(self):
        return "{} {:<30} - {}".format(
            self.date_played,
            self.course.name,
            ",".join([result.player.nick_name for result in self.results]),
        )


class Database:
    def __init__(self, url):
        self.url = url
        self.engine = create_engine(self.url)
        self.Session = sessionmaker(bind=self.engine)

    def create_session(self):
        return self.Session()

    def create_tables(self):
        """Create all tables."""
        Base.metadata.create_all(self.engine)

    def list_tables(self):
        """Create all tables."""
        inspector = inspect(self.engine)
        return inspector.get_table_names()


class DBAdmin(Database):
    """Database wrapper for golf admin objects."""

    def remove(self):
        """Delete a database."""
        Base.metadata.drop_all(self.engine)
