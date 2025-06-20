#!/bin/env python3

import socket
from scapy.supersocket import StreamSocket
from scapy.layers.http import *

IP="127.0.0.1"
INTERFACE="lo"
PORT=8080


def handle_client(conn):

    scapy_sock = StreamSocket(conn, HTTP)
    while True:

        try:
            req = scapy_sock.recv()
            if not req: break
        except EOFError:
            break
        except ConnectionResetError:
            break

        if req["HTTP"].Path == b"/trigger":

            res1 = HTTP() / HTTPResponse() / "You've triggered an attack.\n"
            res2 = HTTP() / HTTPResponse() / "This wasn't meant for anyone.\n"

            try:
                scapy_sock.send(bytes(res1) + bytes(res2))
            except:
                scapy_sock.close()
                break

        elif req["HTTP"].Path == b"/":

            res1 = HTTP() / HTTPResponse() / "OK, here's your content. Try /trigger for some more fun.\n"

            try:
                scapy_sock.send(bytes(res1))
            except:
                scapy_sock.close()
                break
        else:

            res1 = HTTP() / HTTPResponse(Status_Code="404", Reason_Phrase="Not found") / "Not here.\n"

            try:
                scapy_sock.send(res1)
            except:
                scapy_sock.close()
                break




def raw_socket_server():

	server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

	server.bind((IP, PORT))
	server.listen(1)

	while True:
	    conn, addr = server.accept()
	    print(f"Connection from {addr}")
	    handle_client(conn)


raw_socket_server()
