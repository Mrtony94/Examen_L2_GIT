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
PORT = 6123

end = False


def get_name():
    import sys

    try:
        return sys.argv[1]
    except IndexError:
        raise UsageError()


def manage_msg():
    try:
        msg = protocol.recv_one_message(client_socket)
        header = msg['header']
        if header == protocol.ANSWER:
            sum = msg['sum']
            end = msg['end']
            win = msg['win']
            print(f"{sum}")
            return end, win
    except protocol.InvalidProtocol as e:
        print(e)


def send_join():
    msg = {'header': protocol.JOIN}
    protocol.send_one_message(client_socket, msg)


pid = os.getpid()
try:
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((SERVER_IP, PORT))
    send_join()

    end, win = manage_msg()

    while not end:
        print("1.- Continue\n2.- Exit\n")
        option = int(input("Choose an option: "))
        if option == 1:
            msg = {'header': protocol.REQUEST}
            protocol.send_one_message(client_socket, msg)
            end, win = manage_msg()
        elif option == 2:
            msg = {'header': protocol.END}
            protocol.send_one_message(client_socket, msg)

            msg = protocol.recv_one_message(client_socket)
            if msg['header'] == protocol.END:
                total = msg['sum']
                print(f"Total: {total}")
            else:
                print("ERROR: unknown message received")

            end = True

    print()  # esto no entiendo pa que es
    if win:
        print("You win!")
    else:
        print("You lose!")

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
