from cabochon.models import *
from threading import Thread, enumerate, Lock

import traceback
import time
from cabochon.lib.logger import Logger

MAX_THREADS = 10
    
class EventSenderThread(Thread):

    def __init__(self):
        self._lock = Lock()
        self.subscribers = dict((x.id, x.pending_events) for x in Subscriber.select())
        Thread.__init__(self)
        self.setDaemon(True)
        
    def process_event(self, subscriber):
        try:
            try:
                try:
                    self._lock.acquire()                    
                    subscribers = self.subscribers[subscriber]
                    if not len(subscribers):
                        return
                    top_event = subscribers[0]
                finally:
                    self._lock.release()                    

                response = top_event.handle()
                if not response: #yes, response is backwards on purpose
                    self.log ("Sent event to %s" % top_event.subscriber.url)
                    top_event.destroySelf()
                    self.subscribers[subscriber] = self.subscribers[subscriber][1:]
                else:
                    self.log ("Failed sending event event to %s " % top_event.subscriber.url)

                    top_event.last_response = "%s %s" % response
                    top_event.failures += 1
                    return False # failed to handle one

                return True #handled one successfully
            except KeyboardInterrupt:
                interrupt_main()
            except Exception, e:
                traceback.print_exc()
        finally:
            if subscriber in self.subscription_running:
                self.subscription_running.remove(subscriber)


    def add_subscriber(self, subscriber):
        self._lock.acquire()
        self.subscribers[subscriber.id] = []
        self._lock.release()

    def add_pending_event(self, subscriber, event):
        self._lock.acquire()        
        self.subscribers[subscriber.id].append(event)
        self._lock.release()

    def event_queue_empty(self):
        self._lock.acquire()                
        result = not bool(sum(map(len, self.subscribers.values())))
        self._lock.release()
        return result
        
    def run(self):
        self.running = True
        self.subscription_running = set()
        self.log = Logger("send_log")
        while self.running:
            
            for subscriber, queue in self.subscribers.items():
                if subscriber in self.subscription_running:
                    continue
                if not len(queue):
                    continue
                while len(self.subscription_running) > MAX_THREADS:
                    time.sleep(0.00001)
                self.subscription_running.add(subscriber)
                Thread(target=self.process_event, args=(subscriber,)).run()
            time.sleep(0.00001)
        
    def stop(self):
        self.running = False
        
def init_sender_threads():
    #kill old threads.
    for thread in enumerate():
        if isinstance(thread, EventSenderThread):
            thread.stop()
            thread.join()
    est = EventSenderThread()
    est.start()
    return est
