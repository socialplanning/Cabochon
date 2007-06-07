# Copyright 2007, The Open Planning Project

# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the
# Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor,
# Boston, MA  02110-1301
# USA

from cabochon.tests import *
from cabochon.lib.send_event import send_all_pending_events
import cabochon.lib.helpers as h
from wsgiutils import wsgiServer
import paste
from threading import Thread
from simplejson.decoder import JSONDecoder
from paste.util.multidict import MultiDict

class TestCabochonController(TestController):

    def test_cabochon(self):
        test_server = CabochonTestServer()
        test_server.start()
        decode = JSONDecoder().decode
        
        res = self.app.post(h.url_for(controller='event'), params={'name' : 'test_event'})
        subscribe_url = decode(res.body)
        res = self.app.post(subscribe_url, params={'url' : 'http://localhost:10424/test', 'method' : 'POST'})
        fire_url = decode(res.body)
        
        res = self.app.post(fire_url, params={'morx' : [1], 'fleem' : 2})
        assert decode(res.body) == "accepted"

        send_all_pending_events()

        server_fixture = test_server.server_fixture

        assert server_fixture.requests_received == [{'path': '/test', 'params': MultiDict([('fleem', '2'), ('morx', '[1]')]), 'method': 'POST'}]


class CabochonTestServer(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.setDaemon(True)
        
    def run(self):
        self.server_fixture = CabochonServerFixture()
        server = wsgiServer.WSGIServer (('localhost', 10424), {'/': self.server_fixture})
        server.serve_forever()

class CabochonServerFixture:
    def __init__(self):
        self.requests_received = []

    def clear(self):
        self.requests_received = []

    def __call__(self, environ, start_response):
        path_info = environ.get('PATH_INFO', '')
        if path_info == '/error':
            status = '500 Server Error'
        else:
            status = '200 OK'
            start_response(status, [('Content-type', 'text/plain')])
            req = paste.wsgiwrappers.WSGIRequest(environ)
            
            self.requests_received.append({'path' :  environ['PATH_INFO'], 'method' : environ['REQUEST_METHOD'], 'params' : req.params})
            return ['"accepted"']

        
