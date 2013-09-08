# This Python file uses the following encoding: utf-8

from ns import *
import SimpleHTTPServer
from urlparse import urlparse, parse_qsl
import urllib2
from googleCalendar import GoogleCalendar
jst = '+0900'


class GetHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    def do_GET(self):
        getpath = urlparse(self.path)
        unquotedquery = urllib2.unquote(getpath.query)
        querydict = dict(parse_qsl(unquotedquery))
        datestring = querydict['date'] if 'date' in querydict else ''
        if not datestring:
            self.send_error(400, 'date is required')
            return
        start_time = ''
        if 'start' in querydict:
            start_time = datestring + 'T' + querydict['start'] + ':00' + jst
        end_time = ''
        if start_time and 'end' in querydict:
            end_time = datestring + 'T' + querydict['end'] + ':00' + jst
        elif start_time:
            end_time = (start_time[:11] +
                        str(int(start_time[11:13]) + 1).zfill(2) +
                        start_time[13:])
        req = {
            'title': querydict['title'] if 'title' in querydict else None,
            'location': querydict['location']
            if 'location' in querydict else None,
            'start': start_time if start_time else None,
            'end': end_time if end_time else None,
            'date': datestring if not start_time and not end_time else None
        }
        res = gc.createEvent(req)
        if not res:
            res = gc.createEvent(req)
        self.wfile.write('ok ' + res)


def createServer():
    httpd = SimpleHTTPServer.BaseHTTPServer.HTTPServer(
        ('localhost', 8000), GetHandler)
    print httpd.server_name, httpd.server_port
    httpd.serve_forever()

gc = GoogleCalendar()
gc.connect()
createServer()
