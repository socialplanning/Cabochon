from restclient import rest_invoke
from simplejson import loads, dumps
from random import random
from datetime import datetime
from sha import sha
from wsseauth import wsse_header

def fromjson(json):
    try:
        return loads(json)
    except:
        print "Failed to load json from", json
        raise

class ServerInstaller:
    def __init__(self, config_file, username='', password=''):
        self.config_file = config_file
        self.username = username
        self.password = password
        self.events = []
        try:
            f = open(config_file, "r")
            for line in f:
                if line.startswith("#"):
                    continue
                if not "," in line:
                    continue
                if line.endswith("\n"):
                    line = line[:-1]         
                self.events.append (tuple(line.split(",")))
        except:
            pass #no existing events file

    def rest_invoke(self, *args, **kwargs):
        if self.username:
            headers = kwargs.get('headers', {})
            headers['Authorization'] = 'WSSE profile="UsernameToken"'
            headers['X-WSSE'] = wsse_header(self.username, self.password)

            kwargs['headers'] = headers
        kwargs['params'] = dict((key, dumps(value)) for key, value in kwargs['params'].items())                
        return rest_invoke(*args, **kwargs)

    def save(self):
        f = open(self.config_file, "w")
        for event in self.events:
            f.write(",".join(event))
        f.close()
        
    def addEvent(self, server, event, url, method="POST"):
        self.events.append((server, event, url, method))
        #create the event
        urls = fromjson(self.rest_invoke(server + "/event/", method="POST", params={"name" : event}))
        subscribe_url = urls['subscribe']

        self.rest_invoke(server + subscribe_url, method="POST", params={'url' : url, 'method' : method})

    def removeEvent(self, server, event, url):
        rm = []
        for candidate in self.events:
            if candidate[0:3] == (server, event, url):
                rm.append(candidate)

        for candidate in rm:
            (server, event, url) = candidate
            self.rest_invoke(server + "unsubscribe_by_event", method="POST", params={'url' : url, 'event' : event})
            events.remove(candidate)


    def removeAll(self):
        for e in self.events:
            (server, event, url) = e
            self.rest_invoke(server + "unsubscribe_by_event", method="POST", params={'url' : url, 'event' : event})
            events.remove(e)
