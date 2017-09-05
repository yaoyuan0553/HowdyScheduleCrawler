import threading
from threading import Thread
import logging
import time
import sys
import os

logging.basicConfig(level=logging.DEBUG, format=
                    '[DEBUG] (%(threadName)-10s) %(message)s')

class SharedStuff(object):
    def __init__(self):
        self.name = 'Shared!'
        self.num = 0
        self.quitEvent = threading.Event()

def thread1(shared):
    logging.debug('Started thread1')
    for i in range(10005):
        if shared.quitEvent.isSet():
            break
        shared.num += 1
        time.sleep(1)
    logging.debug('Ended')

def thread2(shared):
    logging.debug('Started thread2')
    for i in range(10005):
        if shared.quitEvent.isSet():
            break
        shared.num += 3
        time.sleep(1)
    logging.debug('Ended')

class Thread3(object):
    def run(self, shared):
        logging.debug('Started Thread3.run')
        for i in range(10005):
            if shared.quitEvent.isSet():
                break
            shared.num += 7
            time.sleep(1)
        logging.debug('Ended')

def showMenu():
    pass

def thread_test():
    shared = SharedStuff()
    tFuncObj3 = Thread3()

    threadList = []
    threadList.append(Thread(target=thread1, args=(shared, )))
    threadList.append(Thread(target=thread2, args=(shared, )))
    threadList.append(Thread(target=tFuncObj3.run, args=(shared, )))

    # start threads
    for t in threadList:
        t.start()

    # show menu
    option = None
    while True:
        print "Sample Menu"
        print "1. Show current status (value of shared  number)"
        print "2. Terminate all current jobs"
        print "3. Exit program"
        option = int(raw_input("Please select: "))
        if option == 1:
            print shared.num
        elif option == 2:
            shared.quitEvent.set()
            break
        elif option == 3:
            os._exit(0)

    # join threads
    for t in threadList:
        t.join()

    print shared.num

def main():
    thread_test()
    

if __name__ == "__main__":
    main()
