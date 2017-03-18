"""player.py -- GolfPlayer class."""
from .doc import Doc, DocValidateFail


class GolfPlayer(Doc):
  """Golf player
  
  Members:
    email      - must be unique.
    first_name - string
    last_name  - string
    nick_name  - string
    handicap   - float
  """
  fields = ['email', 'first_name', 'last_name', 'nick_name', 'handicap']

  def __str__(self):
    return '{:<15} - {:<6} {:<10} ({:<6}) handicap {:.1f}'.format(self.email, self.first_name, self.last_name, self.nick_name, self.handicap)
  
  def __repr__(self):
    return 'GolfPlayer(dct={})'.format(self.toDict())


