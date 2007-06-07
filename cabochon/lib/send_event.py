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

from cabochon.models import *
from threading import Thread
import paste
import pylons
import traceback
import time

MAX_THREADS = 10

app_conf = paste.deploy.appconfig('config:development.ini', relative_to='.')
paste.deploy.CONFIG.push_process_config({'app_conf':app_conf})
#engine = pylons.database.create_engine()

subscription_running = set()
    
def process_event(subscriber):
    try:
        try:
            top_event = PendingEvent.selectBy(subscriber=subscriber).orderBy("id").limit(1)
            try:
                top_event = top_event[0]
            except:
                 #no more events for this subscriber
                return

            response = top_event.handle()
            if not response: #yes, response is backwards on purpose
                top_event.destroySelf()
            else:
                top_event.last_response = "%s %s" % response
                return False # failed to handle one

            return True #handled one successfully

        except Exception, e:
            traceback.print_exc()
    finally:
        if subscriber.id in subscription_running:
            subscription_running.remove(subscriber.id)


def loop_send_events():
    while 1:
        subscribers = Subscriber.select()
        for subscriber in subscribers:
            if subscriber.id in subscription_running:
                continue
            while len(subscription_running) > MAX_THREADS:
                time.sleep(0.001)
            subscription_running.add(subscriber.id)
            Thread(target=process_event, args=(subscriber,)).run()

def send_all_pending_events():
    """Attempts to send all pending events in subscriber order, not round-robin.   But
    that's OK, because it's just for testing."""
    subscribers = Subscriber.select()
    for subscriber in subscribers:
        while 1:
            if not process_event (subscriber):
                break
                

