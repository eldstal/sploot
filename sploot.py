#!/bin/env python3
#
# Sets up an HTTP server with various erroneous response patterns
#
# Request /double to get two responses
# Request /partial to get an incomplete response
#

import socket
import datetime
from threading import Thread

from scapy.supersocket import StreamSocket
from scapy.layers.http import *

IP="0.0.0.0"
INTERFACE="lo"
PORT=8080


def handle_client(host, port, conn):

    scapy_sock = StreamSocket(conn, HTTP)
    while True:

        try:
            req = scapy_sock.recv()
            if not req: break
        except EOFError:
            break
        except ConnectionResetError:
            break

        path = req["HTTP"].Path.decode()
        print(f"[{datetime.datetime.now()}]  {host} {port} {path}")

        if path == "/double":

            res1 = HTTP() / HTTPResponse() / "You've triggered a double-response attack.\n"
            res2 = HTTP() / HTTPResponse(Status_Code="403") / "Hard times have befallen you.\n"

            try:
                scapy_sock.send(bytes(res1) + bytes(res2))
            except:
                scapy_sock.close()
                break

        if path == "/partial":

            res1 = HTTP() / HTTPResponse() / "You've triggered a partial response.\n"
            res2 = HTTP() / HTTPResponse() / "This body isn't even transferred.\n"

            # Suggest a longer body, in case we can steal someone else's response
            res2["HTTP"].Content_Length = "1337"
            res2["HTTP"].X_Powered_By="This response was incomplete..."

            # Remove the delimiter and the body, leaving only the (unfinished) header block
            partial_res = bytes(res2)
            cutoff = partial_res.index(b"\r\n\r\n")
            partial_res = partial_res[:cutoff]

            #print(partial_res.decode())

            try:
                scapy_sock.send(bytes(res1) + partial_res)
            except:
                pass

            scapy_sock.close()
            break

        elif path == "/":

            res1 = HTTP() / HTTPResponse() / "OK, here's your content. Try /double or /partial for some more fun.\n"

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
        host, port = addr
        print(f"Connection from {addr}")

        t = Thread(target=handle_client, args=(host, port, conn))
        t.start()
        #handle_client(host, port, conn)


raw_socket_server()
