"""test_db_sqlalchemy.py"""
import pytest
from golf_db.db_sqlalchemy import Player, Hole, Tee, Course
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
def sess():
    db = Database(test_golf_url)
    db.create_tables()
    return db.create_session()


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

    @pytest.mark.parametrize("dct", lst_valid_players)
    def test_insert(self, sess, dct):
        p = Player(**dct)
        sess.add(p)
        sess.commit()

    def test_insert_fail_no_email(self, sess):
        p = Player()
        sess.add(p)
        with pytest.raises(Exception):
            sess.commit()

    def test_insert_fail_bad_gender(self, sess):
        p = Player(email="sj@tl.com", gender="dog")
        sess.add(p)
        with pytest.raises(Exception):
            sess.commit()

    def test_insert_fail_duplicate_email(self, sess):
        p = Player(email="sj@tl.com")
        sess.add(p)
        sess.commit()
        p2 = Player(email="sj@tl.com")
        sess.add(p2)
        with pytest.raises(Exception):
            sess.commit()


class TestHole:
    lst_columns = ["hole_id", "course_id", "num", "par", "handicap"]
    lst_valid_holes = [
        {"course_id": 1, "num": 1, "par": 4, "handicap": 1},
        {"course_id": 1, "num": 2, "par": 3, "handicap": 17},
        {"course_id": 1, "num": 3, "par": 5, "handicap": 3},
    ]
    lst_invalid_holes = [
        {},
        {"course_id": 1, "num": 1, "par": 4},
        {"course_id": 1, "num": 2, "handicap": 17},
        {"course_id": 1, "par": 5, "handicap": 3},
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

    @pytest.mark.parametrize("dct", lst_valid_holes)
    def test_insert(self, sess, dct):
        h = Hole(**dct)
        sess.add(h)
        sess.commit()

    @pytest.mark.parametrize("dct", lst_invalid_holes)
    def test_insert_fail_invalid_holes(self, sess, dct):
        h = Hole(**dct)
        sess.add(h)
        with pytest.raises(Exception):
            sess.commit()


class TestTees:
    lst_columns = ["tee_id", "course_id", "gender", "name", "rating", "slope"]
    lst_valid_tees = [
        {"course_id": 1, "gender": "mens", "name": "Blue", "rating": 72.2, "slope": 68},
        {
            "course_id": 1,
            "gender": "womens",
            "name": "Red",
            "rating": 72.2,
            "slope": 68,
        },
    ]
    lst_invalid_tees = [
        {},
        {"gender": "mens", "name": "Blue", "rating": 72.2, "slope": 68},
        {"course_id": 1, "name": "Blue", "rating": 72.2, "slope": 68},
        {"course_id": 1, "gender": "mens", "rating": 72.2, "slope": 68},
        {"course_id": 1, "gender": "mens", "name": "Blue", "slope": 68},
        {"course_id": 1, "gender": "mens", "name": "Blue", "rating": 72.2},
        {"course_id": 1, "gender": "goat", "name": "Blue", "rating": 72.2, "slope": 68},
    ]

    def test_columns(self):
        assert Tee.__table__.columns.keys() == self.lst_columns

    @pytest.mark.parametrize("dct", lst_valid_tees)
    def test_insert(self, sess, dct):
        t = Tee(**dct)
        sess.add(t)
        sess.commit()

    @pytest.mark.parametrize("dct", lst_invalid_tees)
    def test_insert_fail_invalid_tees(self, sess, dct):
        h = Tee(**dct)
        sess.add(h)
        with pytest.raises(Exception):
            sess.commit()


class TestCourse:
    lst_columns = ["course_id", "name"]
    lst_all_columns = lst_columns + ["holes", "tees", "round"]

    def test_columns(self):
        assert Course.__table__.columns.keys() == self.lst_columns
