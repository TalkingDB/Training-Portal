'''
Created on 27-Jan-2015

@author: sb
'''
import socket
def sendPacketOverSocket(host,port,data):
#     try:
    sock = socket.socket()
    sock.connect((host, port))
    
    sock.send(data)

    #Iterator applied to receive chunks of data over socket
    buf = ''
    while True:
        chunk = sock.recv(4096)
        if not chunk:
            break
        else:
            buf += chunk
#     print buf
    return buf
#     except UnicodeDecodeError:
#         print data + ' is a unicode string'
#     except Exception as e:
#         print e
