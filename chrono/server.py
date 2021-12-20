import os
import signal
from threading import Thread
import socket
import protocol
import json

IP = "127.0.0.1"
PORT = 6123
dorsal_time = []


# def valid_time(dorsal, time):
#     valid = False
#     if len(time) == 8:
#         x = time.split(":")
#         if len(x) == 3:
#             if x[0].isdigit() and x[1].isdigit() and x[2].isdigit():
#                 if 0 <= int(x[0]) <= 9999999 and 0 <= int(x[1]) <= 59 and 0 <= int(x[2]) <= 59:
#                     valid = True
#                 else:
#                     print("Invalid time")
#                     valid = False
#             else:
#                 print("Invalid time")
#                 valid = False
#         else:
#             print("Invalid time")
#             valid = False
#     else:
#         print("Invalid time")
#         valid = False
#     return valid


def valid_time(dorsal, time):
    global valid
    if int(dorsal) <= 0:
        valid = False
    else:
        if len(time) != 8:
            valid = False
        else:
            x = time.split(":")
            if len(x) == 3:
                if int(x[0]) < 24 and int(x[1]) < 60 and int(x[2]) < 60:
                    print("Time valid")
                    valid = True
                else:
                    valid = False
    return valid


class ClientThread(Thread):
    def __init__(self, client_socket, client_address):
        Thread.__init__(self)
        self.client_socket = client_socket
        self.client_address = client_address
        self.stop = False
        self.valid = True

    def add_time(self, message):
        dorsal = message['dorsal']
        time = message['time']
        print(f"[ADD_TIME] reveived Dorsal --> {dorsal} Time --> {time}")
        valid = valid_time(dorsal, time)
        print(f"[ADD_TIME] dorsal and time are valid {valid}")
        dorsal_time.append((dorsal, time))
        message = {'header': protocol.VALID, 'valid': valid}
        protocol.send_one_message(self.client_socket, message)

    def best_time(self):
        print(f"[BEST_TIME] received")
        if len(dorsal_time) == 0:
            found = False
            message = {'header': protocol.BEST_TIME, 'found': found, 'dorsal': dorsal_time[0][0],
                       'time': dorsal_time[0][1]}
        else:
            found = True
            dorsal_time.sort(key=lambda x: x[1])
            message = {'header': protocol.BEST_TIME, 'found': found, 'dorsal': dorsal_time[0][0],
                       'time': dorsal_time[0][1]}
        protocol.send_one_message(self.client_socket, message)

    def handle_message(self, message):
        try:
            header = message['header']
            if header == protocol.ADD_TIME:
                self.add_time(message)
            elif header == protocol.BEST_TIME:
                self.best_time()
            else:
                raise protocol.InvalidProtocol
        except KeyError:
            raise protocol.InvalidProtocol

    def run(self):
        print(f"Connection received from {self.client_address}")
        while not self.stop:
            try:
                message = protocol.recv_one_message(self.client_socket)
                self.handle_message(message)
            except protocol.InvalidProtocol as e:
                print(e)
            except protocol.ConnectionClosed:
                self.stop = True


class ServerSocketThread(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.server_socket.bind((IP, PORT))
        self.server_socket.listen()

    def run(self):
        ip, port = self.server_socket.getsockname()
        print(f"Server listening on ({ip}, {port})...")
        while True:
            client_socket, client_address = self.server_socket.accept()
            client_thread = ClientThread(client_socket, client_address)
            client_thread.start()


pid = os.getpid()  # get the pid of the current process
server_socket_thread = ServerSocketThread()
server_socket_thread.start()
try:
    stop = False
    while not stop:
        command = input('>>')
        if command == 'c' or 'C':
            stop = True
except KeyboardInterrupt:
    print("Server stopped by admin")
except ConnectionResetError:
    print("Server stopped by admin")
os.kill(pid, signal.SIGTERM)
