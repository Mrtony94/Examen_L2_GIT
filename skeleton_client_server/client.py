import os
import signal
import socket
import sys

import protocol
from threading import Thread


class UsageError(Exception):
    def __init__(self):
        super().__init__("usage: python client.py name")


SERVER_IP = "127.0.0.1"
PORT = 6123

end = False


############################# HILO 1 ##########################################
#                                                                             #
#                                                                             #
#                                                                             #

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
                print(">> ", end="", flush=True)
            except KeyError:
                print("Unknown message received")
            except protocol.InvalidProtocol as e:
                print(e)
            except protocol.ConnectionClosed:
                global end
                end = True
                self.stop = True


#                                                                             #
#                                                                             #
#                                                                             #
###############################################################################

def get_name():
    name = input("Enter your name: ")
    return name


def argv_name():
    try:
        return sys.argv[1]
    except IndexError:
        raise UsageError()


def send_join():
    name = get_name()
    # name = argv_name()
    message = {'header': protocol.JOIN, 'name': name}
    protocol.send_one_message(client_socket, message)


def handle_welcome(message):
    valid = message['valid']
    if valid:
        print("Welcome to the chat!")
    else:
        print("Username already in use")
        send_join()
        menu()


def send_end():
    message = {'header': protocol.END}
    protocol.send_one_message(client_socket, message)


def handle_end(message):
    global stop, answer
    stop = message['stop']
    answer = message['answer']
    return stop, answer


def handle_message():
    message = protocol.recv_one_message(client_socket)
    try:
        header = message['header']
        if header == protocol.WELCOME:
            handle_welcome(message)
        elif header == protocol.END_GAME:
            handle_end(message)
        else:
            raise protocol.InvalidProtocol
    except KeyError:
        raise protocol.InvalidProtocol


def menu():
    global end
    while not end:
        menu = """--- MENU ---
1. Send a message
3. Exit
"""
        print(menu)
        command = int(input("Command>> "))
        if command == 1:
            pass
        elif command == 2:
            send_end()
            stop, answer = handle_message()
            if stop:
                end = True
                print(f"{answer}")


pid = os.getpid()
try:
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((SERVER_IP, PORT))
    send_join()
    menu()
    print()
    print("Bye!")
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
