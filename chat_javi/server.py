import os
import random
import signal
from threading import Thread
import socket
import protocol
import json

IP = "127.0.0.1"
PORT = 6123
clients_list = []


class ClientThread(Thread):
    def __init__(self, client_socket, client_address):
        Thread.__init__(self)
        self.client_socket = client_socket
        self.client_address = client_address
        self.valid = False
        self.stop = False

    def handle_join(self, msg):
        name = msg['name']
        print(f"(JOIN) {name}")
        if len(clients_list) > 0:
            for x in range(len(clients_list)):
                if name == clients_list[x][0]:
                    self.valid = False
                else:
                    self.name = name
                    clients_list.append((name, self.client_socket))
                    self.valid = True
        else:
            self.name = name
            clients_list.append((name, self.client_socket))
            self.valid = True
        msg = {'header': protocol.WELCOME, 'valid': self.valid}
        protocol.send_one_message(self.client_socket, msg)

    def handle_msg(self, msg):
        contenido = msg['msg']
        print(f"{self.name}: {contenido}")
        msg = {'header': protocol.MSG, 'msg': f"{self.name}: {contenido}"}
        for name, to in clients_list:
            if name != self.name:
                protocol.send_one_message(to, msg)
                print(f"Message sent to {name}")

    def handle_message(self, msg):
        try:
            msg_header = msg['header']
            if msg_header == protocol.JOIN:
                self.handle_join(msg)
            elif msg_header == protocol.MSG:
                self.handle_msg(msg)
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
            except ConnectionResetError:
                print("Server stopped by admin cosa random")
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
