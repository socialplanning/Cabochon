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

from cabochon.lib.base import *
from cabochon.models import *
from pylons.decorators.rest import dispatch_on
from sqlobject.dberrors import DuplicateEntryError

class EventController(BaseController):
    @dispatch_on(POST='create_event')
    @jsonify
    def index(self):
        return [{'id' : e.id, 'name' : e.name} for e in EventType.select()]


    @jsonify
    def subscribers(self, id):
        event = EventType.get(id)
        return [{'id' : h.id, 'url' : h.url, 'method' : h.method} for h in event.subscribers]

    @jsonify
    def create_event(self):
        name = request.params['name']
        try:
            event = EventType(name=name)
            g.log("Created event %s" % name) 
        except DuplicateEntryError:
            event = EventType.selectBy(name=name)[0]
        return {'subscribe' : h.url_for(action='subscribe', id=event.id),
                'fire' : h.url_for(action='fire', id=event.id)}

    @jsonify
    @dispatch_on(POST='do_fire')
    def fire(self, id):
        pass

    def do_fire(self, id):
        event = EventType.get(id)

        def insert_events(event=event, data=request.params):
            for s in event.subscribers:
                PendingEvent(event_type = event, subscriber = s, data=data)

        do_in_transaction(insert_events)

        g.log("Fired event %s" % event.name) 
        return 'accepted'

    @jsonify
    def subscriptions(self, id):
        event_type = EventType.get(id)
        subscriber = Subscriber.selectBy(event_type=event_type, url=request.params['url'])
        try:
            subscriber = subscriber[0]
            return {'unsubscribe' : h.url_for(action='unsubscribe', id=subscriber.id),
                    'fire' : h.url_for(action='fire', id=event_type.id)}
        except:
            return None

    @dispatch_on(POST='do_unsubscribe')
    def unsubscribe(self, id):
        pass

    @jsonify
    def do_unsubscribe(self, id):
        Subscriber.get(id).destroySelf()
        g.log("Deleted subscription %d" % id)
        
    @dispatch_on(POST='do_unsubscribe_by_event')
    def unsubscribe_by_event(self, id):
        pass

    @jsonify
    def do_unsubscribe_by_event(self, id):
        event_type = EventType.selectBy(name=request.params['event'])[0]
        subscriber = Subscriber.selectBy(event_type=event_type, url=request.params['url'])
        try:
            subscriber = subscriber[0]
            g.log("Deleted subscription" % subscriber.id)            
            subscriber.destroySelf()
            return True
        except:
            return False


    @dispatch_on(POST='do_subscribe')
    def subscribe(self, id):
        pass

    @jsonify
    def do_subscribe(self, id):
        event_type = EventType.get(id)
        subscriber = Subscriber.selectBy(event_type=event_type, url=request.params['url'])
        try:
            subscriber = subscriber[0]
            subscriber.set(**dict(request.params))
            g.log("New subscription %s to %s at %s" % (subscriber.id, event_type.name, request.params['url']))
        except IndexError:
            subscriber = Subscriber(event_type=event_type, **dict(request.params))
            g.log("Updated subscription %s to %s at %s" % (subscriber.id, event_type.name, request.params['url']))

        return h.url_for(action='unsubscribe', id=subscriber.id)
