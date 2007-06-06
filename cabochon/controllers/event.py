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

class EventController(BaseController):
    @dispatch_on(POST='create_event')
    def index(self):
        pass

    @jsonify
    def handlers(self, id):
        event = EventType.get(id)
        return [{'id' : h.id, 'url' : h.url, 'method' : h.method} for h in event.handlers]

    @jsonify
    def create_event(self):
        event = EventType(service=Service.selectBy(name=request.params['service'])[0], name=request.params['name'])
        return event.id

    @jsonify
    @dispatch_on(POST='do_handle')
    def handle(self, id):
        pass

    def do_handle(self, id):
        event = EventType.get(id)
        for h in event.handlers:
            h.handle(params=request.params)
        return ['accepted']

    @jsonify
    def add_handler(self, id):
        return Handler(event_type=EventType.get(id),url=request.params['url'],method=request.params['url']).id
