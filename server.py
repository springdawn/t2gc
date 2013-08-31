import SimpleHTTPServer
from urlparse import urlparse
import urllib2


class GetHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    def do_GET(self):
        getpath = urlparse(self.path)
        print urllib2.unquote(getpath.query)

httpd = SimpleHTTPServer.BaseHTTPServer.HTTPServer(
    ('localhost', 8000), GetHandler)
print httpd.server_name, httpd.server_port
httpd.serve_forever()
