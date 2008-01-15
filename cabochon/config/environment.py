import os

from pylons import config
import cabochon.lib.app_globals as app_globals

from cabochon.config.routing import make_map

class ConfigError(Exception): pass

from cabochon.models import *

def subscribe_by_name(event, url):
    """Subscribe a given URL to the event with the given name."""
    try:
        event_type = EventType.selectBy(name=event)[0]
    except IndexError:
        event_type = EventType(name=event)

    subscriber = Subscriber.selectBy(event_type=event_type, url=url)
    try:
        subscriber = subscriber[0]
        subscriber.set(url=url)
    except IndexError:
        subscriber = Subscriber(event_type=event_type, url=url, method="POST")


def load_environment(global_conf={}, app_conf={}):

    # Setup our paths
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    paths = {'root': root,
             'controllers': os.path.join(root, 'controllers'),
             'templates': [os.path.join(root, path) for path in \
                           ('components', 'templates')],
             'static_files': os.path.join(root, 'public')
             }


    # Initialize config with the basic options
    config.init_app(global_conf, app_conf, package='cabochon',
                    template_engine='mako', paths=paths)

    config['routes.map'] = make_map()    
    config['pylons.g'] = app_globals.Globals()
    import cabochon.lib.helpers
    config['pylons.h'] = cabochon.lib.helpers
    
    # Add your own template options config options here, note that all
    # config options will override any Pylons config options


    # initialize list of subscribers
    subscriber_list_filename = config.get('subscriber_list_filename')
    if subscriber_list_filename is not None:
        try:
            f = open(subscriber_list_filename)
            for line in f:
                line = line.strip()
                event, subscriber = line.split()[:2]
                subscribe_by_name(event, subscriber)
        except IOError:
            pass
