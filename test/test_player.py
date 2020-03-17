import unittest

from golf_db.player import GolfPlayer
from golf_db.data.test_data import GolfPlayers
from golf_db.exceptions import DocValidateFail


class GolfPlayerInitCase(unittest.TestCase):
    def test_init_empty(self):
        # check default parameters
        player = GolfPlayer(email="sjournea@gmail.com", handicap=20.0, gender="man")
        self.assertEqual(player.email, "sjournea@gmail.com")
        self.assertIsNone(player.last_name)
        self.assertIsNone(player.first_name)
        self.assertIsNone(player.nick_name)
        self.assertEqual(player.handicap, 20)
        self.assertEqual(player.gender, "man")

    def test_init_from_dict(self):
        for dct in GolfPlayers:
            player = GolfPlayer(dct=dct)
            self.assertEqual(dct["last_name"], player.last_name)
            self.assertEqual(dct["first_name"], player.first_name)
            self.assertEqual(dct["nick_name"], player.nick_name)
            self.assertEqual(dct["handicap"], player.handicap)
            self.assertEqual(dct["gender"], player.gender)

    def test_toDict(self):
        for dct in GolfPlayers:
            player = GolfPlayer(dct=dct)
            self.assertEqual(player.toDict(), dct)

    def test_fromDict(self):
        for dct in GolfPlayers:
            player = GolfPlayer()
            player.fromDict(dct)
            self.assertEqual(player.toDict(), dct)

    def test_equalOperator(self):
        for dct in GolfPlayers:
            player1 = GolfPlayer(dct=dct)
            player2 = GolfPlayer(dct=player1.toDict())
            self.assertEqual(player1, player2)
            player1.handicap += 1
            self.assertNotEqual(player1, player2)

    def test_validate_good(self):
        for dct in GolfPlayers:
            player = GolfPlayer(dct=dct)
            player.validate()

    def test_get_full_name(self):
        for dct in GolfPlayers:
            player = GolfPlayer(dct=dct)
            name = player.getFullName()
            self.assertIsInstance(name, str)

    def test_validate_fails(self):
        player = GolfPlayer()
        # validate fails, no data
        with self.assertRaises(DocValidateFail):
            player.validate()

        # validate fails until email, handicap, and gender defined
        player.email = "sjournea@gmail.com"
        with self.assertRaises(DocValidateFail):
            player.validate()
        player.handicap = 11.1
        with self.assertRaises(DocValidateFail):
            player.validate()
        player.gender = "man"
        player.validate()

        # validate fails when handicap is not a float
        for bad_handicap in ["11.1", True, "man"]:
            player.handicap = bad_handicap
            with self.assertRaises(DocValidateFail):
                player.validate()
        player.handicap = 11.1

        # validate fails when gender is not man or woman
        for bad_gender in ["dog", True, 42, "tiger woods"]:
            player.gender = bad_gender
            with self.assertRaises(DocValidateFail):
                player.validate()
