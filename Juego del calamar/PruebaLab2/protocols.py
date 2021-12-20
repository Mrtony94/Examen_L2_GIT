MSG_JOIN = "JOIN"
MSG_SERVER = "SERVER"
GET_MARBLES = "MARBLES"
GET_EVEN = "EVEN"
SEND_COMMAND = "COMMAND"
END_GAME = "END"
GAME_FULL = "FULL"

import struct

def recvall(sock, count):
    buf = b''
    while count:
        newbuf = sock.recv(count)
        if not newbuf:
            return None
        buf += newbuf
        count -= len(newbuf)
    return buf

def send_one_message(sock, data):
    length = len(data)
    sock.sendall(struct.pack('!I', length))
    sock.sendall(data)

def recv_one_message(sock):
    import struct
    lengthbuf = recvall(sock, 4)
    length = struct.unpack('!I', lengthbuf)
    return recvall(sock, length)