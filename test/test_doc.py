import unittest

from golf_db.doc import Doc

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


class TestDoc(Doc):
  fields = ['ivalue', 'fvalue', 'svalue', 'lvalue']

class DocFieldEmpty(unittest.TestCase):
  def test_init(self):
    t = TestDoc()
    for field in TestDoc.fields:
      self.assertTrue(hasattr(t, field))
      self.assertIsNone(getattr(t, field))

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
