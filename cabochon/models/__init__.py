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
from restclient import rest_invoke
from pickle import dumps, loads

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
    method = UnicodeCol(default=u"POST")

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
        response = rest_invoke(sub.url,method=sub.method,params=self.data,resp=True)
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
