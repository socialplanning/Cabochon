## NOTE
##   If you plan on using SQLObject, the following should be un-commented and provides
##   a starting point for setting up your schema

from sqlobject import *
from pylons.database import PackageHub
from restclient import rest_invoke
from pickle import dumps, loads

hub = PackageHub("cabochon")
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

    def handle(self,params):
        """ make the necessary request in response to the event being triggered """
        rest_invoke(self.url,method=self.method,params=params,async=True)

class PendingEvent(SQLObject):
    subscriber = ForeignKey('Subscriber')
    data = UnicodeCol()

    def _set_data(self, value):
        return self._SO_set_data(dumps(value))

    def _get_data(self):
        return loads(self._SO_get_data())

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
