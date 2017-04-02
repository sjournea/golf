"""game_factory.py -- factory for games."""
from .exceptions import GolfException
from .game_gross import GrossGame
from .game import NetGame
from .game import SkinsGame

dctGames = { 
  'skins': SkinsGame,
  'gross': GrossGame,
  'net': NetGame,
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