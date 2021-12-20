import os
import random
import signal
from threading import Thread
import socket
import protocol
import json

IP = "127.0.0.1"
PORT = 6123


class ClientThread(Thread):
    def __init__(self, client_socket, client_address):
        Thread.__init__(self)
        self.client_socket = client_socket
        self.client_address = client_address
        self.total = 0
        self.stop = False

    def send_answer(self):
        num = random.randint(1, 10)
        if num <= 7:
            self.total += num
        else:
            self.total += 0.5
        sum = f"La suma es {self.total} y el numero es {num}"
        msg = {"header": protocol.ANSWER, "sum": sum, "end": self.total >= 7.5, "win": self.total == 7.5}
        protocol.send_one_message(self.client_socket, msg)

    def send_end(self):
        print(f"El usuario ha abandonado la sesión")
        msg = {"header": protocol.END, "sum": self.total}
        protocol.send_one_message(self.client_socket, msg)

    def manage_msg(self, msg):
        header = msg["header"]
        if header == protocol.JOIN:
            print(f"El usuario {self.client_address} se ha unido a la sesión")
            self.send_answer()
        elif header == protocol.END:
            print(f"El usuario {self.client_address} ha abandonado la sesión")
            self.send_end()
        elif header == protocol.REQUEST:
            print(f"El usuario {self.client_address} ha pedido una nueva suma")
            self.send_answer()

    def run(self):
        print(f"Connection received from {self.client_address}")
        while not self.stop:
            try:
                msg = protocol.recv_one_message(self.client_socket)
                self.manage_msg(msg)
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


pid = os.getpid()
server_socket_thread = ServerSocketThread()
server_socket_thread.start()
try:
    stop = False
    while not stop:
        command = input()
except KeyboardInterrupt:
    print("Server stopped by admin")
os.kill(pid, signal.SIGTERM)
