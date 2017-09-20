"""doc.py - base class for document objects.
  
Simple design can be improved.

class Doc 
  member fields - list of attributes to use with class.
                  Must be defined. Default is empty list.
  toDict()      - convert all members to a dictionary.
  fromDict()    - load all members from a dictionary.
  validate()    - Validate the object. Default is just a pass.
                  Raise DocValidateFail for validation failures.
"""
from .exceptions import DocValidateFail

class Doc(object):
  """Abstract fields MUST be defined."""
  fields = []
  def __init__(self, **kwargs):
    super(Doc, self).__init__()
    # initialize all fields tfrom keywords or None
    for field in self.fields:
      setattr(self, field, kwargs.get(field))
    # initialize from dictionary
    if kwargs.get('dct'):
      self.fromDict(kwargs.get('dct'))
  
  def validate(self):
    pass
  
  def fromDict(self, dct):
    for field in self.fields:
      setattr(self, field, dct.get(field))
  
  def toDict(self):
    return { field: getattr(self, field) for field in self.fields }
    
  def __eq__(self, other):
    for field in self.fields:
      if getattr(self, field) != getattr(other, field):
        return False
    return True

  def __ne__(self,other):
    return not self == other


