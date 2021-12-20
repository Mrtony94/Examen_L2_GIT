import os
import signal
from threading import Thread
import socket
import protocol
import json

IP = "127.0.0.1"
PORT = 61000


clients = {}


class ClientThread(Thread):
    def __init__(self, client_socket, client_address):
        Thread.__init__(self)
        self.client_socket = client_socket
        self.client_address = client_address
        self.name = ""
        self.stop = False

    def handle_join(self, message):
        try:
            name = message['name']
            print(f"[JOIN] {name} from {self.client_address}")
            global clients
            accepted = True
            if name in clients:
                accepted = False
            else:
                self.name = name
                clients[name] = self.client_socket
            message = {'header': protocol.WELCOME, 'accepted': accepted}
            protocol.send_one_message(self.client_socket, message)
        except KeyError:
            raise protocol.InvalidProtocol

    def handle_msg(self, message):
        try:
            text = message['text']
            print(f"[MSG] {self.name}: {text}")
            global clients
            message = {'header': protocol.TEXT, 'text': f"{self.name}: {text}"}
            for name, to in clients.items():
                if name != self.name:
                    protocol.send_one_message(to, message)
                    print(f"Message sent to {name}")
        except KeyError:
            raise protocol.InvalidProtocol

    def handle_exit(self):
        global clients
        if self.name in clients:
            del clients[self.name]  # pop

    def handle_message(self, message):
        if message['header'] == protocol.JOIN:
            self.handle_join(message)
        elif message['header'] == protocol.TEXT:
            self.handle_msg(message)
        else:
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
                self.handle_exit()
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


pid = os.getpid() # get the pid of the current process
server_socket_thread = ServerSocketThread()
server_socket_thread.start()
try:
    stop = False
    while not stop:
        command = input()
        if command == "close":
            for name, recipient in clients.items():
                print(f"Connection with {name} client closed")
            stop = True
except KeyboardInterrupt:
    print("Server stopped by admin")
os.kill(pid, signal.SIGTERM)
