class BasicAuthMiddleware:
    def __init__(self, app, config):
        self.app = app
        
        assert 'topp_admin_info_filename' in config
            
        admin_file = config['topp_admin_info_filename']
        self.username, self.password = file(admin_file).read().strip().split(":")

    def _fail(self, start_response):
        head = [('WWW-Authenticate', 'Basic realm="cabochon"')]
        start_response("401 Unauthorized", head)
        return ["Bad or no authentication."]

    def __call__(self, environ, start_response):
        if 'REMOTE_USER' in environ:
            return self.app(environ, start_response)

        if not 'HTTP_AUTHORIZATION' in environ:
            return self._fail(start_response)

        basic, encoded = environ['HTTP_AUTHORIZATION'].split(" ")

        if basic != "Basic": 
            return self._fail(start_response)
  
        username, password = encoded.decode("base64").split(":", 1)
        if not (username == self.username and password == self.password):
            return self._fail(start_response)

        environ = environ.copy()
        environ['REMOTE_USER'] = username
        return self.app(environ, start_response)
