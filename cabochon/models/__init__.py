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

from sqlobject import *
from pylons.database import PackageHub
from pickle import dumps, loads
from paste.util.multidict import MultiDict
import urllib
import httplib2

hub = PackageHub("cabochon", pool_connections=False)
__connection__ = hub

# You should then import your SQLObject classes
# from myclass import MyDataClass

#a named type of event
class EventType(SQLObject):
    name = UnicodeCol(default="", unique=True, length=255)
    subscribers = MultipleJoin('Subscriber')

#a subscription
class Subscriber(SQLObject):
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
    version = StringCol(default=u'')
    
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

class PendingEvent(SQLObject):
    event_type = ForeignKey('EventType', cascade=True)
    subscriber = ForeignKey('Subscriber')
    data = StringCol()
    last_response = UnicodeCol(default="") #for debugging, the last thing we got when we tried to send this
    
    def _set_data(self, value):
        return self._SO_set_data(dumps(value))

    def _get_data(self):
        return loads(self._SO_get_data())

    def handle(self):
        sub = self.subscriber
        params = sub.params
        if not params:
            params = {}
        params.update(self.data)
        h = httplib2.Http()
        h.follow_all_redirects = sub.follow_all_redirects
        headers = MultiDict(sub.headers)
        body = sub.body
        
        if sub.username:
            h.add_credentials(sub.username, sub.password)
       
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

        response = h.request(sub.url, method=sub.method, body=body, headers=headers, redirections=sub.redirections)

        if response[1] != '"accepted"':
            return response

soClasses=[EventType,Subscriber, PendingEvent]


def do_in_transaction(func, *args, **kw):
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
