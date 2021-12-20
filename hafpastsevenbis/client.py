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


def send_join():
    msg = {'header': protocol.JOIN}
    protocol.send_one_message(client_socket, msg)


def send_request():
    msg = {'header': protocol.REQUEST}
    protocol.send_one_message(client_socket, msg)


def manage_answer(msg):
    global end
    sum = msg['suma']
    end = msg['end']
    win = msg['win']
    if end:
        if win:
            print(sum)
            print("You win!")
        else:
            print(sum)
            print("You lose!")
            end = True
    else:
        print(sum)


def manage_end(msg):
    global end
    sum = msg['suma']
    print(f"La suma total es --> {sum}")
    end = True


def send_end():
    msg = {'header': protocol.END}
    protocol.send_one_message(client_socket, msg)


def manage_msg():
    try:
        msg = protocol.recv_one_message(client_socket)
        header = msg['header']
        if header == protocol.ANSWER:
            manage_answer(msg)
        elif header == protocol.END:
            manage_end(msg)
    except protocol.InvalidProtocol as e:
        print(e)


def menu():
    print("1. Play")
    print("2. Exit")


try:
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((SERVER_IP, PORT))
    send_join()
    manage_msg()
    while not end:
        menu()
        option = input("Choose an option >> ")
        if option == "1":
            send_request()
        elif option == "2":
            send_end()
        else:
            raise UsageError()
        manage_msg()

except UsageError:
    raise
except Exception as e:
    print(e)
except KeyboardInterrupt:
    pass
finally:
    client_socket.close()
    os.kill(os.getpid(), signal.SIGTERM)
    print("Bye!")
    exit(0)
