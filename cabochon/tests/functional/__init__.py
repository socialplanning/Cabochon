from threading import Thread
from wsgiutils import wsgiServer
import paste

class CabochonTestServer(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.setDaemon(True)

    def run(self):
        self.server_fixture = CabochonServerFixture()
        server = wsgiServer.WSGIServer (('localhost', 10424), {'/': self.server_fixture}, serveFiles = False)
        server.serve_forever()       

class CabochonServerFixture:
    def __init__(self):
        self.requests_received = []

    def clear(self):
        self.requests_received = []

    def __call__(self, environ, start_response):
        path_info = environ.get('PATH_INFO', '')
        req = paste.wsgiwrappers.WSGIRequest(environ)
        
        self.requests_received.append({'path' :  environ['PATH_INFO'], 'method' : environ['REQUEST_METHOD'], 'params' : req.params})        
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
            return ['"accepted"']

        
