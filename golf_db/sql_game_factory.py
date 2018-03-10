"""sql_game_factory.py -- factory for games."""
from .exceptions import GolfException
from .sql_game_gross import SqlGameGross
from .sql_game_net import SqlGameNet
from .sql_game_skins import SqlGameSkins
from .sql_game_putts import SqlGamePutts
from .sql_game_stableford import SqlGameStableford

dctGames = { 
  'gross': SqlGameGross,
  'net': SqlGameNet,
  'skins': SqlGameSkins,
  'putts': SqlGamePutts,
  'stableford': SqlGameStableford,
}

def SqlGolfGameFactory(game):
  """Return the SQL game class.
  
  Args:
    game: name of game.
  Returns:
    game class
  Raises:
    GolfException - bad game name.
  """
  if game in dctGames:
    return dctGames[game]
  raise GolfException('SQL game "{}" not supported'.format(game))

def SqlGolfGameList():
  """Return list of available games."""
  lst = dctGames.keys()
  return sorted(lst) 
  
