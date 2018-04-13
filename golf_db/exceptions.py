"""exceptions.py - All golf exceptions defined here."""

class GolfException(Exception):
  """Bas Golf app exception, all inherit from here."""
  pass

class DocValidateFail(GolfException):
  """Doc class validate fails."""
  pass

class GolfDBException(GolfException):
  pass

class GolfGameException(GolfException):
  """Raised when a golf game need more information to resolve score."""
  def __init__(self, dct):
    self.dct = dct

  