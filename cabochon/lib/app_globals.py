from pylons import config
from logger import Logger

class Globals(object):
    def __init__(self):
        """
        Globals acts as a container for objects available throughout
        the life of the application.

        One instance of Globals is created by Pylons during
        application initialization and is available during requests
        via the 'g' variable.
        
        ``global_conf``
            The same variable used throughout ``config/middleware.py``
            namely, the variables from the ``[DEFAULT]`` section of the
            configuration file.
            
        ``app_conf``
            The same ``kw`` dictionary used throughout
            ``config/middleware.py`` namely, the variables from the
            section in the config file for your application.
            
        ``extra``
            The configuration returned from ``load_config`` in 
            ``config/middleware.py`` which may be of use in the setup of
            your global variables.
            
        """

        log_file = config.get('log_file')
        if log_file:
            self.log = Logger(log_file)
        else:
            self.log = lambda message: None
                
    def __del__(self):
        """
        Put any cleanup code to be run when the application finally exits 
        here.
        """
        pass

