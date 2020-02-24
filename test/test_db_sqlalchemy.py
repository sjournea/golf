"""test_db_sqlalchemy.py"""
import pytest
from golf_db.db_sqlalchemy import Player, Hole
from golf_db.db_sqlalchemy import Database, DBAdmin


# in-memory database
test_golf_url = "sqlite://"
test_golf_admin_url = "sqlite://"
tables = sorted(
    ["games", "holes", "players", "results", "scores", "rounds", "tees", "courses"]
)


@pytest.fixture
def db():
    return Database(test_golf_url)


@pytest.fixture
def db_admin():
    return DBAdmin(test_golf_admin_url)


class TestDatabase:
    def test_init(self, db):
        assert db.url == test_golf_url
        assert db.engine is not None
        assert db.Session is not None

    def test_create_session(self, db):
        session = db.create_session()
        assert session is not None

    def test_create_tables(self, db):
        db.create_tables()

    def test_list_tables(self, db):
        db.create_tables()
        database_tables = db.list_tables()
        assert database_tables == tables


class TestDBAdmin:
    def test_init(self, db_admin):
        pass

    def test_remove_all(self, db_admin):
        db_admin.create_tables()
        db_admin.remove()
        database_tables = db_admin.list_tables()
        assert database_tables == []


class TestPlayer:
    lst_columns = [
        "player_id",
        "email",
        "first_name",
        "last_name",
        "nick_name",
        "handicap",
        "gender",
    ]
    lst_valid_players = [
        {
            "last_name": "Journeay",
            "first_name": "Steve",
            "nick_name": "Hammy",
            "email": "sjournea@tl.com",
            "gender": "man",
            "handicap": 19.5,
        },
        {
            "last_name": "Journeay",
            "first_name": "Ruby",
            "nick_name": "Frenchie",
            "email": "ruby@tl.com",
            "gender": "woman",
            "handicap": 7.6,
        },
    ]

    def test_columns(self):
        assert Player.__table__.columns.keys() == self.lst_columns

    @pytest.mark.parametrize("dct", lst_valid_players)
    def test_getFullName(self, dct):
        p = Player(**dct)
        assert p.getFullName() == f"{p.first_name} {p.last_name}"

    @pytest.mark.parametrize("dct", lst_valid_players)
    def test_getInitials(self, dct):
        p = Player(**dct)
        assert p.getInitials() == p.first_name[0] + p.last_name[0]

    @pytest.mark.parametrize("dct", lst_valid_players)
    def test_genderPlural(self, dct):
        p = Player(**dct)
        assert p.genderPlural == "mens" if p.gender == "man" else "womens"

    @pytest.mark.parametrize("dct", lst_valid_players)
    def test_str_(self, dct):
        p = Player(**dct)
        s = str(p)
        for value in dct.values():
            assert str(value) in s


class TestHole:
    lst_columns = ["hole_id", "course_id", "num", "par", "handicap"]
    lst_valid_holes = [
        {"num": 1, "par": 4, "handicap": 1},
        {"num": 2, "par": 3, "handicap": 17},
        {"num": 3, "par": 5, "handicap": 3},
    ]

    def test_columns(self):
        assert Hole.__table__.columns.keys() == self.lst_columns

    @pytest.mark.parametrize("dct", lst_valid_holes)
    def test_validate(self, dct):
        h = Hole(**dct)
        h.validate()

    @pytest.mark.parametrize("dct", lst_valid_holes)
    def test_isPar(self, dct):
        h = Hole(**dct)
        assert h.isPar(dct["par"])

    @pytest.mark.parametrize("dct", lst_valid_holes)
    def test_str_(self, dct):
        h = Hole(**dct)
        assert str(h) == f"par {h.par} handicap {h.handicap}"
