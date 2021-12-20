import os
import random
import signal
from threading import Thread
import socket
import protocol

IP = "127.0.0.1"
PORT = 6123
NUMBER_LIST = []


class ClientThread(Thread):
    def __init__(self, client_socket, client_address):
        Thread.__init__(self)
        self.client_socket = client_socket
        self.client_address = client_address
        self.current_number = int
        self.suma = 0
        self.win = False
        self.end = False
        self.stop = False

    def manage_numbers(self):
        self.current_number = random.randint(1, 10)
        NUMBER_LIST.append(self.current_number)
        if 1 <= self.current_number <= 7:
            self.suma += self.current_number
        elif 8 <= self.current_number <= 10:
            self.suma += 0.5

    def manage_win(self):
        if self.suma == 7.5:
            self.win = True
            self.end = True
        elif self.suma > 7.5:
            self.win = False
            self.end = True
        else:
            self.win = False
            self.end = False

    def send_answer(self):
        self.manage_numbers()
        self.manage_win()
        result = f"El numero solicitado ha sido --> {self.current_number} \nLa suma hasta el momento es --> {self.suma}"
        msg = {'header': protocol.ANSWER, 'suma': result, 'end': self.end, 'win': self.win}
        protocol.send_one_message(self.client_socket, msg)
        print("[ANSWER] SEND")

    def send_end(self):
        msg = {'header': protocol.END, 'suma': self.suma}
        protocol.send_one_message(self.client_socket, msg)
        print("[END] SEND")

    def handle_message(self, message):
        try:
            message_header = message['header']
            if message_header == protocol.JOIN:
                print("[JOIN] RECEIVED")
                self.send_answer()
            elif message_header == protocol.REQUEST:
                print("[REQUEST] RECEIVED")
                self.send_answer()
            elif message_header == protocol.END:
                print("[END] RECEIVED")
                self.send_end()
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
