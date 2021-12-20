import os
import signal
from threading import Thread
import socket
import protocol
import json

IP = "127.0.0.1"
PORT = 6123

card = []
result = []
limit = 7.5


class ClientThread(Thread):
    def __init__(self, client_socket, client_address):
        Thread.__init__(self)
        self.client_socket = client_socket
        self.client_address = client_address
        self.suma = 0
        self.stop = False

    def manage_number(self, numbers):
        print(f"[NUMBER] {self.client_address} JOINED")
        print(f"{numbers}")
        self.suma = numbers[0] + numbers[1]
        message = {'header': protocol.NUMBER_REPLY, 'sum': self.suma}
        protocol.send_one_message(self.client_socket, message)
        print(f"[NUMBER_REPLY] send to{self.suma} {self.client_address}")

    def manage_string(self, string):
        print(f"[STRING] {self.client_address} RECEIVED")
        print(f"{string}")
        cadena = string[1] + string[0]
        message = {'header': protocol.STRING_REPLY, 'cadena': cadena}
        protocol.send_one_message(self.client_socket, message)
        print(f"[STRING_REPLY] send to{cadena} {self.client_address}")

    def handle_message(self, message):
        try:
            message_header = message['header']
            if message_header == protocol.NUMBER:
                numbers = message['number']
                self.manage_number(numbers)
            elif message_header == protocol.STRING:
                string = message['string']
                self.manage_string(string)
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
        command = input()
except KeyboardInterrupt:
    print("Server stopped by admin")
os.kill(pid, signal.SIGTERM)



