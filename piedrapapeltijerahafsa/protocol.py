MSG_JOIN = "JOIN"
MSG_SERVER = "SERVER"
GET_ANSWER = "GET_ANSWER"
SEND_COMMAND = "COMMAND"
END_GAME = "END"
GAME_FULL = "FULL"

import struct
import json


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
    if header_buffer is None:
        print("nada")
    else:
        header = struct.unpack("!I", header_buffer)
        length = header[0]
        data_buffer = recv_all(recipient, length)
        return json.loads(data_buffer.decode())
