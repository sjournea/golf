""" game.py - GolfGame class."""
import copy
from .game_six_point import SixPointGame


class EightyOneGame(SixPointGame):
  """Eighty one golf game.
  
  Game for a threesome. 9 points per hole, breakdown:
    Rank   Points
    ----   ------  
    1,2,3  5,3,1
    1,2,2  5,2,2
    1,1,2  4,4,1
    1,1,1  3,3,3
  """
  POINTS_WIN_1ST = 5
  POINTS_TIE_1ST = 4
  POINTS_WIN_2ND = 3
  POINTS_TIE_2ND = 2
  POINTS_ALL_TIE = 3
  POINTS_3RD     = 1
  TITLE = 'Eighty One'
  NAME = 'eighty_one'
