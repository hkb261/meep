
#! /usr/bin/env python
import sys
import socket
import unittest
import meep_example_app
import urllib
import datetime
import signal
from cStringIO import StringIO

e = {}
outputStatus = ''
outputHeaders = []

def parse_Server_Line(l):
    global e
    parts = l.split()
    e['REQUEST_METHOD'] = parts[0]
    if len(parts) > 2:
        e['SERVER_PROTOCOL'] = parts[2]
    
    if parts[1].find('?') == -1:
        e['PATH_INFO'] = parts[1]
    else:
        url = parts[1].split('?')
        e['PATH_INFO'] = url[0]
        e['QUERY_STRING'] = url[1]

def parse_Host(l):
    values = l.split(': ')[1]
    parts = values.split(':')
    e['SERVER_NAME'] = parts[0]
    if len(parts) > 1:
        e['SERVER_PORT'] = parts[1]

def parse_other(l,key):
    e[key] = l.split(': ')[1]

def parse_http_header(l):
	try:
		key,value = l.split(': ')
		key = 'HTTP_%s' % (key.upper().replace('-','_'),)
		e[key] = value
	except:
		pass

def fake_start_response(status, headers):
	global outputStatus, outputHeaders
	outputStatus = status
	outputHeaders = headers

def process_Headers(data,ip,port):
	
	global e,outputStatus, outputHeaders
	
	#LOAD DEFAULTS
	e['SCRIPT_NAME'] = ''
	e['REQUEST_METHOD'] = 'GET'
	e['PATH_INFO'] = '/'
	e['QUERY_STRING'] = ''
	e['SERVER_PROTOCOL'] = 'HTTP/1.1'
	e['SERVER_NAME'] = socket.gethostbyaddr(ip)[0]
	e['SERVER_PORT'] = str(port)
	e['CONTENT_TYPE'] = 'text/html'
	e['CONTENT_LENGTH'] = '0'
	e['HTTP_COOKIE'] = ''
	
	lines = data.splitlines()
	for l in lines:
		if l.startswith('GET'):
			parse_Server_Line(l)
			e['CONTENT_LENGTH'] = '0'
		if l.startswith('POST'):
			parse_Server_Line(l)
		elif l.lower().startswith('content-type:'):
			parse_other(l,'CONTENT_TYPE')
		elif l.lower().startswith('host:'):
			parse_Host(l)
		elif l.lower().startswith('cookie'):
			parse_other(l,'HTTP_COOKIE')
		elif l.lower().startswith('content-length'):
                        parse_other(l,'CONTENT_LENGTH')
		else:
			parse_http_header(l)
	
	print 'processed headers:'
	for val in e:
		print '   %s: %s' % (val,e[val],)

def process_Request():
	global e,outputStatus, outputHeaders
	app = meep_example_app.MeepExampleApp()
	print 'processing'
	data = app(e, fake_start_response)
	output = []        
	output.append('%s %s\r\n' % (e['SERVER_PROTOCOL'], outputStatus))
	output.append('Date: %s EST\r\n' % datetime.datetime.now().strftime("%a, %d %b %Y %I:%M:%S"))
	output.append('Server: HaydensAwesomeServer/0.1 Python/2.5\r\n')
	for h in outputHeaders:
            output.append(h[0] + ': ' + h[1] + '\r\n')
            
        if len(data) > 0:
            output.append('Content-Length: %d\r\n\r\n' % (len(data[0]),))
            output.append(data[0])
        else:
            output.append('Content-Length: 0\r\n\r\n')

	return ''.join(output)

def encode_multipart_formdata(data):
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
        L.append(value)
    L.append('--' + BOUNDARY + '--')
    L.append('')
    body = CRLF.join(L)
    content_type = 'multipart/form-data; boundary=%s' % BOUNDARY
    return content_type, body

def handle_connection(sock):
    global e
    try:
        print 'data received from IP: %s' % (sock.getsockname()[0],)
        ip,port = sock.getsockname()
        
        allData = ''
        canCont = True
        while 1:
            data = sock.recv(2)
            allData += data
            if '\r\n\r\n' in allData:
                process_Headers(allData, ip, port)
                print 'content length: %d' % int(e['CONTENT_LENGTH'])
                if int(e['CONTENT_LENGTH']) > 0:
                    post = sock.recv(int(e['CONTENT_LENGTH']))
                    print 'read post data: %s' % post
                    content_type, body = encode_multipart_formdata(post)
                    e['CONTENT_TYPE'] = content_type
                    e['wsgi.input'] = StringIO(body)
                break

        sock.sendall(process_Request())
        
    except socket.error  as (errno, strerror):
        print "%d: %s" % (errno, strerror,)
    sock.close()

def startServer():
    interface, port = sys.argv[1:3]
    port = int(port)

	
    print 'binding', interface, port
    sock = socket.socket()
    sock.bind( (interface, port) )
    sock.listen(5)


    while 1:
        print 'waiting...'
	(client_sock, client_address) = sock.accept()
	print 'got connection', client_address
	handle_connection(client_sock)

    sock.close()

if __name__ == '__main__':
    startServer()
	
	

