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
    logging.debug('Started')
    for i in range(5):
        shared.num += 1
    logging.debug('Ended')

def thread2(shared):
    logging.debug('Started')
    for i in range(5):
        shared.num *= 2
    logging.debug('Ended')

def thread_test():
    shared = SharedStuff()
    t1 = Thread(target=thread1, args=(shared, ))
    t2 = Thread(target=thread2, args=(shared, ))

    t1.start()
    t2.start()

    t1.join()
    t2.join()

    print shared.num

def main():
    thread_test()
    

main()