from cabochon.lib.basic_auth import BasicAuthMiddleware
from os import fdopen

import tempfile
from paste import httpexceptions

def test_basic_auth():
    fd, filename = tempfile.mkstemp()
    f = fdopen(fd, "w")
    f.write("admin:pw2")
    f.close()

    def success_app(environ, start_response):
        assert environ['REMOTE_USER'] == 'admin'
        return []

    config = {'topp_admin_info_filename' : filename}
    middleware = BasicAuthMiddleware(success_app, config)

    environ = {}
    encoded = ":".join(["admin", "pw2"]).encode("base64")
    environ['HTTP_AUTHORIZATION'] = "Basic %s" % encoded
    assert middleware(environ, None) == []

    encoded = ":".join(["admin", "wrong"]).encode("base64")
    environ['HTTP_AUTHORIZATION'] = "Basic %s" % encoded
    middleware = BasicAuthMiddleware(success_app, config)

    response = [None]
    def start_response(code, headers):
        assert code == "401 Unauthorized"
        assert headers == [('WWW-Authenticate', 'Basic realm="cabochon"')]
        response[0] = 1
    middleware(environ, start_response)
    assert response[0] == 1
