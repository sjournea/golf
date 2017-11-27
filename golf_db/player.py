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
    gender     - string; man or woman
  """
  fields = ['email', 'first_name', 'last_name', 'nick_name', 'handicap', 'gender']
  valid_genders = ['man', 'woman']
  
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
    if self.gender is None:
      raise DocValidateFail('gender must be defined.')
    if self.gender not in self.valid_genders:
      raise DocValidateFail('gender must be in {}'.format(self.valid_genders))

  def getFullName(self):
    return '{} {}'.format(self.first_name, self.last_name)
  
  def getInitials(self):
    return self.first_name[0] + self.last_name[0]
  
  def __str__(self):
    return '{:<15} - {:<6} {:<10} {:<8} {:<5} handicap {:.1f}'.format(
        self.email, self.first_name, self.last_name, self.nick_name, self.gender, self.handicap)
  
  def __repr__(self):
    return 'GolfPlayer(dct={})'.format(self.toDict())


