import unittest

from golf_db.db import GolfDB, GolfDBException
from golf_db.player import GolfPlayer

class DBTestType(unittest.TestCase):
  def test_type_default(self):
    db = GolfDB(database='golf_test')

  def test_type_mongo(self):
    db = GolfDB(database='golf_test', db_type='mongo')

  def test_type_rest_api(self):
    with self.assertRaises(GolfDBException):
      db = GolfDB(database='golf_test', db_type='rest_api')

  def test_type_bad_db_type(self):
    with self.assertRaises(GolfDBException):
      db = GolfDB(database='golf_test', db_type='dbase')

class DBTestInit(unittest.TestCase):
  def test_create(self):
    db = GolfDB(database='golf_test')
    db.create()
    with db.db as session:
      dctDatabases = db.db.databases()
    self.assertIn('golf_test', dctDatabases)
    collections = dctDatabases['golf_test']
    expected_collections = [u'courses', u'players',u'rounds']
    self.assertEqual(len(collections), len(expected_collections))
    for exp in expected_collections:
      self.assertIn(exp, collections)
    # test remove
    db.remove()
    with db.db as session:
      dctDatabases = db.db.databases()
    self.assertNotIn('golf_test', dctDatabases)
    
class DBTestAPI(unittest.TestCase):

  @classmethod
  def setUpClass(cls):
    cls.db = GolfDB(database='golf_test')
    cls.db.create()
      
  def test_course_api(self):
    cnt = self.db.courseCount()
    #print 'courses : {}'.format(cnt)
    courses = self.db.courseList()
    #for course in courses:
      #print course
    c = self.db.courseFind(courses[1].name)
    #print c
    self.assertEqual(c, courses[1])
    
  def test_player_api(self):
    cnt = self.db.playerCount()
    #print 'players : {}'.format(cnt)
    players = self.db.playerList()
    #for player in players:
      #print player
    p = self.db.playerFind(players[1].email)
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
    cnt0 = self.db.playerCount()
    self.db.playerSave(beatle)
    cnt = self.db.playerCount()
    self.assertEqual(cnt0+1, cnt)

    # find and verify equal
    p = self.db.playerFind(beatle.email)
    self.assertEqual(p, beatle)

    # save again and verify fails
    with self.assertRaises(GolfDBException):
      self.db.playerSave(beatle)
    
  def test_round_api(self):
    cnt = self.db.roundCount()
    #print 'rounds : {}'.format(cnt)
    rounds = self.db.roundList()
    #for r in rounds:
      #print r
    r = self.db.roundFind(rounds[1].course.name)
    #print r
    self.assertEqual(r, rounds[1])
    