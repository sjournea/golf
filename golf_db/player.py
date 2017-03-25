"""player.py -- GolfPlayer class."""
from .doc import Doc
from .exceptions import DocValidateFail


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

  def validate(self):
    if self.email is None:
      raise DocValidateFail('email must be defined')
    if not isinstance(self.email, str):
      raise DocValidateFail('email must be a string')
    if self.first_name is not None and not isinstance(self.first_name, str):
      raise DocValidateFail('first_name must be a string')
    if self.last_name is not None and not isinstance(self.last_name, str):
      raise DocValidateFail('last_name must be a string')
    if self.nick_name is not None and not isinstance(self.nick_name, str):
      raise DocValidateFail('nick_name must be a string')
    if self.handicap is None:
      raise DocValidateFail('handicap must be defined.')
    if not isinstance(self.handicap, float):
      raise DocValidateFail('handicap must be a float')
      
  def __str__(self):
    return '{:<15} - {:<6} {:<10} ({:<6}) handicap {:.1f}'.format(self.email, self.first_name, self.last_name, self.nick_name, self.handicap)
  
  def __repr__(self):
    return 'GolfPlayer(dct={})'.format(self.toDict())


