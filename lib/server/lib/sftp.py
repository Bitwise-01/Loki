# Date: 07/27/2018
# Author: Pure-L0G1C
# Description: Secure FTP

import os
import ssl
import socket
from . file import File
from time import time, sleep
from lib.const import CERT_FILE, KEY_FILE
from socket import timeout as TimeOutError

class sFTP(object):

    def __init__(self, ip, port, max_time=60, verbose=False):
        self.ip = ip
        self.port = port
        self.error_code = 0
        self.time_elapsed = 0
        self.verbose = verbose
        self.max_time = max_time
        self.chunk_size = 0xffff
        self.server_socket = None
        self.session_size = 0x1000
        self.recipient_session = None

    def display(self, msg):
        if self.verbose:
            print('{}\n'.format(msg))

    def send_file(self, file):

        # send file's name
        sleep(0.5)
        print('Sending file\'s name ...')
        self.recipient_session.sendall(os.path.basename(file).encode('utf8'))

        # send file's data
        sleep(0.5)
        self.display('Sending {} ...'.format(file))
        for data in File.read(file):
            self.recipient_session.sendall(data)
        self.display('File sent')

    def recv_file(self):
        _bytes = b''

        # receive file's name
        file_name = self.recipient_session.recv(self.session_size)

        # receive file's data
        self.display('Downloading {} ...'.format(file_name))
        while True:
            data = self.recipient_session.recv(self.chunk_size << 2)
            if data:
                _bytes += data
            else:
                break

        return file_name, _bytes

    def close(self):
        print('\nClosing sFTP ...')
        try:
            self.recipient_session.shutdown(socket.SHUT_RDWR)
            self.recipient_session.close()
        except:
            try:
                self.server_socket.shutdown(socket.SHUT_RDWR)
                self.server_socket.close()
            except:pass

        try:
            del self.recipient_session
        except:
            try:
                del self.server_socket
            except:pass

    def send(self, file):
        if not os.path.exists(file):
            self.display('File `{}` does not exist'.format(file))
            self.error_code = -1
            return

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.settimeout(self.max_time)

        try:
            self.server_socket.bind((self.ip, self.port))
            self.server_socket.listen(1)
        except OSError:
            self.display('Failed to start FTP server on {}:{}'.format(self.ip, self.port))
            self.error_code = -1

        try:
            session, addr = self.server_socket.accept()
            self.recipient_session = ssl.wrap_socket(session, server_side=True, certfile=CERT_FILE, keyfile=KEY_FILE)
        except TimeOutError:
            self.display('Server timed out')
            self.error_code = -1

        try:
            started = time()
            self.send_file(file)
            self.time_elapsed = (time() - started)
            self.display('Time-elapsed: {}(sec)'.format(time() - started))
        except:
            self.error_code = -1
        finally:
            self.close()

    def recv(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.settimeout(self.max_time)

        try:
            self.server_socket.bind((self.ip, self.port))
            self.server_socket.listen(1)
        except OSError:
            self.display('Failed to start FTP server on {}:{}'.format(self.ip, self.port))
            self.error_code = -1

        try:
            session, addr = self.server_socket.accept()
            self.recipient_session = ssl.wrap_socket(session, server_side=True, certfile=CERT_FILE, keyfile=KEY_FILE)
        except TimeOutError:
            self.display('Server timed out')
            self.error_code = -1

        try:
            started = time()
            file_name, data = self.recv_file()
            File.write(file_name, data)
            self.time_elapsed = (time() - started)
            self.display('Time-elapsed: {}(sec)'.format(time() - started))
        except:
            self.error_code = -1
        finally:
            self.close()
