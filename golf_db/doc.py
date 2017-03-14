"""doc.py"""


class Doc(object):
  """Abstract fields MUST be defined."""
  def __init__(self, dct=None):
    super(Doc, self).__init__()
    # initiaze all fields to None
    for field in self.fields:
      setattr(self, field, None)
    # initialize from dictionary
    if dct:
      self.fromDict(dct)
  
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


class Expand(object):
  """Abstract fields MUST be defined."""
  def __init__(self, dct=None):
    super(Expand, self).__init__()
    # initialize from dictionary
    if dct:
      self.fromDict(dct)
  
  def fromDict(self, dct):
    for key,value in dct.iteritems():
      setattr(self, key, value)
  
  #def toDict(self):
    #dct = {}
    #for field in self.fields:
      #dct[field] = getattr(self, field)
    #return dct
    
  #def __eq__(self, other):
    #for field in self.fields:
      #if getattr(self, field) != getattr(other, field):
        #return False
    #return True

  def __ne__(self,other):
    return not self == other
