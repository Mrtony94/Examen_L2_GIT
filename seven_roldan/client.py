import os
import signal
from threading import Thread
import socket
import protocol
import json


class UsageError(Exception):
    def __init__(self):
        super().__init__("usage: python client.py name")


SERVER_IP = "127.0.0.1"
PORT = 7129
stop = False


def send_join():
    msg = {"header": protocol.JOIN}
    protocol.send_one_message(client_socket, msg)


def send_end():
    msg = {"header": protocol.END}
    protocol.send_one_message(client_socket, msg)


def manage_answer(msg):
    global stop
    print(f"El número que tienes es: {msg['sum']}")
    if msg["end"] == True or msg["win"] == True:
        stop = True


def send_request():
    msg = {"header": protocol.REQUEST}
    protocol.send_one_message(client_socket, msg)


def manage_end(msg):
    global stop
    print(f"El numero que tienes es: {msg['sum']}")
    print("Saliendo...")
    stop = True


def manage_msg():
    msg = protocol.recv_one_message(client_socket)
    header = msg["header"]
    if header == protocol.ANSWER:
        manage_answer(msg)
    if header == protocol.END:
        manage_end(msg)


def menu():
    print("""1.- Continuar
2.- Terminar""")
    option = int(input("Elige una opción (1 ó 2): "))
    if option == 1:
        send_request()
    else:
        send_end()
        manage_msg()


while not stop:
    try:

        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((SERVER_IP, PORT))

        send_join()
        manage_msg()
        menu()

    except TypeError as e:
        print(e)
    except protocol.ConnectionClosed:
        print("Connection closed by the server")
    except ConnectionError:
        print("Could not connect to the server. Is the server alive?")
    except socket.error as e:
        print("Error: {}".format(e))
    except protocol.InvalidProtocol as e:
        print(e)
    except UsageError:
        raise
    except Exception as e:
        print(e)
    except KeyboardInterrupt:
        print("\nBye!")
    except KeyError:
        print("ERROR: invalid message's fragment received")

