import unittest

from golf_db.round import GolfRound
from golf_db.player import GolfPlayer
from golf_db.course import GolfCourse
from golf_db.db import GolfDB, GolfDBAdmin
from golf_db.exceptions import GolfDBException
from golf_db.player import GolfPlayer

class DBTestType(unittest.TestCase):
  def test_type_default(self):
    db = GolfDB(database='golf_test')

  def test_type_mongo(self):
    db = GolfDB(database='golf_test', db_type='mongo')

  def test_type_local(self):
    db = GolfDB(database='golf_test', db_type='local')

  def test_type_rest_api(self):
    with self.assertRaises(GolfDBException):
      db = GolfDB(database='golf_test', db_type='rest_api')

  def test_type_bad_db_type(self):
    with self.assertRaises(GolfDBException):
      db = GolfDB(database='golf_test', db_type='dbase')

class DBTestInit(unittest.TestCase):
  def test_create_mongo(self):
    db = GolfDBAdmin(database='golf_test', db_type='mongo')
    db.create()
    dctDatabases = db.databases()
    self.assertIn('golf_test', dctDatabases)
    collections = dctDatabases['golf_test']
    expected_collections = [u'courses', u'players',u'rounds']
    self.assertEqual(len(collections), len(expected_collections))
    for exp in expected_collections:
      self.assertIn(exp, collections)
    # test remove
    db.remove()
    dctDatabases = db.databases()
    self.assertNotIn('golf_test', dctDatabases)

  def test_create_local(self):
    db = GolfDBAdmin(database='golf_test', db_type='local')
    db.create()
    dctDatabases = db.databases()
    self.assertIn('golf_test', dctDatabases)
    collections = dctDatabases['golf_test']
    expected_collections = [u'courses', u'players',u'rounds']
    self.assertEqual(len(collections), len(expected_collections))
    for exp in expected_collections:
      self.assertIn(exp, collections)
    # test remove
    db.remove()
    dctDatabases = db.databases()
    self.assertNotIn('golf_test', dctDatabases)

  def test_create_fail(self):
    db = GolfDB(database='golf_test')
    with self.assertRaises(AttributeError):
      db.create()
    
class DBTestAPI:
  #@classmethod
  #def setUpClass(cls):
    #cls.db = GolfDBAdmin(database='golf_test')
    #cls.db.create()
      
  def test_course_api(self):
    #cnt = self.db.courseCount()
    #print 'courses : {}'.format(cnt)
    courses = self.db.courseList(dbclass=GolfCourse)
    #for course in courses:
      #print course
    c = self.db.courseFind(courses[1].name, dbclass=GolfCourse)[0]
    #print c
    self.assertEqual(c, courses[1])
    
  def test_player_api(self):
    #cnt = self.db.playerCount()
    #print 'players : {}'.format(cnt)
    players = self.db.playerList(dbclass=GolfPlayer)
    #for player in players:
      #print player
    p = self.db.playerFind(players[1].email, dbclass=GolfPlayer)[0]
    #print r
    self.assertEqual(p, players[1])
    
  def test_player_save(self):
    beatle = GolfPlayer()
    beatle.email = 'jlennon@beatles.com'
    beatle.first_name = 'John'
    beatle.last_name = 'Lennon'
    beatle.handicap = 18.4
    beatle.nick_name = 'NoReligion'
    
    # add and verify count
    cnt0 = self.db.players.count()
    self.db.playerSave(beatle)
    cnt = self.db.players.count()
    self.assertEqual(cnt0+1, cnt)

    # find and verify equal
    p = self.db.playerFind(beatle.email, dbclass=GolfPlayer)[0]
    self.assertEqual(p, beatle)

    # save again and verify fails
    with self.assertRaises(GolfDBException):
      self.db.playerSave(beatle)
    
  def test_round_api(self):
    cnt = self.db.rounds.count()
    #print 'rounds : {}'.format(cnt)
    rounds = self.db.roundList(dbclass=GolfRound)
    #for r in rounds:
      #print r
    r = self.db.roundFind(rounds[1].course.name, dbclass=GolfRound)[0]
    #print r
    self.assertEqual(r, rounds[1])


class DBTestAPI_Mongo(DBTestAPI, unittest.TestCase):
  @classmethod
  def setUpClass(cls):
    cls.db = GolfDBAdmin(database='golf_test')
    cls.db.create()


class DBTestAPI_Local(DBTestAPI, unittest.TestCase):
  @classmethod
  def setUpClass(cls):
    cls.db = GolfDBAdmin(database='golf_test', db_type='local')
    cls.db.create()
