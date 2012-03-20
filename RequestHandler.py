#! /usr/bin/env python

import sys
import socket
import unittest
import meep_example_app
import urllib
import datetime
import signal
from cStringIO import StringIO

class ResponseFunctionHolder(object):
    def __call__(self, status, headers):
        self.status = status
        self.headers = headers

class RequestHandler(object):
    def process(self, data, ip, port):
        self.e = {}
        self.e['SCRIPT_NAME'] = ''
	self.e['REQUEST_METHOD'] = 'GET'
	self.e['PATH_INFO'] = '/'
	self.e['QUERY_STRING'] = ''
	self.e['SERVER_PROTOCOL'] = 'HTTP/1.1'
	self.e['SERVER_NAME'] = socket.gethostbyaddr(ip)[0]
	self.e['SERVER_PORT'] = str(port)
	self.e['CONTENT_TYPE'] = 'text/html'
	self.e['CONTENT_LENGTH'] = '0'
	self.e['HTTP_COOKIE'] = ''

        sections = data.split('\r\n\r\n')
	headers = sections[0].splitlines()
	for h in headers:
	    if h.startswith('GET') or h.startswith('POST'):
                self._parse_Server_Line(h)
            elif h.lower().startswith('content-type:'):
                self._parse_other(h,'CONTENT_TYPE')
            elif h.lower().startswith('host:'):
                self._parse_Host(h)
            elif h.lower().startswith('cookie'):
                self._parse_other(h,'HTTP_COOKIE')
            elif h.lower().startswith('content-length'):
                self._parse_other(h,'CONTENT_LENGTH')
            else:
		self._parse_http_header(h)

	if len(sections) > 1 and self.e['REQUEST_METHOD'] == 'POST':
            post = sections[1]
            print 'POST DATA: %s' % post
            content_type, body = self._encode_multipart_formdata(post)
            self.e['CONTENT_TYPE'] = content_type
            self.e['wsgi.input'] = StringIO(body)

        return self._process_request()


    def _process_request(self):
	app = meep_example_app.MeepExampleApp()
	print 'processing'
	response_fn_callable = ResponseFunctionHolder()
	data = app(self.e, response_fn_callable)
	output = []        
	output.append('%s %s\r\n' % (self.e['SERVER_PROTOCOL'], response_fn_callable.status))
	output.append('Date: %s EST\r\n' % datetime.datetime.now().strftime("%a, %d %b %Y %I:%M:%S"))
	output.append('Server: HaydensAwesomeServer/0.1 Python/2.7\r\n')
	for h in response_fn_callable.headers:
            output.append(h[0] + ': ' + h[1] + '\r\n')
            
        if len(data) > 0:
            output.append('Content-Length: %d\r\n\r\n' % (len(data[0]),))
            output.append(data[0])
        else:
            output.append('Content-Length: 0\r\n\r\n')

        print 'returning'
	return ''.join(output)

    def _parse_Server_Line(self, l):
        parts = l.split()
        self.e['REQUEST_METHOD'] = parts[0]
        if len(parts) > 2:
            self.e['SERVER_PROTOCOL'] = parts[2]
        
        if parts[1].find('?') == -1:
            self.e['PATH_INFO'] = parts[1]
        else:
            url = parts[1].split('?')
            self.e['PATH_INFO'] = url[0]
            self.e['QUERY_STRING'] = url[1]

    def _parse_Host(self, l):
        values = l.split(': ')[1]
        parts = values.split(':')
        self.e['SERVER_NAME'] = parts[0]
        if len(parts) > 1:
            self.e['SERVER_PORT'] = parts[1]

    def _parse_other(self, l,key):
        self.e[key] = l.split(': ')[1]

    def _parse_http_header(self, l):
	try:
            key,value = l.split(': ')
            key = 'HTTP_%s' % (key.upper().replace('-','_'),)
	    self.e[key] = value
	except:
		pass


    def _encode_multipart_formdata(self, data):
        fields = []
        for s in data.split('&'):
            fields.append(s.split('='))
        print 'FIELDS: %s' % fields
        BOUNDARY = '----------HeyImABoundarY_$'
        CRLF = '\r\n'
        L = []
        for (key, value) in fields:
            L.append('--' + BOUNDARY)
            L.append('Content-Disposition: form-data; name="%s"' % key)
            L.append('')
            L.append(urllib.unquote(value.replace('+',' ')))
        L.append('--' + BOUNDARY + '--')
        L.append('')
        body = CRLF.join(L)
        content_type = 'multipart/form-data; boundary=%s' % BOUNDARY
        return content_type, body
