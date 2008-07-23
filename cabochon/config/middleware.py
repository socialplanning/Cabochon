from cabochon.lib.basic_auth import BasicAuthMiddleware
from paste import httpexceptions
from paste.cascade import Cascade
from paste.urlparser import StaticURLParser
from paste.registry import RegistryManager
from paste.deploy.converters import asbool
from supervisorerrormiddleware import SupervisorErrorMiddleware
from wsseauth import WSSEAuthMiddleware

from pylons import config
from pylons.error import error_template
from pylons.middleware import ErrorHandler, ErrorDocuments, StaticJavascripts, error_mapper
import pylons.wsgiapp

from cabochon.config.environment import load_environment
from cabochon.models import *
import cabochon.lib.helpers
import cabochon.lib.app_globals as app_globals

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


def make_app(global_conf, full_stack=True, **app_conf):
    """Create a Pylons WSGI application and return it

    ``global_conf``
        The inherited configuration for this application. Normally from
        the [DEFAULT] section of the Paste ini file.

    ``full_stack``
        Whether or not this application provides a full WSGI stack (by
        default, meaning it handles its own exceptions and errors).
        Disable full_stack when this application is "managed" by
        another WSGI middleware.

    ``app_conf``
        The application's local configuration. Normally specified in the
        [app:<name>] section of the Paste ini file (where <name>
        defaults to main).
    """

    # Load our Pylons configuration defaults
    load_environment(global_conf, app_conf)



    # initialize list of subscribers
    subscriber_list_filename = config.get('subscriber_list_filename')
    if subscriber_list_filename is not None:
        try:
            f = open(subscriber_list_filename)
            for line in f:
                line = line.strip()
                event, subscriber = line.split()[:2]
                assert subscriber.startswith("http"), "Subscriber url must start with http: '%s'" % subscriber
                subscribe_by_name(event, subscriber)
        except IOError:
            pass

        
    # Load our default Pylons WSGI app and make g available
    app = pylons.wsgiapp.PylonsApp()

    try:
        f = open(config["password_file"])
        config['username'], config['password'] = f.read().strip().split(":")
        f.close()
    except IOError:
        pass

    from cabochon.lib.event_queue import init_sender_threads
    app.globals.event_sender = init_sender_threads()
    
    # YOUR MIDDLEWARE
    # Put your own middleware here, so that any problems are caught by the error
    # handling middleware underneath

    if 'topp_admin_info_filename' in config:
        app = BasicAuthMiddleware(app, config)

    #optional security
    username = config.get('username', None)
    password = config.get('password', None)
    if username:
        #If there is no administrative info, the only means of
        #authentication is WSSE
        required = not 'topp_admin_info_filename' in config    
        app = WSSEAuthMiddleware(app, {username : password}, required=required)
            
    app = SupervisorErrorMiddleware(app)

    # If errror handling and exception catching will be handled by middleware
    # for multiple apps, you will want to set full_stack = False in your config
    # file so that it can catch the problems.
    if asbool(full_stack):
        # Change HTTPExceptions to HTTP responses
        app = httpexceptions.make_middleware(app, global_conf)
    
        # Error Handling
        app = ErrorHandler(app, global_conf, error_template=error_template, **config['pylons.errorware'])
    
        # Display error documents for 401, 403, 404 status codes (if debug is disabled also
        # intercepts 500)
        #app = ErrorDocuments(app, global_conf, mapper=error_mapper, **app_conf)
    
    # Establish the Registry for this application
    app = RegistryManager(app)
    
    static_app = StaticURLParser(config['pylons.paths']['static_files'])
    javascripts_app = StaticJavascripts()
    app = Cascade([static_app, javascripts_app, app])
    return app
