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
    