import os

from pylons import config
import cabochon.lib.app_globals as app_globals

from cabochon.config.routing import make_map

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
