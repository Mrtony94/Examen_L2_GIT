import os
import signal
import sys
from threading import Thread
import socket
import protocol
import json


class UsageError(Exception):
    def __init__(self):
        super().__init__("usage: python client.py name")


SERVER_IP = "127.0.0.1"
PORT = 6123


def argv():
    nombre = sys.argv[1]
    return nombre


def send_join():
    nombre = argv()
    msg = {'header':protocol.JOIN, 'name': nombre}
    protocol.send_one_message(client_socket, msg)


def send_msg():
    global end
    contenido = input(">> ")
    if contenido == "exit":
        print("Te has desconectado del chat")
        end = True
    else:
        msg = {'header': protocol.MSG, 'msg': contenido}
        protocol.send_one_message(client_socket, msg)


class HandlerThread(Thread):
    def __init__(self, client_socket):
        Thread.__init__(self)
        self.client_socket = client_socket
        self.stop = False

    def run(self):
        while not self.stop:
            try:
                msg = protocol.recv_one_message(self.client_socket)
                text = msg['msg']
                print(text)
                print(">> ", end="", flush=True)
            except KeyError:
                print("Unknow msg received")
            except protocol.InvalidProtocol as e:
                print(e)
            except KeyboardInterrupt:
                self.stop = True


try:
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((SERVER_IP, PORT))

    send_join()
    msg = protocol.recv_one_message(client_socket)
    valid = msg['valid']
    end = False
    if valid:
        print("Te has unido al chat")
        handler = HandlerThread(client_socket)
        handler.start()
        while not end:
            send_msg()
    else:
        print("Tu nombre de usuario ya está en uso")

except UsageError:
    print("Hay algo que huele mal")
except KeyboardInterrupt:
    print("Desconectado")
    os.kill(os.getpid(), signal.SIGTERM)