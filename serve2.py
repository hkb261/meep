#! /usr/bin/env python
import sys
import socket
import unittest
import meep_example_app
import urllib
import datetime
import signal

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

def parse_Content_Type(l):
    values = l.split(': ')[1]
    types = values.split(',')
    e['CONTENT_TYPE'] = types[0]

def parse_Host(l):
    values = l.split(': ')[1]
    parts = values.split(':')
    e['SERVER_NAME'] = parts[0]
    if len(parts) > 1:
        e['SERVER_PORT'] = parts[1]

def parse_cookie(l):
    e['HTTP_COOKIE'] = l.split(': ')[1]

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

def process_incoming(data,ip,port):
	
	global e,outputStatus, outputHeaders
	
	#LOAD DEFAULTS
	e['SCRIPT_NAME'] = ''
	e['REQUEST_METHOD'] = 'GET'
	e['PATH_INFO'] = '/'
	e['QUERY_STRING'] = ''
	e['SERVER_PROTOCOL'] = 'HTTP/1.1'
	e['SERVER_NAME'] = socket.gethostbyaddr("69.59.196.211")
	e['SERVER_PORT'] = str(port)
	e['CONTENT_TYPE'] = 'text/plain'
	e['CONTENT_LENGTH'] = '0'
	e['HTTP_COOKIE'] = ''
	
	lines = data.splitlines()
	for l in lines:
		if l.startswith('GET'):
			parse_Server_Line(l)
			e['CONTENT_LENGTH'] = '0'
		elif l.lower().startswith('accept:'):
			parse_Content_Type(l)
		elif l.lower().startswith('host:'):
			parse_Host(l)
		elif l.lower().startswith('cookie'):
			parse_cookie(l)
		else:
			parse_http_header(l)
	
	print 'processed headers:'
	for val in e:
		print '   %s: %s' % (val,e[val],)
	
	app = meep_example_app.MeepExampleApp()
	print 'processing'
	data = app(e, fake_start_response)
	output = '%s %s\r\n' % (e['SERVER_PROTOCOL'], outputStatus)
	output += 'Date: %s EST\r\n' % datetime.datetime.now().strftime("%a, %d %b %Y %I:%M:%S")
	output += 'Server: HaydensAwesomeServer/0.1 Python/2.5\r\n'
	output += 'Content-type: %s\r\n' % (e['CONTENT_TYPE'],)
	output += 'Location: %s\r\n' % (e['PATH_INFO'],)
	if len(data) > 0:
		output += 'Content-Length: %d\r\n\r\n' % (len(data[0]),)
		output += data[0]
	else:
		output += 'Content-Length: 0\r\n\r\n'
	print 'done'
	return output

def handle_connection(sock):
    while 1:
        try:
            data = sock.recv(4096)
            if not data:
                break
                    
            print 'data received from IP: ', (sock.getsockname(),)
            ip,port = sock.getsockname()
            sock.sendall(process_incoming(data, ip, port))
            sock.close()
            break
        except socket.error:
            print 'error'
            break

if __name__ == '__main__':
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

