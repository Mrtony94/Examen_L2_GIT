import os
import signal
from threading import Thread
import socket
import protocol
import json


class UsageError(Exception):
    def __init__(self):
        super().__init__("usage: python client.py name")


SERVER_IP = "127.0.0.1"
PORT = 61000


def get_name():
    import sys

    try:
        return sys.argv[1]
    except IndexError:
        raise UsageError()


end = False


class HandlerThread(Thread):
    def __init__(self, client_socket):
        Thread.__init__(self)
        self.client_socket = client_socket
        self.stop = False

    def run(self):
        while not self.stop:
            try:
                message = protocol.recv_one_message(self.client_socket)

                text = message['text']
                print()
                print(text)
                print(">> ", end="", flush=True)
            except KeyError:
                print("Unknown message received")
            except protocol.InvalidProtocol as e:
                print(e)
            except protocol.ConnectionClosed:
                global end
                end = True
                self.stop = True


pid = os.getpid()
try:
    name = get_name()

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((SERVER_IP, PORT))

    message = {'header': protocol.JOIN, 'name': name}
    protocol.send_one_message(client_socket, message)

    message = protocol.recv_one_message(client_socket)
    accepted = message['accepted']
    if accepted:
        print("Welcome to PST-Chat")
        handler = HandlerThread(client_socket)
        handler.start()

        while not end:
            text = input(">> ")
            if text == "exit":
                print("Thanks for using PST-Chat")
                end = True
            else:
                message = {'header': protocol.TEXT, 'text': text}
                protocol.send_one_message(client_socket, message)
    else:
        print(f"[PST-Chat] name {name} already exists")
except KeyError:
    print("ERROR: invalid message's fragment received")
except UsageError as e:
    print(e)
except protocol.InvalidProtocol as e:
    print(e)
except protocol.ConnectionClosed:
    print("Connection closed by the server")
except ConnectionError:
    print("Could not connect to the server. Is the server alive?")
os.kill(pid, signal.SIGTERM)
