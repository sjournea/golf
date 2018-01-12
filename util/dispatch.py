"""dispatch.py - simple REST API dispatcher."""
import cgi
from wsgiref.simple_server import make_server

from util.tl_logger import TLLog
log = TLLog.getLogger('dispatch')

def notfound_404(environ, start_response):
  """default not found return."""
  start_response('404 not found', [('Content-type', 'text/plain')])
  return [b'Not Found']


class PathDispatcher:
  def __init__(self):
    log.debug('__init__')
    self.pathmap = {}

  def __call__(self, environ, start_response):
    log.debug('__call__')
    #for key,value in environ.items():
      #print('  {}:{}'.format(key,value))
    path = environ['PATH_INFO']
    params = cgi.FieldStorage(environ['wsgi.input'], environ=environ)
    method = environ['REQUEST_METHOD'].lower()
    environ['params'] = {key: params.getvalue(key) for key in params}
    handler = self.pathmap.get((method,path), notfound_404)
    return handler(environ, start_response)

  def register(self, method, path, function):
    log.debug('register() method:{} path:{} function:{}'.format(method, path, function))
    self.pathmap[method.lower(), path] = function
    return function

  def server_forever(self, port):
    """Run the server."""
    log.debug('server_forever() port:{}'.format(port))
    # launch server
    self._httpd = make_server('', port, self)
    print('Serving on port {}'.format(port))
    self._httpd.serve_forever()

  def shutdown(self):
    """TODO: implement this."""
    log.debug('shutdown()')
