from pylons import Response, c, g, cache, request, session
from pylons.controllers import WSGIController
from pylons.decorators import jsonify, validate
from pylons.templating import render
from pylons.controllers.util import abort, redirect_to, etag_cache
from pylons.i18n import N_, _, ungettext
import cabochon.models as model
import cabochon.lib.helpers as h

from simplejson import loads, dumps
from paste.wsgiwrappers import WSGIResponse

class BaseController(WSGIController):
    def __call__(self, environ, start_response):
        # Insert any code to be run per request here. The Routes match
        # is under environ['pylons.routes_dict'] should you want to check
        # the action or route vars here

        if environ['pylons.routes_dict']['controller'] != 'admin':
            try:
                self.params = {}
                for param, value in request.params.items():
                    self.params[param] = loads(value)
            except ValueError:
                g.log("Bogus event %r" % request.params)
                #rejecting it won't help -- they'll just send it again
                return WSGIResponse(code=200, content='{"status" : "accepted"}') 
        return WSGIController.__call__(self, environ, start_response)

# Include the '_' function in the public names
__all__ = [__name for __name in locals().keys() if not __name.startswith('_') \
           or __name == '_']
