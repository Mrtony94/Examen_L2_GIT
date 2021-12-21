import socket
import json
import protocol as p


def get_answer(options):
    global o
    exit = False
    while not exit:
        o = input('Enter answer: ')
        if o in options:
            exit = True
    return o


def manage_marbles(c_s, options):
    answer = get_answer(options)
    msg = {"protocol": p.SEND_COMMAND, "option": answer}
    p.send_one_message(c_s, msg)


c_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
c_s.connect(("127.0.0.1", 7129))

exit = False
# usualmente en este punto le enviamos un mensaje al servidor para decirle
# que estamos aquí e iniciar la conversación
msg = {"protocol": p.MSG_JOIN}
p.send_one_message(c_s, msg)

while not exit:
    try:
        # en este cliente se espera a que el servidor diga algo
        server_msg = p.recv_one_message(c_s)
        if server_msg["protocol"] == p.MSG_SERVER:
            print(server_msg["msg"])
        elif server_msg["protocol"] == p.GET_ANSWER:
            manage_marbles(c_s, server_msg["options"])
        elif server_msg["protocol"] == p.END_GAME:
            print(server_msg["msg"])
            exit = True
        elif server_msg["protocol"] == p.GAME_FULL:
            print("Could not join. Game is full")
            exit = True

    except ConnectionResetError:
        exit = True
        print("El servidor ha sido cerrado")

c_s.close()
"""if server_msg["protocol"] == p.whatever_protocol:
                manage_this_msg()

    except ConnectionResetError:
        exit = True
        print("El servidor ha sido cerrado")
c_s.close()"""
