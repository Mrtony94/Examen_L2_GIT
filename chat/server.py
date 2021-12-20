import os
import signal
from threading import Thread
import socket
import protocol

IP = "127.0.0.1"
PORT = 6123
name_list = []


class ClientThread(Thread):
    def __init__(self, client_socket, client_address):
        Thread.__init__(self)
        self.client_socket = client_socket
        self.client_address = client_address
        self.name = ""
        self.stop = False
        self.valid = False

    def valid_name(self, name):
        if len(name_list) == 0:
            self.valid = True
            self.name = name
            name_list.append((self.name, self.client_socket))
        else:
            for x, y in name_list:
                if x == name:
                    self.valid = False
                    break
                else:
                    self.valid = True
                    self.name = name
                    name_list.append((self.name, self.client_socket))
                    break

    def manage_join(self, message):
        name = message['name']
        self.valid_name(name)
        print(f"[JOIN] received {name}")
        msg = {'header': protocol.WELCOME, 'valid': self.valid}
        protocol.send_one_message(self.client_socket, msg)
        print("WELCOME sended")

    def handle_text(self):
        text = input("[TEXT]>> ")

        print("TEXT sended")

    def handle_message(self, message):
        try:
            header = message['header']
            if header == protocol.JOIN:
                self.manage_join(message)
            elif header == protocol.MSG:
                text = message['msg']
                print(f"{self.name}: {text}")
                text = f"{self.name}: {text}"
                msg = {'header': protocol.MSG, 'msg': text}
                for name, recipient in name_list:
                    if name != self.name:
                        protocol.send_one_message(recipient, msg)
                        print(f"Message sent to {name}")
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
        if command == 'close':
            stop = True
except KeyboardInterrupt:
    print("Server stopped by admin")
except ConnectionResetError:
    print("Server stopped by admin")
os.kill(pid, signal.SIGTERM)
