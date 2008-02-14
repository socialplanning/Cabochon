from cabochon.lib.basic_auth import BasicAuthMiddleware
from paste import httpexceptions
from paste.cascade import Cascade
from paste.urlparser import StaticURLParser
from paste.registry import RegistryManager
from paste.deploy.converters import asbool
from wsseauth import WSSEAuthMiddleware

from pylons import config
from pylons.error import error_template
from pylons.middleware import ErrorHandler, ErrorDocuments, StaticJavascripts, error_mapper
import pylons.wsgiapp

from cabochon.config.environment import load_environment
import cabochon.lib.helpers
import cabochon.lib.app_globals as app_globals

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
