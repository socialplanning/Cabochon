# Copyright (C) 2008 The Open Planning Project

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
from pylons.controllers.util import redirect_to
from pylons.decorators.rest import restrict
from webhelpers.pagination import paginate, links
import logging

class AdminController(BaseController):
    def index(self):
        """Return a page displaying everything."""
        c.subscribers = Subscriber.select()
        return render("admin")

    def pending_events(self):
        paginator, c.pending_events = paginate(PendingEvent, request.params.get('page', 0))
        c.page_list = links.pagelist(paginator.current)
        return render("pending_events")

    def failed_events(self):
        paginator, c.failed_events = paginate(FailedEvent, request.params.get('page', 0))
        c.page_list = links.pagelist(paginator.current)
        return render("failed_events")

    @restrict('POST')
    def unsubscribe(self, id):
          Subscriber.get(id).destroySelf()
          g.log("Deleted subscription %s" % id)
          return redirect_to(action="index")

    @restrict('POST')
    def delete_failed_event(self, id):
          FailedEvent.get(id).destroySelf()
          g.log("Deleted pending event %s" % id)
          return redirect_to(action="failed_events")

    @restrict('POST')
    def delete_pending_event(self, id):
          PendingEvent.get(id).destroySelf()
          g.log("Deleted failed event %s" % id)
          return redirect_to(action="pending_events")

    @restrict('POST')
    def retry_event(self, id):
          FailedEvent.get(id).reenqueue()
          return redirect_to(action="failed_events")

    @restrict('POST')
    def fail_pending_event(self, id):
          e = PendingEvent.get(id)
          e.fail()
          e.destroySelf()
          return redirect_to(action="pending_events")
      
    def event_details(self, id):
        cls = request.params.get('cls')
        if cls == "pending":
            e = PendingEvent.get(id)
        else:
            e = FailedEvent.get(id)
        c.data = e.data
        c.event = e
        return render("event_details")
