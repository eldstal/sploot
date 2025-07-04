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

KEEPALIVE="timeout=600, max=0"


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

        query = req["HTTP"].Path.decode()
        print(f"[{datetime.datetime.now()}]  {host} {port} {query}")

        path = query.split("?")[0]
        params = ""
        if "?" in query:
            params = query.split("?")[1]


        if path == "/two":

            # Two consecutive responses

            res1 = HTTP() / HTTPResponse(Keep_Alive=KEEPALIVE) / f"First={params}\n"
            res2 = HTTP() / HTTPResponse(Keep_Alive=KEEPALIVE) / f"Hard times have befallen you.\n"

            try:
                #scapy_sock.send(bytes(res1) + bytes(res2))
                scapy_sock.send(bytes(res1))
                scapy_sock.send(bytes(res2))
            except:
                scapy_sock.close()
                break

        elif path == "/double":
            # Two responses in a single packet (probably)

            res1 = HTTP() / HTTPResponse(Keep_Alive=KEEPALIVE) / f"First={params}\n"
            res2 = HTTP() / HTTPResponse(Keep_Alive=KEEPALIVE) / "Hard times have befallen you.\n"

            try:
                scapy_sock.send(bytes(res1) + bytes(res2))
            except:
                scapy_sock.close()
                break

        elif path == "/partial":

            res1 = HTTP() / HTTPResponse(Keep_Alive=KEEPALIVE) / f"Partial={params}.\n"
            res2 = HTTP() / HTTPResponse(Keep_Alive=KEEPALIVE) / "This body isn't even transferred.\n"

            # Suggest a longer body, in case we can steal someone else's response
            res2["HTTP"].Content_Length = "1337"
            res2["HTTP"].X_Powered_By="This response was incomplete..."

            # Remove the delimiter and the body, leaving only the (unfinished) header block
            partial_res = bytes(res2)
            cutoff = partial_res.index(b"\r\n\r\n")
            partial_res = partial_res[:cutoff]

            try:
                scapy_sock.send(bytes(res1) + partial_res)
            except:
                pass

            scapy_sock.close()
            break

        elif path == "/":

            res1 = HTTP() / HTTPResponse(Keep_Alive=KEEPALIVE) / f"Normal={params}\n"

            try:
                scapy_sock.send(bytes(res1))
            except:
                scapy_sock.close()
                break
        else:

            print(f"404! \"{path}\"")
            req.show()

            res1 = HTTP() / HTTPResponse(Status_Code="404", Reason_Phrase="Not found", Keep_Alive=KEEPALIVE) / "Not here.\n"

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
