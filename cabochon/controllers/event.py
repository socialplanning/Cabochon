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
import logging

class EventController(BaseController):
    @dispatch_on(POST='create_event')
    @jsonify
    def index(self):
        """Return a list of registered event types"""
        return {'event_types' : [{'id' : e.id, 'name' : e.name} for e in EventType.select()]}


    @jsonify
    def subscribers(self, id):
        """Return a list of subscribers for a given event type"""
        event = EventType.get(id)
        return {'subscribers' : [{'id' : h.id, 'url' : h.url, 'method' : h.method} for h in event.subscribers]}

    @jsonify
    def create_event(self):
        """Create an event type"""        
        name = self.params['name']
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
        """see do_fire"""
        pass

    def _insert_events(self, event, data):
        log = logging.getLogger('cabochon')
        log.info ("Got event %s" % event.name)
        sender = g.event_sender
        for s in event.subscribers + universalEvent().subscribers:
            log.info ("Enqueueing event %s for %s" % (event.name, s.url))
            e = PendingEvent(event_type = event, subscriber = s, data=data)
            sender.add_pending_event(s, e)
            
    def do_fire(self, id):
        """Fire an event by id"""
        event = EventType.get(id)
        do_in_transaction(lambda:self._insert_events(event, self.params))

        g.log("Fired event %s" % event.name) 
        return {'status' : 'accepted'}

    @jsonify
    @dispatch_on(POST='do_fire_by_name')
    def fire_by_name(self, id):
        "See do_fire_by_name"
        pass

    def do_fire_by_name(self, id):
        """Fire an event by name"""
        try:
            event = EventType.selectBy(name=id)[0]
        except IndexError:
            #there must be no listeners -- that's OK.
            return {'status' : 'accepted'}
        
        do_in_transaction(lambda:self._insert_events(event, self.params))

        g.log("Fired event %s" % event.name) 
        return {'status' : 'accepted'}


    @jsonify
    def subscriptions(self, id):
        """Determine whether a given URL is subscribed to a given event type"""        
        event_type = EventType.get(id)
        subscriber = Subscriber.selectBy(event_type=event_type, url=self.params['url'])
        try:
            subscriber = subscriber[0]
            return {'status' : 'subscribed',
                    'unsubscribe' : h.url_for(action='unsubscribe', id=subscriber.id),
                    'fire' : h.url_for(action='fire', id=event_type.id)}
        except:
            return {'status' : 'not subscribed'}

    @dispatch_on(POST='do_unsubscribe')
    def unsubscribe(self, id):
        """See do_unsubscribe"""
        pass

    @jsonify
    def do_unsubscribe(self, id):
        """Unsubscribe a given subscriber by id"""
        try:
            Subscriber.get(id).destroySelf()
            g.log("Deleted subscription %s" % id)
        except:
            g.log("Failed to delete subscription %s (probably no such thing)" % id)
            return {'status' : 'failed'}
        return {'status' : 'unsubscribed'}
        
    @dispatch_on(POST='do_unsubscribe_by_event')
    def unsubscribe_by_event(self):
        """see do_unsubsribe_by_event"""
        pass

    @jsonify
    def do_unsubscribe_by_event(self):
        """Unsubscribe a given subscriber by event name and URL"""        
        event_type = EventType.selectBy(name=self.params['event'])[0]
        subscriber = Subscriber.selectBy(event_type=event_type, url=self.params['url'])
        try:
            subscriber = subscriber[0]
            g.log("Deleted subscription %s (by event %s)" % (subscriber.id, self.params['event']))
            subscriber.destroySelf()
        except:
            g.log("Failed to delete subscription %s (by event %s)" % (subscriber.id, self.params['event']))
            return {'status' : 'failed'}
        return {'status' : 'unsubscribed'}


    @dispatch_on(POST='do_subscribe')
    def subscribe(self, id):
        """see do_subsribe"""        
        pass

    @jsonify
    def do_subscribe(self, id):
        """Subscribe a given URL to the event with the given id."""
        event_type = EventType.get(id)
        subscriber = Subscriber.selectBy(event_type=event_type, url=self.params['url'])
        try:
            subscriber = subscriber[0]
            subscriber.set(**dict(self.params))
            g.log("New subscription %s to %s at %s" % (subscriber.id, event_type.name, self.params['url']))
        except IndexError:
            subscriber = Subscriber(event_type=event_type, **dict(self.params))
            g.event_sender.add_subscriber(subscriber)
            g.log("Updated subscription %s to %s at %s" % (subscriber.id, event_type.name, self.params['url']))

        return {'unsubscribe' : h.url_for(action='unsubscribe', id=subscriber.id)}
