from restclient import rest_invoke as base_rest_invoke
from cabochonserver import ServerInstaller
from cabochon.tests.functional import CabochonTestServer
from wsseauth import wsse_header
from simplejson import loads as fromjson, dumps
import os
import time
from random import random
from datetime import datetime
from sha import sha
from paste.util.multidict import MultiDict

username = 'topp'
password = 'secret'

#if your cabochon environment does not permit wsse auth,
#uncomment the following line, and comment out the method

#rest_invoke = base_rest_invoke

def rest_invoke(*args, **kwargs):
    #merge in wsse headers

    headers = kwargs.get('headers', {})
    headers['Authorization'] = 'WSSE profile="UsernameToken"'
    headers['X-WSSE'] = wsse_header(username, password)

    kwargs['headers'] = headers
    if 'params' in kwargs:
        kwargs['params'] = dict((key, dumps(value)) for key, value in kwargs['params'].items())                    
    return base_rest_invoke(*args, **kwargs)

def test_server():

    test_server = CabochonTestServer()
    test_server.start()
    time.sleep(0.01) #time for the first line of the new thread to run
    server_fixture = test_server.server_fixture

    server_url = "http://localhost:24532"

    status, body = rest_invoke(server_url + "/event/", method="GET", resp=True)
    if status['status'] != '200':
        raise RuntimeError("You need a Cabochon server running on port 24532")

    event_name = "cabochon_server_library_test_event"

    installer = ServerInstaller(".servers", username=username, password=password)
    installer.addEvent(server_url, event_name, "http://localhost:10424/example/1")
    installer.save()

    #get the fire url

    urls = fromjson(rest_invoke(server_url + "/event", method="POST", params={'name':event_name}))
    fire_url = urls['fire']

    #fire the event
    rest_invoke(server_url + fire_url, method="POST", params={'morx':'fleem'})

    #wait a second
    time.sleep(1)
    #insure that we got it
    assert server_fixture.requests_received == [{'path': '/example/1', 'params': MultiDict([('morx', '"fleem"')]), 'method': 'POST', 'username' : username}], "Actually got %s" % server_fixture.requests_received

    installer2 = ServerInstaller(".servers")

    os.remove(".servers")
