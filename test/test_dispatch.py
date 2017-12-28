""" functional_tests.py """
import time
import unittest

from util.dispatch import PathDispatcher

class DispatchInstanceTest(unittest.TestCase):
  def setUp(self):
    pass

  def test_create(self):
    pd = PathDispatcher()
    self.assertEqual(pd.pathmap, {})

    
hello_resp = """
<html>
  <head>
    <title>Hello {name}</title>
  </head>
  <body>
    <h1>Hello {name}!</h1>
  </body>
</html>
"""

def hello_world(environ, start_response):
  start_response('200 OK', [('Content-type', 'text/html')])
  params = environ['params']
  resp = hello_resp.format(name=params.get('name'))
  yield resp.encode('utf-8')
  
localtime_resp = '''\
<?xml version="1.0"?>
<time>
  <year>{t.tm_year}</year>
  <month>{t.tm_mon}</month>
  <day>{t.tm_mday}</day>
  <hour>{t.tm_hour}</hour>
  <minute>{t.tm_min}</minute>
  <second>{t.tm_sec}</second>
</time>
'''

def localtime(environ, start_response):
  start_response('200 OK', [('Content-type', 'application/xml')])
  resp = localtime_resp.format(t=time.localtime())
  yield resp.encode('utf-8')

def config_register(dispatcher):
  dispatcher.register('GET', '/hello', hello_world)
  dispatcher.register('GET', '/localtime', localtime)


class DispatchRunTest(unittest.TestCase):
  
  def setUp(self):
    pass
  
  def test_register(self):
    pd = PathDispatcher()
    paths = (
      ('GET', '/hello', hello_world),
      ('GET', '/localtime', localtime),
    )
    self.assertEqual(len(pd.pathmap), 0)
    for n,(method, path, function) in enumerate(paths):
      pd.register(method, path, function)
      self.assertEqual(len(pd.pathmap), n+1)
      self.assertIn((method.lower(), path), pd.pathmap)

