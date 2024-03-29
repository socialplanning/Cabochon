# Copyright (C) 2007 The Open Planning Project

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

from datetime import datetime
from paste.util.multidict import MultiDict
from pickle import dumps, loads
from pylons import config
from pylons.database import PackageHub
from sqlobject import *
from wsseauth import wsse_header
import httplib2
import logging
import re
import simplejson
import socket
import sys
import urllib

#The maximum number of times we'll try to send an event before we give up.
#Time taken will be 2**(MAX_SEND_FAILURES+1) seconds or so
MAX_SEND_FAILURES=17

log = logging.getLogger('cabochon')

hub = PackageHub("cabochon", pool_connections=False)
__connection__ = hub

# You should then import your SQLObject classes
# from myclass import MyDataClass

#a named type of event
class EventType(SQLObject):
    """Represents a named event type, such as edit_page"""
    name = UnicodeCol(default="", unique=True, length=255)
    subscribers = MultipleJoin('Subscriber')

_universal = None
def universalEvent():
    """Returns the event with name"*", whose subscribers should get all
    messages"""
    global _universal
    if not _universal:
        _universal = EventType.selectBy(name="*")[0]
    return _universal


#a subscription
class Subscriber(SQLObject):
    """Represents a subscription to an event type"""
    event_type = ForeignKey('EventType',cascade=True)
    url = UnicodeCol(default=u"")
    method = StringCol(default=u"POST")
    queryString = StringCol(default=u'')
    body = StringCol(default=u'')
    username = StringCol(default=u'')
    password = StringCol(default=u'')
    params = StringCol(default=u'')
    headers = StringCol(default=u'')
    redirections = IntCol(default=5)
    follow_all_redirects = BoolCol(default=False)
    critical = BoolCol(default=True)
    version = StringCol(default=u'')

    pending_events = MultipleJoin('PendingEvent', orderBy="failures")
    failed_events = MultipleJoin('FailedEvent', orderBy='id')

    def _set_url(self, value):
        assert value.startswith('http'), 'bad subscriber url "%s"' % value
        self._SO_set_url(value)
    
    def _set_redirections(self, value):
        return self._SO_set_redirections(int(value))

    def _set_params(self, value):
        return self._SO_set_params(dumps(value))

    def _get_params(self):
        params = self._SO_get_params()
        if params:
            params = loads(params)
            if params:
                return params
            else:
                return {}
        else:
            return None
    
    def _set_headers(self, value):
        return self._SO_set_headers(dumps(value))

    def _get_headers(self):
        headers = self._SO_get_headers()
        if headers:
            headers = loads(headers)
            if headers:
                return headers
            else:
                return []
        else:
            return []

    def destroySelf(self):
        for event in self.pending_events:
            event.destroySelf()
        for event in self.failed_events:
            event.destroySelf()            
        super(Subscriber, self).destroySelf()

class FailedEvent(SQLObject):
    """An event we have given up on.  It can be reenqueued"""    
    class sqlmeta:
       createSQL = {'mysql' :
                    ['alter table pending_event engine InnoDB;']
                    }
    event_type = ForeignKey('EventType', cascade=True)
    subscriber = ForeignKey('Subscriber')
    data = BLOBCol(length=65535)
    last_response = UnicodeCol(default="") #for debugging, the last thing we got when we tried to send this
    failures = IntCol(default=0)
    last_sent = DateTimeCol()

    def reenqueue(self):
        PendingEvent(event_type=self.event_type, subscriber=self.subscriber,data=self.data) 
        self.destroySelf()

    def _set_data(self, value):
        return self._SO_set_data(dumps(value))

    def _get_data(self):
        return loads(self._SO_get_data())

