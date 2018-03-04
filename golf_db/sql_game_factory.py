"""sql_game_factory.py -- factory for games."""
from .exceptions import GolfException
from .sql_game_gross import SqlGameGross

dctGames = { 
  'gross': SqlGameGross,
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
  
