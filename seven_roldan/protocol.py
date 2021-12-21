import json
import struct

JOIN = 'JOIN' # client wants to join a room (client -> server) HEADER --> {'header': 'protocol.JOIN'}
REQUEST = 'REQUEST' # client wants to request for a number (client -> server) HEADER --> {'header': 'protocol.REQUEST'}
END = 'END' # client wants to end the game (client -> server) HEADER --> {'header': 'protocol.END'}

ANSWER = 'ANSWER' # server sends the answer to the client with information about game (server -> client) HEADER --> {'header': 'protocol.ANSWER', 'sum': 'suma', 'end': end, 'win': win}



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