import unittest

from golf_db.db import GolfDB, GolfDBException

class DBTest(unittest.TestCase):
  def test_init(self):
    db = GolfDB()

  def test_course_api(self):
    db = GolfDB()
    print 'courses : {}'.format(db.courseCount())
    courses = db.courseList()
    for course in courses:
      print course
    c = db.courseFind(courses[1].name)
    print c
    self.assertEqual(c, courses[1])
    
  def test_player_api(self):
    db = GolfDB()
    print 'players : {}'.format(db.playerCount())
    players = db.playerList()
    for player in players:
      print player
    
  def test_player_api(self):
    db = GolfDB()
    print 'rounds : {}'.format(db.roundCount())
    rounds = db.roundList()
    for r in rounds:
      print r
    r = db.roundFind(rounds[1].course.name)
    print r
    self.assertEqual(r, rounds[1])
    