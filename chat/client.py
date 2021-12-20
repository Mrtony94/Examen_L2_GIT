import os
from threading import Thread
import socket
import protocol
import sys


class UsageError(Exception):
    def __init__(self):
        super().__init__("usage: python client.py name")


SERVER_IP = "127.0.0.1"
PORT = 6123

end = False


def send_join():
    try:
        name = sys.argv[1]
        msg = {'header': protocol.JOIN, 'name': name}
        protocol.send_one_message(client_socket, msg)
    except ValueError:
        print("Invalid name")


class HandlerThread(Thread):
    def __init__(self, client_socket):
        Thread.__init__(self)
        self.client_socket = client_socket
        self.stop = False

    def run(self):
        while not self.stop:
            try:
                message = protocol.recv_one_message(self.client_socket)
                header = message['header']
                if header == protocol.MSG:
                    text = message['msg']
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
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((SERVER_IP, PORT))
    send_join()
    try:
        msg = protocol.recv_one_message(client_socket)
        header = msg['header']
        if header == protocol.WELCOME:
            valid = msg['valid']
            print(f"{valid} Welcome to the chat room!")
            if valid:
                print("You are now connected to the server")
                handler = HandlerThread(client_socket)
                handler.start()
                while not end:
                    msg = input(">> ")
                    if msg == "exit":
                        print("Disconnecting from server")
                        end = True
                        break
                    else:
                        msg = {'header': protocol.MSG, 'msg': msg}
                        protocol.send_one_message(client_socket, msg)
            else:
                print("Invalid name")
                end = True
    except protocol.InvalidProtocol as e:
        print(e)

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
# os.kill(pid, signal.SIGTERM)
