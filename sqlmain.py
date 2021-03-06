#!/usr/bin/env python
""" dbmain.py - simple query test program for database """
import datetime
import logging

# import platform
import threading
import traceback

# from golf_db.player import GolfPlayer
from golf_db.course import GolfCourse
from golf_db.data.test_courses import DBGolfCourses
from golf_db.data.test_players import DBGolfPlayers
from golf_db.sql_game_factory import SqlGolfGameOptions
from golf_db.exceptions import GolfGameException

from util.menu import MenuItem, Menu, InputException
from util.tl_logger import TLLog, logOptions

from golf_db.db_sqlalchemy import (
    Player,
    Course,
    Round,
    Hole,
    Tee,
    Result,
    Game,
    DBAdmin,
)

TLLog.config("logs/sqlmain.log", defLogLevel=logging.INFO)

log = TLLog.getLogger("sqlmain")


class SQLMenu(Menu):
    def __init__(self, **kwargs):
        cmdFile = kwargs.get("cmdFile")
        super().__init__(cmdFile)

        self.url = kwargs.get("url")
        self.db = DBAdmin(self.url)
        self._round_id = None
        # add menu items
        self.addMenuItem(
            MenuItem("dc", "", "create golf database.", self._createDatabase)
        )
        self.addMenuItem(
            MenuItem(
                "RM", "", "remove all data from golf database.", self._clearDatabase
            )
        )
        self.addMenuItem(MenuItem("pli", "", "player insert.", self._playerInsert))
        self.addMenuItem(MenuItem("pll", "", "player list.", self._playerList))
        self.addMenuItem(
            MenuItem("plu", "<email> <key,value>", "player update.", self._playerUpdate)
        )
        self.addMenuItem(MenuItem("plr", "", "player remove.", self._playerRemove))
        self.addMenuItem(
            MenuItem("coi", "testdata", "course insert.", self._courseInsert)
        )
        self.addMenuItem(MenuItem("col", "", "course list.", self._courseList))
        self.addMenuItem(
            MenuItem("cou", "<name> <key,value>", "course update.", self._courseUpdate)
        )
        self.addMenuItem(MenuItem("cor", "", "course remove.", self._courseRemove))
        self.addMenuItem(
            MenuItem("cos", "", "Get a scorecard", self._courseGetScorecard)
        )
        self.addMenuItem(MenuItem("rol", "", "round list.", self._roundList))
        self.addMenuItem(
            MenuItem(
                "gcr",
                "<course> <YYYY-MM-DD> [option=value,...]",
                "Create a Round of Golf",
                self._roundCreate,
            )
        )
        self.addMenuItem(
            MenuItem(
                "gad",
                "<email> <tee>",
                "Add player to Round of Golf",
                self._roundAddPlayer,
            )
        )
        self.addMenuItem(
            MenuItem(
                "gag",
                "<game> <players>",
                "Add game to Round of Golf",
                self._roundAddGame,
            )
        )
        self.addMenuItem(MenuItem("gst", "", "Start Round of Golf", self._roundStart))
        self.addMenuItem(
            MenuItem(
                "gas",
                "<hole> gross=<gross..> <pause=enable>",
                "Add Scores",
                self._roundScore,
            )
        )
        self.addMenuItem(MenuItem("sql", "", "Test a SQLAlchemy query", self._roundSQL))
        self.addMenuItem(MenuItem("tbl", "", "SQLAlchemy tables", self._dbTables))
        self.updateHeader()

    def updateHeader(self):
        self.header = "database url:{} - database:{}".format(self.url, "???")

    def _dbTables(self):
        for col in Player.__table__.columns:
            print("col.name:{}".format(col.name))
            print("col.desc:{}".format(col.desc))
            print("col.type:{}".format(col.type))
            # print('type(col):{}'.format(type(col)))
            for attr in dir(col):
                try:
                    if attr[0] == "_":
                        continue
                    print("  {:<30} -- {}".format(attr, getattr(col, attr)))
                except Exception as ex:
                    print("  EXCEPTION - {}".format(ex))

    def _clearDatabase(self):
        self.db.remove()

    def _createDatabase(self):
        self.db.create_tables()

    def _playerInsert(self):
        """Inserts ALL players from DBGolfPlayers."""
        session = self.db.Session()
        if self.lstCmd[1] == "testdata":
            for dct in DBGolfPlayers:
                player = Player(**dct)
                session.add(player)
        else:
            dct = {}
            for values in self.lstCmd[1:]:
                lst = values.split("=")
                dct[lst[0]] = eval(lst[1])
            player = Player(**dct)
            session.add(player)
        session.commit()

    def _playerList(self):
        """List all players in database."""
        session = self.db.Session()
        players = session.query(Player).all()
        print("{} players".format(len(players)))
        for n, player in enumerate(players):
            print("  {:<2}:{}".format(n + 1, player))

    def _playerRemove(self):
        """Remove ALL players from database.
    plr <email>|all
    """
        session = self.db.Session()
        query = session.query(Player)
        if self.lstCmd[1] == "all":
            players = query.all()
        else:
            player = query.filter(Player.email == self.lstCmd[1]).first()
            players = [player]
        for player in players:
            session.delete(player)
        session.commit()

    def _playerUpdate(self):
        """Update a player record.
    plu <email> <key=value> ...
    """
        session = self.db.Session()
        email = self.lstCmd[1]
        query = session.query(Player)
        player = query.filter(Player.email == email).first()
        for values in self.lstCmd[2:]:
            lst = values.split("=")
            if hasattr(player, lst[0]):
                setattr(player, lst[0], eval(lst[1]))
            else:
                raise InputException('player has no attribute "{}"'.format(lst[0]))
        session.commit()

    def _courseInsert(self):
        """Inserts courses to database."""
        session = self.db.Session()
        if self.lstCmd[1] == "testdata":
            for dct in DBGolfCourses:
                # co = GolfCourse(dct=dct)
                course = Course(name=dct["name"])
                for n, dct_hole in enumerate(dct["holes"]):
                    hole = Hole(
                        par=dct_hole["par"],
                        handicap=dct_hole["handicap"],
                        num=n + 1,
                        course=course,
                    )
                    session.add(hole)
                for gt in dct["tees"]:
                    tee = Tee(
                        gender=gt["gender"],
                        name=gt["name"],
                        rating=gt["rating"],
                        slope=gt["slope"],
                        course=course,
                    )
                    session.add(tee)
                session.add(course)
        else:
            raise InputException("only testdata allowed for courses insert.")
        session.commit()

    def _courseList(self):
        """List all courses in database."""
        session = self.db.Session()
        query = session.query(Course)
        match = "all"
        if len(self.lstCmd) > 1:
            query = query.filter(Course.name.like("%{}%".format(self.lstCmd[1])))
            match = 'name contains "{}"'.format(self.lstCmd[1])
        courses = query.all()
        print(f"{len(courses)} courses - {match}")
        for n, course in enumerate(courses):
            print(f"  {n+1:<2}:{course}")

    def _courseRemove(self):
        """Remove course from database.
    cor <name>|all
    """
        session = self.db.Session()
        query = session.query(Course)
        if self.lstCmd[1] == "all":
            courses = query.all()
        else:
            course = query.filter(
                Course.name.like("%{}%".format(self.lstCmd[1]))
            ).first()
            courses = [course]
        for course in courses:
            session.delete(course)
        session.commit()

    def _courseUpdate(self):
        """Update a course record.
    cou <name> <key=value> ...
    """
        raise InputException("course update not implemented (yet)")

    def _courseGetScorecard(self):
        if len(self.lstCmd) < 2:
            raise InputException(
                "Not enough arguments for {} command".format(self.lstCmd[0])
            )
        session = self.db.Session()
        query = session.query(Course).filter(
            Course.name.like("%{}%".format(self.lstCmd[1]))
        )
        course = query.first()
        print(course)
        dct = course.getScorecard()
        print(dct["hdr"])
        print(dct["par"])
        print(dct["hdcp"])

    def _roundList(self):
        """List all rounds in database."""
        # dct = {}
        # for arg in self.lstCmd[2:]:
        # lst = arg.split('=')
        # if lst[0] == '':
        # players = eval(lst[1])
        # else:
        # dct[lst[0]] = eval(lst[1])

        session = self.db.Session()
        query = session.query(Round)
        # if len(self.lstCmd) > 1:
        # query = query.filter(Course.name.like('%{}%'.format(self.lstCmd[1])))
        # match = 'name contains "{}"'.format(self.lstCmd[1])
        rounds = query.all()
        print("{} rounds".format(len(rounds)))
        for n, golf_round in enumerate(rounds):
            print("{:>2} : {}".format(n + 1, golf_round))

    def _roundCreate(self):
        if len(self.lstCmd) < 3:
            raise InputException("Not enough arguments for %s command" % self.lstCmd[0])
        dtPlay = datetime.datetime.strptime(self.lstCmd[2], "%Y-%m-%d")
        # get options
        options = {}
        for option in self.lstCmd[3:]:
            lst = option.split("=")
            options[lst[0]] = lst[1]
        # session
        session = self.db.Session()
        query = session.query(Course).filter(
            Course.name.like("%{}%".format(self.lstCmd[1]))
        )
        course = query.first()
        golf_round = Round(course_id=course.course_id, date_played=dtPlay)
        session.add(golf_round)
        session.commit()
        if options:
            print("options:{}".format(options))
            for key, value in options.items():
                print("key:{} value:{}".format(key, value))
                golf_round.set_option(key, value)
                session.commit()
        # save round id
        self._round_id = golf_round.round_id
        print("new round id = {}".format(golf_round.round_id))

    def _roundAddPlayer(self):
        # gap <email like> <tee>
        if self._round_id is None:
            raise InputException("Golf round not created")
        if len(self.lstCmd) < 3:
            raise InputException("Not enough arguments for %s command" % self.lstCmd[0])

        session = self.db.Session()
        # get round
        golf_round = session.query(Round).filter(Round.round_id == self._round_id).one()
        # find player
        player = (
            session.query(Player)
            .filter(Player.email.like("%{}%".format(self.lstCmd[1])))
            .one()
        )
        # get tee
        tee = (
            session.query(Tee)
            .filter(
                Tee.course_id == golf_round.course_id,
                Tee.gender == player.genderPlural,
                Tee.name == self.lstCmd[2],
            )
            .one()
        )
        # Create Result
        result = Result(
            round=golf_round,
            player_id=player.player_id,
            tee_id=tee.tee_id,
            handicap=player.handicap,
        )
        result.calcCourseHandicap(tee)
        session.add(result)
        session.commit()

    def _roundStart(self):
        if self._round_id is None:
            raise InputException("Golf round not created")
        self._roundDump()

    def _roundAddGame(self):
        if self._round_id is None:
            raise InputException("Golf round not created")
        if len(self.lstCmd) < 2:
            raise InputException("Not enough arguments for %s command" % self.lstCmd[0])
        game_type = self.lstCmd[1]

        dct = {}
        for arg in self.lstCmd[2:]:
            lst = arg.split("=")
            dct[lst[0]] = lst[1]

        session = self.db.Session()
        # get round
        golf_round = session.query(Round).filter(Round.round_id == self._round_id).one()
        gameOptions = SqlGolfGameOptions(game_type)
        # print('dct:{}'.format(dct))
        # print('gameOptions:{}'.format(gameOptions))
        for key, value in dct.items():
            if key in gameOptions:
                if gameOptions[key]["type"] == "bool":
                    dct[key] = value.lower() in ("yes", "true", "on")
        # print('dct:{}'.format(dct))
        golf_round.addGame(session, game_type, dct)
        session.commit()

    def _roundScore(self):
        """ gas <hole> gross=<list> [pause=enable]"""
        if self._round_id is None:
            raise InputException("Golf round not created")
        if len(self.lstCmd) < 3:
            raise InputException("Not enough arguments for %s command" % self.lstCmd[0])
        hole = int(self.lstCmd[1])
        pause_command = "pause"
        lstGross, lstPutts = None, None
        options = {}
        for arg in self.lstCmd[2:]:
            lst = arg.split("=")
            if lst[0] == "gross":
                lstGross = eval(lst[1])
            elif lst[0] == "putts":
                lstPutts = eval(lst[1])
            elif lst[0] in ("greenie", "snake"):
                options[lst[0]] = eval(lst[1])
            elif lst[0] == "pause":
                pause_command += " " + lst[1]
            else:
                raise InputException("Unknown argument {}".format(arg))
        if lstGross is None:
            raise InputException("gross must be set with gas command.")
        #
        session = self.db.Session()
        # get round
        golf_round = session.query(Round).filter(Round.round_id == self._round_id).one()

        dct_score_data = {
            "lstGross": lstGross,
            "lstPutts": lstPutts,
            "options": options,
        }
        golf_round.addScores(session, hole, dct_score_data)
        session.commit()

        lst_game_more_info_needed = []
        golf_round = session.query(Round).filter(Round.round_id == self._round_id).one()
        for game in golf_round.games:
            try:
                game.CreateGame()
            except GolfGameException as ex:
                print(
                    "{} Game - {} - {}".format(
                        ex.dct["game"].short_description,
                        ex.dct["msg"],
                        ",".join([pl.nick_name for pl in ex.dct["players"]]),
                    )
                )
                lst_game_more_info_needed.append(ex)

        if lst_game_more_info_needed:
            for ex in lst_game_more_info_needed:
                prompt = "{} Game - {} - {} : ".format(
                    ex.dct["game"].short_description,
                    ex.dct["msg"],
                    ",".join(
                        [
                            "{} : {}".format(n, pl.nick_name)
                            for n, pl in enumerate(ex.dct["players"])
                        ]
                    ),
                )

                i = input(prompt)
                if i == "x":
                    raise Exception("Abort by user")
                i = int(i)
                game = (
                    session.query(Game)
                    .filter(Game.game_id == ex.dct["game"].game.game_id)
                    .one()
                )
                game.add_hole_dict_data(
                    ex.dct["hole_num"], {ex.dct["key"]: ex.dct["players"][i].nick_name}
                )
                session.commit()

        self._roundDump()
        self.pushCommands([pause_command])

    def _roundDump(self):
        """ dump scorecard, leaderboard, status."""
        session = self.db.Session()
        # get round
        golf_round = session.query(Round).filter(Round.round_id == self._round_id).one()
        games = [game.CreateGame() for game in golf_round.games]

        self._roundScorecard(golf_round, games)
        self._roundLeaderboard(golf_round, games)
        self._roundStatus(golf_round, games)

    def _roundScorecard(self, golf_round, games):
        dct = golf_round.getScorecard(ESC=True)
        print(dct["title"])
        print(dct["hdr"])
        print(dct["par"])
        print(dct["hdcp"])
        for game in games:
            dct = game.getScorecard()
            print(dct["header"])
            for player in dct["players"]:
                print(player["line"])

    def _roundLeaderboard(self, golf_round, games, **kwargs):
        lstLines = [None for _ in range(10)]

        def update_line(index, msg):
            if lstLines[index] is None:
                lstLines[index] = "{:<22}".format(msg)
            else:
                lstLines[index] += " {:<22}".format(msg)

        header = "{0:-^22}" if kwargs.get("sort_type") == "money" else "{0:*^22}"
        for game in games:
            dctLeaderboard = game.getLeaderboard(**kwargs)
            update_line(0, header.format(" " + game.short_description + " "))
            update_line(1, dctLeaderboard["hdr"])
            for i, dct in enumerate(dctLeaderboard["leaderboard"]):
                update_line(i + 2, dct["line"])
        for line in [line for line in lstLines if line is not None]:
            print(line)

    def _roundStatus(self, golf_round, games):
        for game in games:
            dctStatus = game.getStatus()
            print("{:<15} - {}".format(game.short_description, dctStatus["line"]))

    def _roundSQL(self):
        """ sql <args>"""
        if self._round_id is None:
            raise InputException("Golf round not created")
        #
        session = self.db.Session()
        # get round
        gr = session.query(Round).filter(Round.round_id == self._round_id).one()
        #
        print("round_id:{}".format(gr.round_id))
        print("course_id:{}".format(gr.course_id))
        print("date_played:{}".format(gr.date_played))
        print("course:{}".format(gr.course))
        # print('results:{}'.format(gr.results))
        for n, result in enumerate(gr.results):
            print("  {:>3} - player {}".format(n, result.player.getFullName()))
            for n2, score in enumerate(result.scores):
                print(
                    "    {:>3} - {} {} {}".format(
                        n2, score.num, score.gross, score.putts
                    )
                )
        # print('games:{}'.format(gr.games))
        for n, game in enumerate(gr.games):
            print("  {:>3} - {}".format(n, game))


