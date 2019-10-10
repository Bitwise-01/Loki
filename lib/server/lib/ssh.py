# Date: 07/27/2018
# Author: Pure-L0G1C
# Description: Secure shell

import os
import ssl
import socket
from threading import Thread
from lib.const import CERT_FILE, KEY_FILE
from socket import timeout as TimeOutError


class Communicate(object):

    def __init__(self, session):
        self.session_recv = 4096 << 12
        self.session = session
        self.is_alive = True
        self.pending = False
        self.tmp_resp = ''
        self.resp = None

    def recv(self):
        self.session.settimeout(0.5)
        while self.is_alive:
            try:
                recv = self.session.recv(self.session_recv)
                if recv:
                    data = recv.decode('utf8')
                    if data != '-1':
                        self.tmp_resp += data
                    else:
                        self.resp = self.tmp_resp
                        self.pending = False
                else:
                    self.stop()
            except:
                pass

    def send(self, data):
        if len(data.strip()):
            if not self.is_alive:
                return
            try:
                self.pending = True
                self.session.sendall(data.encode('utf8'))
            except:
                pass

    def start(self):
        recv = Thread(target=self.recv)
        recv.daemon = True
        recv.start()

    def stop(self):
        self.is_alive = False


class Server(object):

    def __init__(self, communication):
        self.communication = communication
        self.communication.start()
        self.is_alive = True

    def stop(self):
        self.is_alive = False
        self.communication.is_alive = False

    def send(self, cmd):
        if len(cmd.strip()):
            if not self.communication.pending:
                self.communication.send(cmd)
                while all([self.is_alive, self.communication.is_alive, self.communication.pending]):
                    pass
                self.communication.tmp_resp = ''
                resp = self.communication.resp
                self.communication.resp = None
                return resp


class SSH(object):

    def __init__(self, ip, port, max_time=10, verbose=False):
        self.ip = ip
        self.port = port
        self.verbose = verbose
        self.max_time = max_time
        self.communication = None
        self.recipient_session = None

    def display(self, msg):
        if self.verbose:
            print('{}\n'.format(msg))

    def start(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.settimeout(self.max_time)

        try:
            server_socket.bind((self.ip, self.port))
            server_socket.listen(1)
            return server_socket
        except OSError:
            self.display('Failed to start ssh server on {}:{}'.format(
                self.ip, self.port))

    def serve(self, server_socket):
        try:
            session, addr = server_socket.accept()
            self.recipient_session = ssl.wrap_socket(
                session, server_side=True, certfile=CERT_FILE, keyfile=KEY_FILE)
        except TimeOutError:
            self.display('Server timed out')
            self.close()
            return -1

        communication = Communicate(self.recipient_session)
        if self.communication:
            self.close()

        self.communication = Server(communication)
        return 0

    def close(self):
        try:
            print('\nClosing SSH ...')
            if self.communication:
                self.communication.stop()

            self.recipient_session.close()
            self.recipient_session.shutdown(socket.SHUT_RDWR)
        except:
            pass

    def send(self, cmd):
        if self.communication:
            return self.communication.send(cmd)
