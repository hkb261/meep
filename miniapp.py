import sys
import unittest
import meep_example_app
import urllib
import datetime

e = {}
outputStatus = ''
outputHeaders = []

def parse_Server_Line(l):
    global e
    parts = l.split()
    e['REQUEST_METHOD'] = parts[0]
    if len(parts) > 2:
        e['SERVER_PROTOCOL'] = parts[2]
    else:
        e['SERVER_PROTOCOL'] = 'HTTP/1.1'
    
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
    
    

def fake_start_response(status, headers):
	global outputStatus, outputHeaders
	outputStatus = status
	outputHeaders = headers

if (len(sys.argv) < 2):
    print "Please provide a request file."
    sys.exit()
    
fileName = sys.argv[1]
fp = open(fileName)
data = fp.read()
fp.close()

global e,outputStatus, outputHeaders

e['SCRIPT-NAME'] = ''

lines = data.splitlines()
for l in lines:
    if l.startswith('GET'):
        parse_Server_Line(l)
        e['CONTENT_LENGTH'] = '0'
    if l.startswith('accept:'):
        parse_Content_Type(l)
    if l.startswith('host:'):
        parse_Host(l)
    if l.startswith('cookie'):
        parse_cookie(l)

app = meep_example_app.MeepExampleApp()

data = app(e, fake_start_response)

output = '%s %s\r\n' % (e['SERVER_PROTOCOL'], outputStatus)
output += 'Date: %s EST\r\n' % datetime.datetime.now().strftime("%a, %d %b %Y %I:%M:%S")
output += 'Server: HaydensAwesomeServer/0.1 Python/2.5\r\n'
output += 'Content-type: %s\r\n' % (e['CONTENT_TYPE'],)
output += 'Location: %s\r\n' % (e['PATH_INFO'],)
output += 'Content-Length: %d\r\n\r\n' % (len(data[0]),)
output += data[0]
print output
