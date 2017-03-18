"""doc.py"""

class DB(object):
  """Abstract - fields MUST be defined."""
  def __init__(self, dct=None):
    super(DB, self).__init__()
    # Add _id field
    self.fields.append('_id')

  def put(self, collection):
    collection.save(self.toDict(), safe=True)

class DocValidateFail(Exception):
  pass

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
    dct = {}
    for field in self.fields:
      dct[field] = getattr(self, field)
    return dct
    
  def __eq__(self, other):
    for field in self.fields:
      if getattr(self, field) != getattr(other, field):
        return False
    return True

  def __ne__(self,other):
    return not self == other


