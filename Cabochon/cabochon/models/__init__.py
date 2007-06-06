## NOTE
##   If you plan on using SQLObject, the following should be un-commented and provides
##   a starting point for setting up your schema

from sqlobject import *
from pylons.database import PackageHub
from restclient import rest_invoke

hub = PackageHub("cabochon")
__connection__ = hub

# You should then import your SQLObject classes
# from myclass import MyDataClass

#a topic
class Service(SQLObject):
    name = UnicodeCol(default=u"", alternateID=True, length=100)
    events = MultipleJoin('EventType')

#a named type of event
class EventType(SQLObject):
    service = ForeignKey('Service',cascade=True)
    name = UnicodeCol(default="", unique=True, length=100)
    handlers = MultipleJoin('Handler')

#a subscription
class Handler(SQLObject):
    event_type = ForeignKey('EventType',cascade=True)
    url = UnicodeCol(default=u"")
    method = UnicodeCol(default=u"POST")

    def handle(self,params):
        """ make the necessary request in response to the event being triggered """
        rest_invoke(self.url,method=self.method,params=params,async=True)


soClasses=[Service,EventType,Handler]
