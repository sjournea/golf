import unittest

from golf_db.doc import Doc
from golf_db.exceptions import DocValidateFail

class DocBaseCase(unittest.TestCase):
  def test_init_empty(self):
    doc = Doc()
    self.assertEqual(doc.toDict(), {})
    doc.fromDict({})
    self.assertEqual(doc.toDict(), {})

  def test_init_dct(self):
    doc = Doc(dct={})
    self.assertEqual(doc.toDict(), {})
    doc.fromDict({})
    self.assertEqual(doc.toDict(), {})

  def test_validate(self):
    doc = Doc()
    doc.validate()

class TestDoc(Doc):
  fields = ['ivalue', 'fvalue', 'svalue', 'lvalue']
  

class DocKeywordTest(unittest.TestCase):
  def test_init(self):
    doc = TestDoc(ivalue=3, fvalue=1.0, svalue='hello', lvalue=False)
    self.assertEqual(doc.ivalue, 3)
    self.assertEqual(doc.fvalue, 1.0)
    self.assertEqual(doc.svalue, 'hello')
    self.assertEqual(doc.lvalue, False)

  def test_init_dct(self):
    doc = TestDoc(ivalue=3, fvalue=1.0, svalue='hello', lvalue=False)
    self.assertEqual(doc.toDict(), { 'ivalue':3, 'fvalue':1.0, 'svalue':'hello', 'lvalue':False})


class DocFieldEmpty(unittest.TestCase):
  def test_init(self):
    t = TestDoc()
    for field in TestDoc.fields:
      self.assertTrue(hasattr(t, field))
      self.assertIsNone(getattr(t, field))
    t.validate()
    
  def test_init_empty_dict(self):
    t = TestDoc(dct={})
    for field in TestDoc.fields:
      self.assertTrue(hasattr(t, field))
      self.assertIsNone(getattr(t, field))

  def test_dct_is_nones(self):
    t = TestDoc()
    dct = t.toDict()
    for field in TestDoc.fields:
      self.assertIn(field, dct)
      self.assertIsNone(dct[field])
    self.assertDictEqual(dct, {field: None for field in TestDoc.fields})

  def test_validate(self):
    doc = TestDoc()
    doc.validate()

class DocFieldValues(unittest.TestCase):
  def test_ivalue(self):
    lst = [1, 10, 100, 1000, 0, -1]
    for value in lst:
      t = TestDoc(dct={'ivalue':value})
      self.assertEqual(t.ivalue, value)
      self.assertIsNone(t.fvalue)
      self.assertIsNone(t.svalue)
      self.assertIsNone(t.lvalue)
      dct = t.toDict()
      self.assertEqual(len(dct), len(TestDoc.fields))
      self.assertEqual(dct['ivalue'], value)
      self.assertIsNone(dct['fvalue'])
      self.assertIsNone(dct['svalue'])
      self.assertIsNone(dct['fvalue'])

  def test_fvalue(self):
    lst = [1.0, 10.0, 100.0, 1e-6, 0, -1]
    for value in lst:
      t = TestDoc(dct={'fvalue':value})
      self.assertEqual(t.fvalue, value)
      self.assertIsNone(t.ivalue)
      self.assertIsNone(t.svalue)
      self.assertIsNone(t.lvalue)
      dct = t.toDict()
      self.assertEqual(len(dct), len(TestDoc.fields))
      self.assertEqual(dct['fvalue'], value)
      self.assertIsNone(dct['ivalue'])
      self.assertIsNone(dct['svalue'])
      self.assertIsNone(dct['fvalue'])

  def test_svalue(self):
    lst = ['hello', 'world', '', '\x46']
    for value in lst:
      t = TestDoc(dct={'svalue':value})
      self.assertEqual(t.svalue, value)
      self.assertIsNone(t.ivalue)
      self.assertIsNone(t.fvalue)
      self.assertIsNone(t.lvalue)
      dct = t.toDict()
      self.assertEqual(len(dct), len(TestDoc.fields))
      self.assertEqual(dct['svalue'], value)
      self.assertIsNone(dct['ivalue'])
      self.assertIsNone(dct['fvalue'])
      self.assertIsNone(dct['lvalue'])

  def test_fvalue(self):
    lst = [True, False]
    for value in lst:
      t = TestDoc(dct={'lvalue':value})
      self.assertEqual(t.lvalue, value)
      self.assertIsNone(t.ivalue)
      self.assertIsNone(t.svalue)
      self.assertIsNone(t.fvalue)
      dct = t.toDict()
      self.assertEqual(len(dct), len(TestDoc.fields))
      self.assertEqual(dct['lvalue'], value)
      self.assertIsNone(dct['ivalue'])
      self.assertIsNone(dct['fvalue'])
      self.assertIsNone(dct['svalue'])

class TestDocValidate(TestDoc):
  """Overloads TestDoc and adds type validation."""
  def validate(self):
    # all fields MUST be defined
    for field in self.fields:
      if getattr(self, field) is None:
        raise DocValidateFail('{} must be defined'.format(field))
    # Validate types
    if not isinstance(self.ivalue, int):
      raise DocValidateFail('ivalue must be an int')
    if not isinstance(self.fvalue, float):
      raise DocValidateFail('fvalue must be an float')
    if not isinstance(self.svalue, str):
      raise DocValidateFail('svalue must be an str')
    if not isinstance(self.lvalue, bool):
      raise DocValidateFail('lvalue must be an bool')
    
class DocValidateTest(unittest.TestCase):
  def test_init(self):
    t = TestDocValidate()
    with self.assertRaises(DocValidateFail):
      t.validate()

  def test_init_good(self):
    dct = { 'ivalue': 1, 'lvalue': True, 'fvalue': 45.0, 'svalue': 'Spam'}
    t = TestDocValidate(dct=dct)
    t.validate()
    
  def test_init_missing(self):
    lst = [
      { 'ivalue': 1, 'lvalue': True, 'fvalue': 45.0},
      { 'ivalue': 1, 'lvalue': True, 'svalue': 'Spam'},
      { 'ivalue': 1, 'fvalue': 45.0, 'svalue': 'Spam'},
      { 'lvalue': True, 'fvalue': 45.0, 'svalue': 'Spam'},
    ]
    for dct in lst:
      t = TestDocValidate(dct=dct)
      with self.assertRaises(DocValidateFail):
        t.validate()

  def test_bad_types(self):
    lst = [
      { 'ivalue': 1.0, 'lvalue': True, 'fvalue': 45.0, 'svalue': 'Spam'},
      { 'ivalue': 1, 'lvalue': 's', 'fvalue': 45.0, 'svalue': 'Spam'},
      { 'ivalue': 1, 'lvalue': True, 'fvalue': 'h', 'svalue': 'Spam'},
      { 'ivalue': 1, 'lvalue': True, 'fvalue': 45.0, 'svalue': 46},
    ]
    for dct in lst:
      t = TestDocValidate(dct=dct)
      with self.assertRaises(DocValidateFail):
        t.validate()
