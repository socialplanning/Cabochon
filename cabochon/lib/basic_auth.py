from paste import httpexceptions

class BasicAuthMiddleware:
    def __init__(self, app, config):
        self.app = app
        
        self.not_set_up = False
        assert 'topp_admin_info_filename' in config
            
        admin_file = config['topp_admin_info_filename']
        self.username, self.password = file(admin_file).read().strip().split(":")        

        
    def __call__(self, environ, start_response):
        if 'REMOTE_USER' in environ:
            return self.app(environ, start_response)

        if not 'HTTP_AUTHORIZATION' in environ:
            head = [('WWW-Authenticate', 'Basic realm="cabochon"')]
            raise httpexceptions.HTTPUnauthorized(headers=head)
            
        basic, encoded = environ['HTTP_AUTHORIZATION'].split(" ")
        if basic != "Basic": return False
        username, password = encoded.decode("base64").split(":")
        if not (username == self.username and password == self.password):
            head = [('WWW-Authenticate', 'Basic realm="cabochon"')]
            raise httpexceptions.HTTPUnauthorized(headers=head)

        
        environ['REMOTE_USER'] = username
        return self.app(environ, start_response)
