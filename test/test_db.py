import unittest

from golf_db.db import GolfDB, GolfDBException

class DBTest(unittest.TestCase):
  def test_init(self):
    db = GolfDB()

  def test_course_api(self):
    db = GolfDB()
    cnt = db.courseCount()
    #print 'courses : {}'.format(cnt)
    courses = db.courseList()
    #for course in courses:
      #print course
    c = db.courseFind(courses[1].name)
    #print c
    self.assertEqual(c, courses[1])
    
  def test_player_api(self):
    db = GolfDB()
    cnt = db.playerCount()
    #print 'players : {}'.format(cnt)
    players = db.playerList()
    #for player in players:
      #print player
    p = db.playerFind(players[1].email)
    #print r
    self.assertEqual(p, players[1])
    
  def test_round_api(self):
    db = GolfDB()
    cnt = db.roundCount()
    #print 'rounds : {}'.format(cnt)
    rounds = db.roundList()
    #for r in rounds:
      #print r
    r = db.roundFind(rounds[1].course.name)
    #print r
    self.assertEqual(r, rounds[1])
    