class PendingEvent(SQLObject):
    """An event in the queue.  It will be resent until it's accepted
    or we give up."""
    class sqlmeta:
       createSQL = {'mysql' :
                    ['alter table pending_event engine InnoDB;']
                    }
    event_type = ForeignKey('EventType', cascade=True)
    subscriber = ForeignKey('Subscriber')
    data = BLOBCol(length=65535)
    last_response = UnicodeCol(default="") #for debugging, the last thing we got when we tried to send this
    failures = IntCol(default=0)
    last_sent = DateTimeCol(default=datetime.now)
    
    def _set_data(self, value):
        return self._SO_set_data(dumps(value))

    def _get_data(self):
        return loads(self._SO_get_data())

    url_template_re = re.compile("\{(.*?)\}")

    @property
    def url(self):
        """URL templating"""
        data = self.data
        original_url = self.subscriber.url

        return self.url_template_re.sub(lambda m: data.get(m.group(1)), original_url)

    def fail(self):
        fields = self.sqlmeta.asDict()
        del fields['id']
        FailedEvent(**fields)

    def handle(self):
        """NOTE: The result of this function is *backwards*.  It
        returns None for success.  Just like C.
        """
        sub = self.subscriber
        params = dict(sub.params)
        params.update(self.data)
        h = httplib2.Http()
        h.follow_all_redirects = sub.follow_all_redirects
        headers = MultiDict(sub.headers)
        body = sub.body
        
        if sub.username:
            h.add_credentials(sub.username, sub.password)

        params = dict((key, simplejson.dumps(value)) for key, value in params.items())

        if sub.method == "GET":
            #merge params with query string
            qs = sub.queryString
            if qs:
                qs += "&"
            else:
                qs = "?"
            qs += urllib.urlencode(params)

            headers['Content-Length'] = '0'
        else:
            body = urllib.urlencode(params)
            headers['Content-Length'] = str(len(body))
            
        if not headers.has_key('Content-Type'):
            headers['Content-Type'] = 'application/x-www-form-urlencoded'

            username = config.get('username', None)
            password = config.get('password', None)
            if username:
                headers['AUTHORIZATION'] = 'WSSE profile="UsernameToken"'
                headers['X_WSSE'] = wsse_header(username, password)

        __traceback_info__ = '%s %s (%i bytes in body)' % (sub.method, self.url, len(body))
        log.info('Sending event %s %s (%i bytes in body, id=%s' % (self.url, sub.method, len(body), self.id))

        self.last_sent = datetime.now()            
        self.failures += 1 #if we succeed, we won't care that someone called
                           #us a failure

        if self.failures > MAX_SEND_FAILURES:
            self.fail()
            return None
            
        
        try:
            response = h.request(self.url, method=sub.method, body=body, headers=headers, redirections=sub.redirections)
        except socket.error, e:
            print >> sys.stderr, 'Error doing %s %s (body length: %i bytes)' % (self.url, sub.method, len(body))
            return "%s" % e, ''
        except httplib2.RedirectLimit:
            #too many redirections. Treat the request as handled,
            #because the subscriber was the one who wanted that
            #limit in the first place
            return None            
            
        #303 -> too many redirections. I think this is for
        #older versions of httplib2.
        success_codes = dict.fromkeys(('303', '200', '201'))
        response_code = response[0]['status']
        if response_code in success_codes:
            if response_code != '303' and sub.critical:
                # we're a 'critical' subscriber, so we need to see an
                # explicit confirmation we were rec'd in the body of the
                # response
                jsonbody = simplejson.loads(response[1])
                if jsonbody.get('status') != 'accepted':
                    return response
            return None
        else:
            return response

soClasses=[EventType, Subscriber, PendingEvent, FailedEvent]


def do_in_transaction(func, *args, **kw):
    """Run a function in a database transaction"""
    old_conn = hub.getConnection()
    conn = old_conn.transaction()
    hub.threadConnection = conn
    try:
        try:
            value = func(*args, **kw)
        except:
            conn.rollback()
            raise
        else:
            conn.commit()
            return value
    finally:
        hub.threadConnection = old_conn
