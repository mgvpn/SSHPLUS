#!/usr/bin/env python2
import socket, threading, sys

IP = '0.0.0.0'
try:
    PORT = int(sys.argv[1])
except:
    PORT = 80

def handle_client(client_socket):
    try:
        request = client_socket.recv(4096)
        if not request:
            client_socket.close()
            return
        ssh_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ssh_socket.connect(('127.0.0.1', 22))
        ssh_socket.send(request)
        client_socket.settimeout(60)
        ssh_socket.settimeout(60)
        while True:
            try:
                data = client_socket.recv(8192)
                if not data:
                    break
                ssh_socket.send(data)
            except:
                break
            try:
                data = ssh_socket.recv(8192)
                if not data:
                    break
                client_socket.send(data)
            except:
                break
        ssh_socket.close()
        client_socket.close()
    except:
        client_socket.close()

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((IP, PORT))
    server.listen(100)
    print "Python WS activo en puerto %d" % PORT
    while True:
        client, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(client,))
        thread.start()

if __name__ == '__main__':
    main()