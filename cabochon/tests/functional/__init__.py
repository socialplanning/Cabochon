from threading import Thread
from wsgiutils import wsgiServer
import paste
import time
import re

class CabochonTestServer(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.setDaemon(True)
        self._server_fixture = None
        
    @property
    def server_fixture(self):
        while not self._server_fixture:
            time.sleep(0)
        return self._server_fixture

    def run(self):
        self._server_fixture = CabochonServerFixture()
        server = wsgiServer.WSGIServer (('localhost', 10424), {'/': self.server_fixture}, serveFiles = False)
        server.serve_forever()       

        
class CabochonServerFixture:
    wsse_username_re = re.compile('Username="(\w+)"')
    def __init__(self):
        self.requests_received = []

    def clear(self):
        self.requests_received = []

    def __call__(self, environ, start_response):
        path_info = environ.get('PATH_INFO', '')
        req = paste.wsgiwrappers.WSGIRequest(environ)

        req_dict = {'path' :  environ['PATH_INFO'], 'method' : environ['REQUEST_METHOD'], 'params' : req.params}

        if environ.get('HTTP_X_WSSE'):
            match = self.wsse_username_re.search(environ.get('HTTP_X_WSSE'))
            req_dict['username'] = match.group(1)
        
        self.requests_received.append(req_dict)
        if path_info == '/error':
            status = '500 Server Error'
            start_response(status, [('Content-type', 'text/plain')])
            return ['you lose']
        if path_info == '/elsewhere':
            status = '303 Moved'
            start_response(status, [('Location', '/redirected')])
            return ['']
        else:
            status = '200 OK'
            start_response(status, [('Content-type', 'text/plain')])
            return ['{"status" : "accepted"}']

        
