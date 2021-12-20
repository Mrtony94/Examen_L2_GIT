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
        self.total = 0
        self.stop = False

    def manage_join(self):
        print(f"[JOIN] {self.client_address} JOINED")
        self.manage_answer()

    def random_number(self):
        import random
        random_num = random.randint(1, 10)
        card.append(random_num)
        return random_num

    def sum(self, num):
        global result
        if 1 <= num <= 7:
            result.append(num)
        elif 8 <= num <= 10:
            num = 0.5
            result.append(num)
        self.total += num

    def manage_answer(self):
        end = False
        win = False
        try:
            num = self.random_number()
            self.sum(num)
            if self.total >= limit:
                end = True
            elif self.total == limit:
                win = True

            msg_envio = f"[ANSWER] {self.client_address} answered add num: {num} and the sum is: {self.total}"
            message = {'header': protocol.ANSWER, 'sum': msg_envio, 'end': end, 'win': win}
            protocol.send_one_message(self.client_socket, message)
            print(f"[ANSWER] send to {self.client_address} ")

        except KeyError:
            raise protocol.InvalidProtocol

    def handle_message(self, message):
        try:
            message_header = message['header']
            if message_header == protocol.JOIN:
                self.manage_join()
            elif message_header == protocol.REQUEST:
                self.manage_answer()
            elif message_header == protocol.END:
                msg = {'header': protocol.END, 'sum': self.sum()}
                protocol.send_one_message(self.client_socket, msg)
                self.stop = True
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



