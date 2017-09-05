import threading
from threading import Thread
import logging
import time

logging.basicConfig(level=logging.DEBUG, format=
                    '[DEBUG] (%(threadName)-10s) %(message)s')

class SharedStuff(object):
    def __init__(self):
        self.name = 'Shared!'
        self.num = 0

def thread1(shared):
    logging.debug('Started thread1')
    for i in range(10005):
        shared.num += 1
    logging.debug('Ended')

def thread2(shared):
    logging.debug('Started thread2')
    for i in range(10005):
        shared.num += 3
    logging.debug('Ended')

class Thread3(object):
    def run(self, shared):
        logging.debug('Started Thread3.run')
        for i in range(10005):
            shared.num += 7
        logging.debug('Ended')

def thread_test():
    shared = SharedStuff()
    tFuncObj3 = Thread3()
    t1 = Thread(target=thread1, args=(shared, ))
    t2 = Thread(target=thread2, args=(shared, ))
    t3 = Thread(target=tFuncObj3.run, args=(shared, ))

    # start threads
    t1.start()
    t2.start()
    t3.start()

    t1.join()
    t2.join()
    t3.join()

    print shared.num

def main():
    thread_test()
    

if __name__ == "__main__":
    main()
