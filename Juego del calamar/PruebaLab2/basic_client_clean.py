import socket
import json
import protocols as p

def get_marbles(options):
    exit = False
    while not exit:
        try:
            o = int(input('Enter a number of marbles: '))
            if options[0] <= o <= options[1]:
                exit = True
        except ValueError:
            print('We need a number')
    return o

def get_even(options):
    exit = False
    while not exit:
        try:
            o = input('Enter Even or odd').lower()
            if o in options:
                exit = True
        except ValueError:
            print('We need a number')
    return o

def manage_marbles(c_s, options):
    marbles = get_marbles(options)
    msg = {"protocol": p.SEND_COMMAND, "option": marbles}
    p.send_one_message(c_s, json.dumps(msg).encode())

def manage_even(c_s, options):
    even = get_even(options)
    msg = {"protocol": p.SEND_COMMAND, "option": even}
    p.send_one_message(c_s, json.dumps(msg).encode())

c_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
c_s.connect(("127.0.0.1", 7129))

exit = False
#usualmente en este punto le enviamos un mensaje al servidor para decirle
#que estamos aquí e iniciar la conversación
msg = {"protocol": p.MSG_JOIN}
p.send_one_message(c_s, json.dumps(msg).encode())

while not exit:
    try:
        #en este cliente se espera a que el servidor diga algo
        server_msg = json.loads(p.recv_one_message(c_s).decode())
        if server_msg["protocol"] == p.MSG_SERVER:
            print(server_msg["msg"])
        elif server_msg["protocol"] == p.GET_MARBLES:
            manage_marbles(c_s, server_msg["options"])
        elif server_msg["protocol"] == p.GET_EVEN:
            manage_even(c_s, server_msg["options"])
        elif server_msg["protocol"] == p.END_GAME:
            print(server_msg["msg"])
            exit = True
        elif server_msg["protocol"] == p.END_FULL:
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