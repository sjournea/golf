import pytest

from golf_db.round import GolfRound
from golf_db.player import GolfPlayer
from golf_db.course import GolfCourse
from golf_db.db import GolfDB, GolfDBAdmin
from golf_db.exceptions import GolfDBException
from golf_db.player import GolfPlayer


class TestDBType:
    def test_type_default(self):
        db = GolfDB(database="golf_test")

    lstSupportedTypes = ["local"]

    @pytest.mark.parametrize("db_type", lstSupportedTypes)
    def test_type_supported(self, db_type):
        db = GolfDB(database="golf_test", db_type=db_type)

    lstNotSupportedTypes = ["mongo", "restapi", "redis"]

    @pytest.mark.parametrize("db_type", lstNotSupportedTypes)
    def test_type_not_supported(self, db_type):
        with pytest.raises(GolfDBException):
            db = GolfDB(database="golf_test", db_type=db_type)


class TesrDBInit:
    @pytest.mark.skip()
    def test_create_mongo(self):
        db = GolfDBAdmin(database="golf_test", db_type="mongo")
        db.create()
        dctDatabases = db.databases()
        assert "golf_test" in dctDatabases
        collections = dctDatabases["golf_test"]
        expected_collections = ["courses", "players", "rounds"]
        assert len(collections) == len(expected_collections)
        for exp in expected_collections:
            assert exp in collections
        # test remove
        db.remove()
        dctDatabases = db.databases()
        assert "golf_test" not in dctDatabases

    lstSupportedTypes = ["local"]

    @pytest.mark.parametrize("db_type", lstSupportedTypes)
    def test_create_local(self, db_type):
        db = GolfDBAdmin(database="golf_test", db_type=db_type)
        db.create()
        dctDatabases = db.databases()
        assert "golf_test" in dctDatabases
        collections = dctDatabases["golf_test"]
        expected_collections = ["courses", "players", "rounds"]
        assert len(collections) == len(expected_collections)
        for exp in expected_collections:
            assert exp in collections
        # test remove
        db.remove()
        dctDatabases = db.databases()
        assert "golf_test" not in dctDatabases

    def test_create_fail(self):
        db = GolfDB(database="golf_test")
        with pytest.raises(AttributeError):
            db.create()


class DBTestAPI:
    # @classmethod
    # def setUpClass(cls):
    # cls.db = GolfDBAdmin(database='golf_test')
    # cls.db.create()

    def test_course_api(self):
        # cnt = self.db.courseCount()
        # print 'courses : {}'.format(cnt)
        courses = self.db.courseList(dbclass=GolfCourse)
        # for course in courses:
        # print course
        c = self.db.courseFind(courses[1].name, dbclass=GolfCourse)[0]
        # print c
        self.assertEqual(c, courses[1])

    def test_player_api(self):
        # cnt = self.db.playerCount()
        # print 'players : {}'.format(cnt)
        players = self.db.playerList(dbclass=GolfPlayer)
        # for player in players:
        # print player
        p = self.db.playerFind(players[1].email, dbclass=GolfPlayer)[0]
        # print r
        self.assertEqual(p, players[1])

    def test_player_save(self):
        beatle = GolfPlayer()
        beatle.email = "jlennon@beatles.com"
        beatle.first_name = "John"
        beatle.last_name = "Lennon"
        beatle.handicap = 18.4
        beatle.nick_name = "NoReligion"

        # add and verify count
        cnt0 = self.db.players.count()
        self.db.playerSave(beatle)
        cnt = self.db.players.count()
        self.assertEqual(cnt0 + 1, cnt)

        # find and verify equal
        p = self.db.playerFind(beatle.email, dbclass=GolfPlayer)[0]
        self.assertEqual(p, beatle)

        # save again and verify fails
        with self.assertRaises(GolfDBException):
            self.db.playerSave(beatle)

    def test_round_api(self):
        cnt = self.db.rounds.count()
        # print 'rounds : {}'.format(cnt)
        rounds = self.db.roundList(dbclass=GolfRound)
        # for r in rounds:
        # print r
        r = self.db.roundFind(rounds[1].course.name, dbclass=GolfRound)[0]
        # print r
        self.assertEqual(r, rounds[1])


@pytest.mark.skip()
class TestDB_Local(DBTestAPI):
    @classmethod
    def setUpClass(cls):
        cls.db = GolfDBAdmin(database="golf_test", db_type="local")
        cls.db.create()