def main():
    DEF_LOG_ENABLE = "sqlmain"
    DEF_DB_URL = "sqlite:///golf.sqlite"
    # build the command line arguments
    from optparse import OptionParser

    parser = OptionParser()
    parser.add_option(
        "-u",
        "--url",
        dest="url",
        default=DEF_DB_URL,
        help='SQLAlchemy Comma separated list of log modules to enable, * for all. Default is "%s"'
        % DEF_LOG_ENABLE,
    )
    parser.add_option(
        "-m",
        "--logEnable",
        dest="lstLogEnable",
        default=DEF_LOG_ENABLE,
        help='Comma separated list of log modules to enable, * for all. Default is "%s"'
        % DEF_LOG_ENABLE,
    )
    parser.add_option(
        "-g",
        "--showLogs",
        action="store_true",
        dest="showLogs",
        default=False,
        help="list all log options.",
    )
    parser.add_option(
        "-y",
        "--runCmdFile",
        dest="cmdFile",
        default=None,
        help="Run a command file at startup.",
    )

    #  parse the command line and set values
    (options, args) = parser.parse_args()

    try:
        # set the main thread name
        thrd = threading.currentThread()
        thrd.setName("sqlmain")

        log.info(80 * "*")
        log.info("sqlmain - starting")
        logOptions(options.lstLogEnable, options.showLogs, log=log)

        # create menu application
        menu = SQLMenu(url=options.url, cmdFile=options.cmdFile)
        menu.runMenu()

    except Exception as err:
        s = "%s: %s" % (err.__class__.__name__, err)
        log.error(s)
        print(s)

        print("-- traceback --")
        traceback.print_exc()
        print()

    finally:
        log.info("dbmain - exiting")
        TLLog.shutdown()


if __name__ == "__main__":
    main()
