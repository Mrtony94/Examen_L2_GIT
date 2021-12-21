import json
import struct

JOIN = "JOIN"
WELCOME = "WELCOME"
LOAD_GAME = "LOAD_GAME"
LOAD_GAME_ANSWER = "LOAD_GAME_ANSWER"
SERVER_OPTION = "SEND_SERVER_OPTION"
CHOOSE_CHARACTER = "CHOOSE_CHARACTER"
CHARACTER = "SEND_CHARACTER"
SERVER_MESSAGE = "SERVER_MESSAGE"
YOUR_TURN = "YOUR_TURN"
CHARACTER_COMMAND = "SEND_CHARACTER_COMMAND"
GAMES = "SEND_GAMES"
GAME_CHOICE = "SEND_GAME_CHOICE"
VALID_GAME = "SEND_VALID_GAME"
END_GAME = "END_GAME"
DC_ME = "DC_ME"
DC_SERVER = "DC_SERVER"


class ConnectionClosed(Exception):
    def __init__(self):
        super().__init__("Connection closed by other")


def recv_all(recipient, length):
    buffer = b''
    while length != 0:
        buffer_aux = recipient.recv(length)
        if not buffer_aux:
            return None
        buffer = buffer + buffer_aux
        length = length - len(buffer_aux)
    return buffer


def send_one_message(recipient, message):
    encoded_data = json.dumps(message).encode()
    length = len(encoded_data)
    header = struct.pack("!I", length)
    recipient.sendall(header)
    recipient.sendall(encoded_data)


def recv_one_message(recipient):
    header_buffer = recv_all(recipient, 4)  # int size -> 4
    if header_buffer:
        header = struct.unpack("!I", header_buffer)
        length = header[0]
        encoded_data = recv_all(recipient, length)
        message = json.loads(encoded_data.decode())
        return message
    else:
        raise ConnectionClosed()