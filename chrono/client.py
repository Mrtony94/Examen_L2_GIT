import os
import signal
import socket
import protocol


class UsageError(Exception):
    def __init__(self):
        super().__init__("usage: python client.py name")


SERVER_IP = "127.0.0.1"
PORT = 6123

end = False


def send_add_time():
    try:
        dorsal = input("Dorsal: ")
        time = input("Time: ")
        msg = {'header': protocol.ADD_TIME, 'dorsal': dorsal, 'time': time}
        protocol.send_one_message(client_socket, msg)
    except ValueError:
        print("Invalid time")


def manage_valid(valid):
    if valid:
        print("The time is Valid")

    else:
        print("The time is not Valid, try again")
        send_add_time()


def manage_best_time(msg):
    found = msg['found']
    dorsal = msg['dorsal']
    time = msg['time']
    if found:
        print("The best time is {} for dorsal {}".format(time, dorsal))
    else:
        print("the  list is empty")


def manage_msg():
    try:
        msg = protocol.recv_one_message(client_socket)
        header = msg['header']
        if header == protocol.VALID:
            valid = msg['valid']
            manage_valid(valid)
        elif header == protocol.BEST_TIME:
            manage_best_time(msg)
    except protocol.InvalidProtocol as e:
        print(e)


def send_best_time():
    msg = {'header': protocol.BEST_TIME}
    protocol.send_one_message(client_socket, msg)


def menu():
    menu = """ 1. Add time and dorsal
    2. Show best time
    3. Exit
    """
    return menu


pid = os.getpid()
try:
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((SERVER_IP, PORT))
    while not end:

        print(menu())
        option = int(input("Choose a option >>"))
        if option == 1:
            send_add_time()
        elif option == 2:
            send_best_time()
        elif option == 3:
            end = True
        if not end:
            manage_msg()
        else:
            break
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
