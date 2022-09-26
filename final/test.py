import multiprocessing

from lib import *
from mutual_exclusion import *

import random

MAX_COUNT = 10

def parsing(file_path: str) -> tuple:
    file = open(file_path)
    qtt_processes = int(file.readline().split()[0])
    base_port = int(file.readline().split()[0])
    file.close()

    return (qtt_processes, base_port)

def test(id: int, qtt_processes: int, base_port: int, causal_process: int) -> None:
    # Test total
    mutex = Ricart_Agrawala(id, qtt_processes, base_port)
    
    # Test causal
    distributed = Distributed(id, qtt_processes, base_port + qtt_processes * 2)

    count = 0

    msg = ['MESSAGE'.encode()]

    while count < MAX_COUNT:
        mutex.acquire()

        print(f"Process [{id}] acquired | count: {count}")
       
        distributed.send(causal_process, msg)
        count += 1
        sec = random.uniform(0.1, 2)
        time.sleep(sec)

        print(f"Sleep: {sec}")
        print(f"Process [{id}] released | count: {count}")

        mutex.release()

    print(f"Process [{id}]: finished!")

    mutex.join() # It's necessary to keep socket alive

    if id == causal_process:
        print('-'*50)

        while len(distributed.messages_queue) > 0:
            print(distributed.receive(msg))

if __name__ == "__main__":
    qtt_processes, base_port = parsing("test.txt")

    print("Test:")
    print("Quantity of processes: ", qtt_processes)
    print("Port: ", base_port)
    print('-'*50)

    causal_process = random.randint(0, qtt_processes -1)

    processes = []

    for id in range(qtt_processes):
        processes.append(multiprocessing.Process(target=test, args=(int(id), int(qtt_processes), int(base_port), causal_process)))

    for p in processes:
        p.start()

    for p in processes:
        p.join()
