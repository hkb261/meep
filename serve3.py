
#! /usr/bin/env python
import sys
import socket
import signal
import threading
from RequestHandler import RequestHandler

def handle_connection(sock):
    while 1:
        try:
            print 'data received from IP: %s' % (sock.getsockname()[0],)
            ip,port = sock.getsockname()
        
            allData = ''
            while 1:
                data = sock.recv(1)
                if not data:
                    break
                allData += data
                if '\r\n\r\n' in allData:
                    if 'Content-Length' in allData:
                        start = allData.find('Content-Length: ')
                        end = allData.find('\r\n',start)
                        length = int(allData[start:end].split(': ')[1])
                        allData += sock.recv(length)
                    break

            reqHand = RequestHandler()
            sock.sendall(reqHand.process(allData, ip, port))
            sock.close()
            break
        except socket.error:
            break

        


def startServer():
    interface, port = sys.argv[1:3]
    port = int(port)

	
    print 'binding', interface, port
    sock = socket.socket()
    sock.bind( (interface, port) )
    sock.listen(2)

    
    while 1:
        print 'waiting...'
        (client_sock, client_address) = sock.accept()
        print 'got connection', client_address
        #handle_connection(client_sock)
        t = threading.Thread(target=handle_connection, args=(client_sock,))
        t.start()
    sock.close()


if __name__ == '__main__':
    startServer()
	
	

