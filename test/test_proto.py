""" functional_tests.py """
import unittest

from util.proto import Proto


class User(Proto):
    def __init__(self, name, email):
        self.name = name
        self.email = email

    def fromDict(self, dct):
        self.name = dct["name"]
        self.email = dct["email"]

    def toDict(self):
        return {"name": self.name, "email": self.email}


class BadUser(Proto):
    def __init__(self, name, email):
        self.name = name
        self.email = email


class ProtoInstanceTest(unittest.TestCase):
    dct_user = {"name": "Steve", "email": "sjournea@gmail.com"}

    def test_create_base_fails(self):
        with self.assertRaises(TypeError):
            p = Proto()

    def test_create_not_implemented(self):
        with self.assertRaises(TypeError):
            p = BadUser()

    def test_create(self):
        p = User("Steve", "sjournea@gmail.com")

    def test_create_from_dict(self):
        p = User.initFromDict(self.dct_user)
        self.assertEqual(self.dct_user, p.toDict())


class ProtoDictTest(unittest.TestCase):
    dct_user = {"name": "Steve", "email": "sjournea@gmail.com"}
    dct_user2 = {"name": "Ruby", "email": "frenchie@gmail.com"}

    def setUp(self):
        self.user = User(self.dct_user["name"], self.dct_user["email"])

    def test_toDict(self):
        dct = self.user.toDict()
        self.assertIsInstance(dct, dict)
        self.assertEqual(dct, self.dct_user)

    def test_fromDict(self):
        self.user.fromDict(self.dct_user2)
        dct = self.user.toDict()
        self.assertIsInstance(dct, dict)
        self.assertEqual(dct, self.dct_user2)
