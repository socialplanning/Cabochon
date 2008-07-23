#!/usr/bin/python

#from sys import atexit
import BaseHTTPServer
import cgi
import urllib
from simplejson import loads
from pprint import pprint

class Handler(BaseHTTPServer.BaseHTTPRequestHandler):
    def _send_response(self):
        self.send_response(200, 'OK')
        self.wfile.write(
"""Content-Type: text/json

'{"status" : "accepted"}'""")

    def _print_query(self, query):
        for param, value in query.items():
            query[param] = loads(value[0])
        pprint(query)

    def do_GET(self):
        self._send_response()
        path, query = urllib.splitquery(self.path)
        query = cgi.parse_qs(query)
        self._print_query(query)

    def do_POST(self):
        query = cgi.parse_qs(self.rfile._rbuf)
        self._print_query(query)
        self._send_response()


server_address = ('', 8000)
httpd = BaseHTTPServer.HTTPServer(server_address, Handler)
httpd.serve_forever()
