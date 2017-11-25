"""game_factory.py -- factory for games."""
from .exceptions import GolfException
from .game_gross import GrossGame
from .game_net import NetGame
from .game_skins import SkinsGame
from .game_six_point import SixPointGame
from .game_eighty_one import EightyOneGame
from .game_match import MatchGame
from .game_stableford import StablefordGame

dctGames = { 
  'skins': SkinsGame,
  'gross': GrossGame,
  'net': NetGame,
  'six_point': SixPointGame, 
  'eighty_one': EightyOneGame, 
  'match': MatchGame, 
  'stableford': StablefordGame, 
}

def GolfGameFactory(game):
  """Return the game class.
  
  Args:
    game: name of game.
  Returns:
    game class
  Raises:
    GolfException - bad game name.
  """
  if game in dctGames:
    return dctGames[game]
  raise GolfException('game "{}" not supported'.format(game))

def GolfGameList():
  """Return list of available games."""
  lst = dctGames.keys()
  return sorted(lst) 
  
