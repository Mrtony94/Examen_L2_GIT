import socket
import protocol as p


def get_answer(options):
    global o
    exit = False
    while not exit:
        o = input('Enter answer: ').lower()
        if o in options:
            exit = True
    return o


def manage_command(c_s, options):
    answer = get_answer(options)
    msg = {"protocol": p.COMMAND, "option": answer}
    p.send_one_message(c_s, msg)


c_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
c_s.connect(("127.0.0.1", 6123))

exit = False
# usualmente en este punto le enviamos un mensaje al servidor para decirle
# que estamos aquí e iniciar la conversación
msg = {"protocol": p.JOIN}
p.send_one_message(c_s, msg)

while not exit:
    try:
        # en este cliente se espera a que el servidor diga algo
        server_msg = p.recv_one_message(c_s)
        if server_msg["protocol"] == p.DC:
            print(server_msg["msg"])
            exit = True
        elif server_msg["protocol"] == p.TURN:
            manage_command(c_s, server_msg["options"])
        elif server_msg["protocol"] == p.COMMAND:
            print(server_msg["msg"])
            exit = True
        elif server_msg["protocol"] == p.ENDGAME:
            print(f"{server_msg['msg']}")
            exit = True
        elif server_msg["protocol"] == p.SERVER:
            print(server_msg["msg"])

    except ConnectionResetError:
        exit = True
        print("El servidor ha sido cerrado")

c_s.close()

