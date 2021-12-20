import socket
import threading
import json
import protocols as p
import game

client_threads_running = []
g = game.Game()

def play_round():
    global g
    msg1 = {"protocol": p.GET_MARBLES, "options": [1, g.marbles[g.turn]]}
    msg2 = {"protocol": p.GET_EVEN, "options": ["even", "odd"]}
    p.send_one_message(g.sockets[g.turn], json.dumps(msg1).encode())
    other = (g.turn + 1) % game.Game.NUM_PLAYERS
    p.send_one_message(g.sockets[other], json.dumps(msg2).encode())


def manage_join(c_s):
    global g
    if len(g.sockets) == 2:
        msg = {"protocol": p.GAME_FULL}
        p.send_one_message(c_s, json.dumps(msg).encode())
    else:
        g.sockets.append(c_s)
        msg = {"protocol": p.MSG_SERVER, "msg": "You are player" + str(len(g.sockets) - 1)}
        p.send_one_message(c_s, json.dumps(msg).encode())
        if len(g.sockets) == 2:
            play_round()
        else:
            msg = {"protocol": p.MSG_SERVER, "msg": "waiting for a second player"}
            p.send_one_message(c_s, json.dumps(msg).encode())


def send_end_message(win, lose):
    global g
    msg1 = {"protocol": p.END_GAME, "msg": "You win"}
    msg2 = {"protocol": p.END_GAME, "msg": "You lose"}
    p.send_one_message(g.sockets[lose], json.dumps(msg2).encode())
    p.send_one_message(g.sockets[win], json.dumps(msg1).encode())


def manage_command(c_s, option):
    global g
    who = g.sockets.index(c_s)
    g.answers.insert(who, option)
    if len(g.answers) == 2:
        marbles = g.answers[g.turn]
        even = g.answers[(g.turn + 1) % game.Game.NUM_PLAYERS]
        if (even == "even" and marbles % 2 == 0) or (even == "odd" and marbles % 2 == 1):
            player_win = (g.turn + 1) % game.Game.NUM_PLAYERS
        else:
            player_win = g.turn
        player_lose = (player_win + 1) % game.Game.NUM_PLAYERS
        g.marbles[player_win] += marbles
        g.marbles[player_lose] -= marbles
        if g.marbles[0] <= 0:
            send_end_message(0, 1)
        elif g.marbles[1] <= 0:
            send_end_message(1, 0)
        else:
            g.turn = (g.turn + 1) % game.Game.NUM_PLAYERS
            g.answers = []
            text = "Marbles 0:" + str(g.marbles[0]) + "Marbles 1:" + str(g.marbles[1])
            msg = {"protocol": p.MSG_SERVER, "msg": text}
            for o in g.sockets:
                p.send_one_message(o, json.dumps(msg).encode())
            play_round()


class ClientThread(threading.Thread):

    def __init__(self, client_socket):
        threading.Thread.__init__(self)
        self.c_s = client_socket
        self.client_exit = False

    def run(self):
        while not self.client_exit:
            try:
                message = json.loads(self.c_s.recv(1024).decode())
                print("Mensaje recibido", message)
                if message["protocol"] == p.MSG_JOIN:
                    manage_join(self.c_s)
                elif message["protocol"] == p.SEND_COMMAND:
                    manage_command(self.c_s, message["option"])
            except ConnectionResetError:
                self.client_exit = True
            except ConnectionAbortedError:
                self.client_exit = True
            except TypeError:
                self.client_exit = True
                self.c_s.close()
                print("Error receiving message due to client dc")


class ServerThread(threading.Thread):
    def __init__(self, ip, port):
        threading.Thread.__init__(self)
        self.stop = False
        self.s_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s_s.bind((ip, port))
        self.s_s.listen(100)

    @staticmethod
    def close_client_connections():
        global client_threads_running
        for th in client_threads_running:
            th.c_s.close()

    def run(self):
        # si queremos que la variable pueda ser modificada desde el hilo tenemos
        # que utilizar la sentencia global
        global client_threads_running
        while not self.stop:
            try:
                c_s, c_a = self.s_s.accept()
                print("Conexión desde", c_a)
                client_thread = ClientThread(c_s)
                client_thread.start()
                # Añadimos el hilo a una lista para poder controlarlo desde el
                # programa principal
                client_threads_running.append(client_thread)

            except OSError:
                self.stop = True
                ServerThread.close_client_connections()
        print("Sale del servidor")


server_thread = ServerThread("0.0.0.0", 7129)
server_thread.start()

exit = False
while not exit:
    server_input = input("Enter exit to close server")
    if server_input == "exit":
        try:
            exit = True
            server_thread.s_s.close()
        except OSError:
            print("Se ha cerrado el servidor")
        except ConnectionAbortedError:
            print("Conexion cerrada")
        except ConnectionResetError:
            print("Conexión cerrada")


