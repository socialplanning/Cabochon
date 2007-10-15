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
from cabochon.tests.functional import CabochonTestServer
from cabochon.models import *
import cabochon.lib.helpers as h
from simplejson import loads as fromjson, dumps
from paste.util.multidict import MultiDict
import time

from paste.deploy import loadapp
import paste.fixture

test_server = CabochonTestServer()
test_server.start()

def send_all_pending_events(res):
    while not res.g.event_sender.event_queue_empty():
        time.sleep(0.2)

def jsonpost(old_post):
    def jsonpost_func(url, params={}):
        params = dict((key, dumps(value)) for key, value in params.items())            
        return old_post(url, params)
    return jsonpost_func
        
class TestCabochonController(TestController):
    def setUp(self):
        test_server.server_fixture.clear()
        for e in EventType.select():
            e.destroySelf()
        for s in Subscriber.select():
            s.destroySelf()
        for p in PendingEvent.select():
            p.destroySelf()            

        wsgiapp = loadapp('config:test.ini', relative_to=self.conf_dir)
        self.app = paste.fixture.TestApp(wsgiapp)
        old_post = self.app.post
        self.app.post = jsonpost(old_post)
        
    def test_cabochon(self):
        res = self.app.post(h.url_for(controller='event'), params={'name' : 'test_event'})
        urls = fromjson(res.body)
        fire_url = urls['fire']
        subscribe_url = urls['subscribe']
        res = self.app.post(subscribe_url, params={'url' : 'http://localhost:10424/test', 'method' : 'POST'})
        
        res = self.app.post(fire_url, params={'morx' : [1], 'fleem' : 2})
        assert fromjson(res.body) == {'status' : "accepted"}

        send_all_pending_events(res)

        server_fixture = test_server.server_fixture
        assert server_fixture.requests_received == [{'path': '/test', 'params': MultiDict([('fleem', '2'), ('morx', '[1]')]), 'method': 'POST'}]


    def test_redirect(self):
        res = self.app.post(h.url_for(controller='event'), params={'name' : 'test_event'})
        urls = fromjson(res.body)
        fire_url = urls['fire']
        subscribe_url = urls['subscribe']
        res = self.app.post(subscribe_url, params={'url' : 'http://localhost:10424/elsewhere', 'method' : 'POST', 'redirections': 0})
        
        res = self.app.post(fire_url, params={'morx' : [1], 'fleem' : 2})
        assert fromjson(res.body) == {'status' : "accepted"}

        send_all_pending_events(res)

        server_fixture = test_server.server_fixture
        assert server_fixture.requests_received == [{'path': '/elsewhere', 'params': MultiDict([('fleem', '2'), ('morx', '[1]')]), 'method': 'POST'}]


    def test_unsub(self):
        res = self.app.post(h.url_for(controller='event'), params={'name' : 'nte'})
        urls = fromjson(res.body)
        fire_url = urls['fire']
        subscribe_url = urls['subscribe']

        #subscribe and send a message
        res = self.app.post(subscribe_url, params={'url' : 'http://localhost:10424/morx/fleem', 'method' : 'POST'})
        unsubscribe_url = fromjson(res.body)['unsubscribe']
        
        res = self.app.post(fire_url, params={'morx' : [1], 'fleem' : 2})
        assert fromjson(res.body) == {'status' : "accepted"}

        send_all_pending_events(res)

        #now unsubscribe and send a message
        res = self.app.post(unsubscribe_url)
        assert fromjson(res.body) == {'status' : 'unsubscribed'}
        
        res = self.app.post(fire_url, params={'morx' : [1], 'fleem' : 2})
        assert fromjson(res.body) == {'status' : "accepted"}        
        
        send_all_pending_events(res)

        #we only get the first message
        server_fixture = test_server.server_fixture
        assert server_fixture.requests_received == [{'path': '/morx/fleem', 'params': MultiDict([('fleem', '2'), ('morx', '[1]')]), 'method': 'POST'}]

        

    def test_unsub_by_event(self):
        res = self.app.post(h.url_for(controller='event'), params={'name' : 'grib'})
        urls = fromjson(res.body)
        fire_url = urls['fire']
        subscribe_url = urls['subscribe']

        #subscribe and send a message
        res = self.app.post(subscribe_url, params={'url' : 'http://localhost:10424/morx/fleem', 'method' : 'POST'})
        
        res = self.app.post(fire_url, params={'morx' : [1], 'fleem' : 2})
        assert fromjson(res.body) == {'status' : "accepted"}

        send_all_pending_events(res)

        #now unsubscribe and send a message
        res = self.app.post(h.url_for(controller='event', action='unsubscribe_by_event'), params={'url' : 'http://localhost:10424/morx/fleem', 'event' : 'grib'})
        assert fromjson(res.body) == {"status" : "unsubscribed"}
        
        res = self.app.post(fire_url, params={'morx' : [1], 'fleem' : 2})
        assert fromjson(res.body) == {'status' : "accepted"}
        
        send_all_pending_events(res)

        #we only get the first message
        server_fixture = test_server.server_fixture
        assert server_fixture.requests_received == [{'path': '/morx/fleem', 'params': MultiDict([('fleem', '2'), ('morx', '[1]')]), 'method': 'POST'}]

        

