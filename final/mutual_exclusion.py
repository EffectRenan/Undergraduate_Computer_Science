from lib import *
from network import *
import _thread

import time
from threading import Lock

RELEASED = 0
HELD = 1
WANTED = 2
INIT = 3
END = 4

class Ricart_Agrawala:
    
    def __init__(self, id: int, qtt_processes: int, base_port: int) -> None:
        self.distributed = Distributed(id, qtt_processes, base_port, self.__rcv_broadcast_handler)
        self.sock = _thread.start_new_thread(sock_listen, (qtt_processes + id, self.__received_count, base_port))
        self.state = RELEASED
        self.base_port = base_port
        self.process_id = id
        self.qtt_processes = qtt_processes
        self.received_count = 0

        self.qtt_join = 0

        self.init = 0
        self.end = 0
        self.mutex = Lock()

        if qtt_processes > 1:
            self.__init()

    def __init(self):
        for i in range(self.qtt_processes):
            if i != self.process_id:
                sock_data_send([], '', self.base_port + self.qtt_processes + i, INIT)

        while self.init < (self.qtt_processes - 1): # waiting all thread are ok to start
            continue

    def __rcv_broadcast_handler(self, socket_message: Socket_Message) -> None:
        msg = socket_message.m[0].decode().split('#')
        id = int(msg[0])
        type = int(msg[1])
        m = socket_message.m

        if id != self.process_id:
            timestamp = None
            timestamp2 = None
            if self.state == WANTED:
                timestamp = self.distributed.broadcast_msg_index(m)
                timestamp2 = self.distributed.broadcast_msg_index([f'{self.process_id}#{WANTED}'.encode()])

            if type == WANTED:
                if timestamp2 == None and self.state == HELD or (self.state == WANTED and timestamp2 < timestamp):
                    pass
                else:
                    self.distributed.deliver(m)
                    sock_data_send(m, m[0], self.base_port + self.qtt_processes + id, WANTED) # trigger received_count
            else:
                print("Error type: ", socket_message.type)
                exit()

    def __received_count(self, socket_message: Socket_Message):
        type = socket_message.type
        if type == RELEASED:
            if socket_message.m in self.distributed.broadcast_queue.values():
                self.distributed.deliver(socket_message.m)
        elif type == WANTED:
            self.received_count += 1
        elif type == INIT:
            self.init += 1
        elif type == END:
            self.end += 1
        else:
            print("Error type: ", type)
            exit()

    def acquire(self):

        self.state = WANTED
        data = str(self.process_id) + "#" + str(self.state) 
        msg = [data.encode()]
        self.distributed.broadcast(msg)

        while self.received_count < (self.qtt_processes - 1):
            pass

        self.state = HELD

    def release(self):
        data = self.distributed.deliver(None)
        while len(data) > 0:
            id = int(data[0].decode().split("#")[0])

            if id != self.process_id:
                sock_data_send(data, data[0], self.base_port + self.qtt_processes + id, WANTED) # trigger received_count
            
            data = self.distributed.deliver(None)
       
        self.received_count = 0
        self.state = RELEASED

    def join(self):
        if self.qtt_processes > 1:
            for i in range(self.qtt_processes):
                if i != self.process_id:
                    sock_data_send([], '', self.base_port + self.qtt_processes + i, END)

            while self.end < (self.qtt_processes - 1): # waiting all threads are ok to end
                time.sleep(1)
