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
PORT = 6123

end = False


def numbers():
    try:
        number1 = 30
        number2 = 5
    except IndexError:
        raise UsageError()
    return number1, number2


def send_number():
    number1, number2 = numbers()
    number = [number1, number2]
    msg = {'header': protocol.NUMBER, 'number': number}
    protocol.send_one_message(client_socket, msg)


def strings():
    try:
        string1 = "hola"
        string2 = "mundo"
    except IndexError:
        raise UsageError()
    return string1, string2


def send_string():
    string1, string2 = strings()
    string = [string1, string2]
    msg = {'header': protocol.STRING, 'string': string}
    protocol.send_one_message(client_socket, msg)


def manage_msg():
    try:
        msg = protocol.recv_one_message(client_socket)
        header = msg['header']
        if header == protocol.NUMBER_REPLY:
            suma = msg['sum']
            print(f"La suma es: {suma}")
        elif header == protocol.STRING_REPLY:
            cadena = msg['cadena']
            print(f"La cadena es: {cadena}")
    except protocol.InvalidProtocol as e:
        print(e)


try:
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((SERVER_IP, PORT))
    send_number()
    manage_msg()
    send_string()
    manage_msg()
    lista = [1, 2, 3, 4, 5]
    hola = lista.sort()
    print(hola)
    for i in reversed(lista):
        print(i)

    print()
    print("Bye!")
except UsageError:
    raise
