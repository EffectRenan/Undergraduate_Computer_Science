from network import *
from threading import Lock
import _thread
from random import uniform

import time

MESSAGE = 1
SEQUENCER = 0

TYPE_SEND = 0
TYPE_BROADCAST = 1
TYPE_BROADCAST_CALLBACK = 2

DEBUG = 0

class Distributed:

    def __init__(self, id: int, qtt_processes: int, base_port: int, custom_rcv_handler: Callable = None) -> None:
        self.process_id = id 
        self.qtt_processes = qtt_processes
        self.base_port = base_port

        self.timestamps = [0 for _ in range(qtt_processes)] 
        self.sock = _thread.start_new_thread(sock_listen, (id, self.__rcv_handler, base_port))
        
        self.mutex = Lock()     # send, receive
        self.mutex2 = Lock()    # broadcast, deliver

        self.sequencer_count = 0
        self.local_count = 0

        self.broadcast_queue = {}   # {index: message} 
        self.messages_queue = []    # list of tuples: (timestamp, message)

        self.custom_rcv_handler = custom_rcv_handler
        self.custom_rcv_handler_enable = False


    def send(self, process_id: int, m: list) -> None:
        self.mutex.acquire()
        sock_data_send(m, self.timestamps, self.base_port + process_id, TYPE_SEND)

        if self.process_id != process_id:
            self.timestamps[process_id] += 1

        self.mutex.release()

    def receive(self, m: list) -> list:
        msg = []
        while len(msg) == 0:
            self.mutex.acquire()
            if len(self.messages_queue) > 0:
                self.messages_queue.sort()
                if self.messages_queue[0][1] == m:
                    msg = self.messages_queue.pop(0)
                
            self.mutex.release()
            
            if len(msg) == 0:
                time.sleep(uniform(0.1, 0.3)) # Give some time to another process that wants lock

        return msg

    def broadcast(self, m: list) -> None:
        if self.process_id == SEQUENCER:
            self.mutex2.acquire()
            data = {str(self.sequencer_count): m}
            self.broadcast_queue.update(data)
            self.sequencer_count += 1
            self.mutex2.release()

            for i in range(self.qtt_processes):
                if i != SEQUENCER:
                    sock_data_send(m, data, self.base_port + i, TYPE_BROADCAST_CALLBACK)
        
        else:
            sock_data_send(m, self.process_id, self.base_port + SEQUENCER, TYPE_BROADCAST)
    
    def deliver(self, m) -> list:

        data = []
        if m == None: # Pop the first
            while len(data) == 0 and len(self.broadcast_queue.keys()) != 0:
                self.mutex2.acquire()
                if str(self.local_count) in self.broadcast_queue.keys():
                    data = self.broadcast_queue.pop(str(self.local_count))
                    self.local_count += 1
                    self.mutex2.release()
                    return data
                else:
                    self.mutex2.release()
                    time.sleep(uniform(0.1, 0.3)) # Give some time to another process that wants lock

            return data
            
        while len(data) == 0:
            self.mutex2.acquire()
            if str(self.local_count) in self.broadcast_queue.keys():
                if self.broadcast_queue[str(self.local_count)] == m:
                    data = self.broadcast_queue.pop(str(self.local_count))
                    self.local_count += 1
            self.mutex2.release()

            time.sleep(uniform(0.1, 0.3)) # Give some time to another process that wants lock

        return data

    def broadcast_msg_index(self, m) -> int:
        index = None
        while index == None:
            self.mutex2.acquire()
            if m in self.broadcast_queue.values():
                key = [*self.broadcast_queue.values()].index(m)
                index = int([*self.broadcast_queue.keys()][key])
                self.mutex2.release()
            else:
                self.mutex2.release()
                time.sleep(uniform(0.1, 0.3)) # Give some time to another process that wants lock

        return index
  
    def __rcv_handler(self, socket_message: Socket_Message):
        if DEBUG:
            print(f"Received: {self.process_id} | type: {socket_message.type}")

        if socket_message.type == TYPE_SEND:
            self.mutex.acquire()
            for i in range(len(self.timestamps)):
                if i != self.process_id:
                    self.timestamps[i] = max(self.timestamps[i], socket_message.data[i])

            self.messages_queue.append((self.timestamps[self.process_id], socket_message.m))
            self.timestamps[self.process_id] += 1
            self.mutex.release()
        elif socket_message.type == TYPE_BROADCAST: # Only the SEQUENCER should run it
            self.mutex2.acquire()
            data = {str(self.sequencer_count): socket_message.m}
            self.broadcast_queue.update(data)
            self.sequencer_count += 1
            self.mutex2.release()

            for i in range(self.qtt_processes):
                if i != SEQUENCER:
                    sock_data_send(socket_message.m, data, self.base_port + i, TYPE_BROADCAST_CALLBACK)
       
        elif socket_message.type == TYPE_BROADCAST_CALLBACK:
            self.mutex2.acquire()
            self.broadcast_queue.update(socket_message.data)
            self.mutex2.release()
        else:
            if DEBUG:
                print("Error type: ", socket_message.type)
            exit()

        if self.custom_rcv_handler != None:
            self.custom_rcv_handler(socket_message)
        

