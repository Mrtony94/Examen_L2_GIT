import os
import random
import signal
from threading import Thread
import socket

import protocol
from game import Game

IP = "127.0.0.1"
PORT = 6123


class ClientThread(Thread):
    def __init__(self, client_socket, client_address):
        Thread.__init__(self)
        self.client_socket = client_socket
        self.client_address = client_address
        self.stop = False
        self.valid = False
        self.answer = ""
        self.name = ""
        self.move = ""
        self.win = False
        self.winner = ""

    def handle_join(self, message):
        name = message["name"]
        self.name = name
        print(f"[JOIN] received by {self.name}")
        if len(Game.players) == 0:
            self.valid = True
            self.answer = f"Welcome {self.name} join the game"
            print(f"{self.name} join the game")
            Game.players.append((self.name, self.client_socket))
        elif len(Game.players) <= 1:
            for x, y in Game.players:
                if x == self.name:
                    self.valid = False
                    self.answer = "Name is in use"
                    break
                else:
                    self.valid = True
                    self.answer = f"Welcome {self.name} to the game"
                    print(f"{self.name} join the game")
                    Game.players.append((self.name, self.client_socket))
                    break
        else:
            self.valid = False
            self.answer = "Game is full"
        message = {'header': protocol.WELCOME, 'valid': self.valid, 'answer': self.answer}
        protocol.send_one_message(self.client_socket, message)

    def random_move(self):
        self.move = random.choice(Game.hand_list)

    def compare(self, action):
        self.random_move()
        print(f"{self.name} played {action} and SERVER played {self.move}")
        if self.move == action:
            self.win = False
            self.answer = "EMPATE, try again"
            self.winner = None
        elif self.move == "papel" and action == "piedra":
            self.win = False
            self.winner = "server"
            self.answer = "SERVER WON"
        elif self.move == "piedra" and action == "papel":
            self.win = True
            self.winner = self.name
            self.answer = "CLIENT WON"
        elif self.move == "piedra" and action == "tijera":
            self.win = False
            self.winner = "server"
            self.answer = "SERVER WON"
        elif self.move == "tijera" and action == "piedra":
            self.win = True
            self.winner = self.name
            self.answer = "CLIENT WON"
        elif self.move == "tijera" and action == "papel":
            self.win = False
            self.winner = "server"
            self.answer = "SERVER WON"
        elif self.move == "papel" and action == "tijera":
            self.win = True
            self.winner = self.name
            self.answer = "CLIENT WON"

    def handle_action(self, action):
        if action in Game.hand_list:
            Game.players_hand.append((self.name, self.client_socket, action))
            self.valid = True
            print(f"{self.name} played {action}")
            self.compare(action)
        else:
            self.valid = False
            self.answer = "Invalid action"
            self.win = False
            self.winner = None
        answer = {'header': protocol.VALID_MOVE, 'valid': self.valid, 'win': self.win, 'winner': self.winner, 'answer': self.answer}
        protocol.send_one_message(self.client_socket, answer)

    def handle_message(self, message):
        header = message['header']
        if header == protocol.JOIN:
            self.handle_join(message)
        elif header == protocol.END_GAME:
            print(f"[END_GAME] received by {self.name}")
            self.stop = True
            message = {'header': protocol.END_GAME, 'stop': self.stop, 'answer': "Leave the game"}
            protocol.send_one_message(self.client_socket, message)
        elif header == protocol.ACTION:
            print(f"[ACTION] received by {self.name}")
            action = message['action']
            self.handle_action(action)

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
