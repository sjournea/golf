import unittest

from golf_db.doc import Doc, Expand

#class DocInitCase(unittest.TestCase):

  #def test_init_empty(self):
    ## check default parameters
    #doc = Doc()
    #print doc
    ##self.assertIsNone()
    ##self.assertIsNone(course.holes)

class ExpandInitCase(unittest.TestCase):

  def test_init_empty(self):
    # check default parameters
    e = Expand()
    self.assertDictEqual(e.__dict__, {})

  def test_init_dict_int(self):
    # check default parameters
    e = Expand(dct={'i': 1, 'j':100})
    self.assertEqual(e.i, 1)
    self.assertEqual(e.j, 100)

  def test_init_dict_float(self):
    e = Expand(dct={'f': 1.0})
    self.assertEqual(e.f, 1.0)
    e = Expand(dct={'f': 1.5e-99})
    self.assertEqual(e.f, 1.5e-99)

  def test_init_dict_string(self):
    e = Expand(dct={'s': 'String'})
    self.assertEqual(e.s, 'String')
    e = Expand(dct={'s': 'Hello Python'})
    self.assertEqual(e.s, 'Hello Python')
