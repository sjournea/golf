"""hole.py - simple golf hole class."""
from .doc import Doc
from .exceptions import DocValidateFail


class GolfHole(Doc):
    """Golf hole
  
  Members:
    par      - Int - Usually 3, 4, or 5.
    handicap - Int - 1 to 18.
  """

    fields = ["par", "handicap"]
    valid_pars = [3, 4, 5, 6]
    valid_handicaps = [n + 1 for n in range(18)]

    def validate(self):
        if not isinstance(self.par, int):
            raise DocValidateFail("par must be an int")
        if self.par not in self.valid_pars:
            raise DocValidateFail("par must be {}".format(self.valid_pars))
        if not isinstance(self.handicap, int):
            raise DocValidateFail("handicap must be an int")
        if self.handicap not in self.valid_handicaps:
            raise DocValidateFail("handicap must be {}".format(self.valid_handicaps))

    def isPar(self, par):
        return self.par == par

    def __str__(self):
        return "par {} handicap {}".format(self.par, self.handicap)

    def __repr__(self):
        return "GolfHole(dct={})".format(self.toDict())
