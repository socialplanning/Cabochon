from paste import httpexceptions

class BasicAuthMiddleware:
    def __init__(self, app, config):
        self.app = app
        
        self.not_set_up = False
        if not 'topp_admin_info_filename' in config:
            self.not_set_up = True
            return
        
        admin_file = config['topp_admin_info_filename']
        self.username, self.password = file(admin_file).read().strip().split(":")
        if len(self.admin_info) != 2:
            raise Exception("Bad format in administrator info file")
        
        self.username
        
    def __call__(self, environ, start_response):
        if self.not_set_up:
            return self.app(environ, start_response)

        if not 'HTTP_AUTHORIZATION' in environ:
            head = [('WWW-Authenticate', 'Basic realm="cabochon"')]
            return HTTPUnauthorized(headers=head)
            
        basic, encoded = environ['HTTP_AUTHORIZATION'].split(" ")
        if basic != "Basic": return False
        username, password = encoded.decode("base64").split(":")
        if not username == self.username and password == self.password:
            raise httpexceptions.HTTPForbidden("Access denied")
        
        environ['REMOTE_USER'] = username
        return self.app(environ, start_response)
