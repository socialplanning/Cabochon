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
        try:
            event = EventType(name=request.params['name'])
        except DuplicateEntryError:
            event = EventType.selectBy(name=request.params['name'])[0]
        return h.url_for(action='subscribe', id=event.id)

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
        
        return 'accepted'

    @jsonify
    def subscribe(self, id):
        subscriber = Subscriber(event_type=EventType.get(id), url=request.params['url'], method=request.params['method'])
        return h.url_for(action='fire', id=subscriber.id)
