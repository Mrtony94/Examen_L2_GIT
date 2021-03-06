import socket
from threading import Thread
import protocol as p
import game

client_threads_running = []
g = game.Game()


def play_round():
    global g
    msg1 = {"protocol": p.GET_ANSWER, "options": ["piedra", "papel", "tijeras"]}
    p.send_one_message(g.sockets[g.turn], msg1)
    other = (g.turn + 1) % game.Game.NUM_PLAYERS
    p.send_one_message(g.sockets[other], msg1)


def manage_join(c_s):
    global g
    if len(g.sockets) == 2:
        msg = {"protocol": p.GAME_FULL}
        p.send_one_message(c_s, msg)
    else:
        g.sockets.append(c_s)
        msg = {"protocol": p.MSG_SERVER, "msg": "You are player" + str(len(g.sockets) - 1)}
        p.send_one_message(c_s, msg)
        if len(g.sockets) == 2:
            play_round()
        else:
            msg = {"protocol": p.MSG_SERVER, "msg": "waiting for a second player"}
            p.send_one_message(c_s, msg)


def send_end_message(win, lose):
    global g
    msg1 = {"protocol": p.END_GAME, "msg": "You win"}
    msg2 = {"protocol": p.END_GAME, "msg": "You lose"}
    p.send_one_message(g.sockets[lose], msg2)
    p.send_one_message(g.sockets[win], msg1)


def manage_command(c_s, option):
    global g
    who = g.sockets.index(c_s)
    g.answers.insert(who, option)
    if len(g.answers) == 2 and not (g.num_ronda == 2):
        answer1 = g.answers[g.turn]
        answer2 = g.answers[(g.turn + 1) % game.Game.NUM_PLAYERS]
        if answer1 == answer2:
            player_win = g.turn
            g.num_ronda += 1
            g.answers = []  # [piedra, piedra]
            g.wins[player_win] += 1  # [2,1]
            play_round()
        elif answer1 == "piedra" and answer2 == "tijeras":
            player_win = g.turn
            send_end_message(0, 1)
            g.num_ronda += 1
        elif answer1 == "tijeras" and answer2 == "piedra":
            player_win = (g.turn + 1) % game.Game.NUM_PLAYERS
            send_end_message(1, 0)
            g.num_ronda += 1
            g.wins[player_win] += 1
        elif answer1 == "papel" and answer2 == "piedra":
            player_win = g.turn
            send_end_message(0, 1)
        elif answer1 == "piedra" and answer2 == "papel":
            player_win = (g.turn + 1) % game.Game.NUM_PLAYERS
            send_end_message(1, 0)
        elif answer1 == "papel" and answer2 == "tijeras":
            player_win = (g.turn + 1) % game.Game.NUM_PLAYERS
            send_end_message(1, 0)
        elif answer1 == "tijeras" and answer2 == "papel":
            player_win = g.turn
            send_end_message(0, 1)
    elif len(g.answers) == 2 and g.num_ronda == 2:
        print(g.wins[g.turn])
        print(g.wins[(g.turn + 1) % g.NUM_PLAYERS])
        if g.wins[g.turn] >= g.wins[(g.turn + 1) % g.NUM_PLAYERS]:
            win = g.turn
            print(g.wins[0])
        else:
            win = (g.turn + 1) % g.NUM_PLAYERS
        lose = (win + 1) % g.NUM_PLAYERS
        message = {"protocol": p.MSG_SERVER, "msg": win}
        for socket in g.sockets:
            p.send_one_message(socket, message)
        send_end_message(win, lose)


class ClientThread(Thread):

    def __init__(self, client_socket):
        Thread.__init__(self)
        self.c_s = client_socket
        self.client_exit = False

    def run(self):
        while not self.client_exit:
            try:
                message = p.recv_one_message(self.c_s)
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


class ServerThread(Thread):
    def __init__(self, ip, port):
        Thread.__init__(self)
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
                print("Conexi??n desde", c_a)
                client_thread = ClientThread(c_s)
                client_thread.start()
                # A??adimos el hilo a una lista para poder controlarlo desde el
                # programa principal
                client_threads_running.append(client_thread)

            except OSError:
                self.stop = True
                ServerThread.close_client_connections()
        print("Sale del servidor")


server_thread = ServerThread("127.0.0.1", 7129)
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
            print("Conexi??n cerrada")
