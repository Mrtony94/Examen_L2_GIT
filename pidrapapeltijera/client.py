import os
import signal
import socket
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


def join():
    valid_name = False
    while not valid_name:
        name = get_name()
        message = {'header': protocol.JOIN, 'name': name}
        protocol.send_one_message(client_socket, message)
        response = protocol.recv_one_message(client_socket)
        if response['header'] == protocol.WELCOME:
            valid_name = response['valid']
            answer = response['answer']
            if valid_name:
                print(answer)
                valid_name = True
            else:
                print(answer)
                stop = end_game()
                if stop:
                    valid_name = True


def handle_action():
    global action, end
    ok = False
    while not ok:
        action = input(f"Action>> ")
        if action.upper() == "EXIT":
            stop, answer = end_game()
            if stop:
                print(answer)
                ok = True
                end = True
        else:
            message = {'header': protocol.ACTION, 'action': action}
            protocol.send_one_message(client_socket, message)
            response = protocol.recv_one_message(client_socket)
            if response['header'] == protocol.VALID_MOVE:
                valid = response['valid']
                if valid:
                    answer = response['answer']
                    win = response['win']
                    winner = response['winner']
                    print(f"{winner} is {answer}")
                else:
                    print("Invalid action. Try again: ")


def end_game():
    global stop, answer
    message = {'header': protocol.END_GAME}
    protocol.send_one_message(client_socket, message)
    response = protocol.recv_one_message(client_socket)
    if response['header'] == protocol.END_GAME:
        stop = response['stop']
        answer = response['answer']
    return stop, answer


def menu():
    global end
    while not end:
        print("1. Send Action")
        print("2. Exit")
        command = int(input("Command>> "))
        if command == 1:
            handle_action()
        elif command == 2:
            end_game()
            end = True


pid = os.getpid()
try:
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((SERVER_IP, PORT))
    join()
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
