import socket
import pickle
import _thread
import time

from typing import Callable

HOST = '127.0.0.1'

DEBUG = 0

class Socket_Message:

    def __init__(self, m, data, type) -> None:
        self.m = m
        self.data = data 
        self.type = type

def serialize(m: list, data, type):
    msg = Socket_Message(m, data, type)
    return pickle.dumps(msg)

def unserialize(data) -> Socket_Message:
    return pickle.loads(data)

def sock_listen(id: int, handler: Callable, base_port: int) -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        if DEBUG:
            print(f"Client {id} listening on {base_port + id}")

        s.bind((HOST, base_port + id))
        s.listen()

        while True:
            conn, addr = s.accept()
            with conn:
                if DEBUG:
                    print(f"Connected by {addr}")
                _thread.start_new_thread(handler, (sock_data_recv(conn),))

def sock_data_recv(conn: socket.SocketType) -> Socket_Message:
    data = conn.recv(1024)
    d = conn.recv(1024)

    while len(d) != 0:
        data += d
        d = conn.recv(1024)

    return unserialize(data)

def sock_data_send(m: list, data, port, type) -> None:
    data = serialize(m, data, type)

    while True:
        try:
            conn = sock_connect(port)
            conn.send(data)
            conn.close()
            break
        except:
            continue

def sock_connect(port: int) -> socket.SocketType:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, port))
    
    return sock
