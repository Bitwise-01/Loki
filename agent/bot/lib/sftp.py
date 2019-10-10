# Date: 07/27/2018
# Author: Pure-L0G1C
# Description: Secure FTP

import os
import ssl
import socket
from os import chdir
from . import screen
from . file import File
from time import sleep, time
from socket import timeout as TimeOutError


class sFTP(object):

    def __init__(self, ip, port, home, max_time=10, verbose=False):
        self.ip = ip
        self.port = port
        self.home = home
        self.verbose = verbose
        self.max_time = max_time
        self.chunk_size = 0xffff
        self.session_size = 0x1000
        self.recipient_session = None

    def display(self, msg):
        if self.verbose:
            print('{}\n'.format(msg))

    def read_file(self, file):
        with open(file, 'rb') as f:
            while True:
                data = f.read(self.chunk_size)
                if data:
                    yield data
                else:
                    break

    def send_file(self, file):
        chdir(self.home)
        if not os.path.exists(file):
            self.display('File `{}` does not exist'.format(file))
            return -1

        # send file's name
        sleep(0.5)
        print('Sending file\'s name ...')
        self.recipient_session.sendall(os.path.basename(file).encode('utf8'))

        # send file's data
        sleep(0.5)
        self.display('Sending {} ...'.format(file))

        chdir(self.home)
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
        try:
            self.recipient_session.close()
            self.recipient_session.shutdown(socket.SHUT_RDWR)
        except:
            pass

    def socket_obj(self):
        chdir(self.home)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        try:
            self.recipient_session = ssl.wrap_socket(
                sock, ssl_version=ssl.PROTOCOL_SSLv23)
            self.recipient_session.connect((self.ip, self.port))
        except:
            return -1

    def send(self, file):
        if self.socket_obj() == -1:
            return -1
        try:
            started = time()
            self.send_file(file)
            self.display('Time-elapsed: {}(sec)'.format(time() - started))
        except:
            pass
        finally:
            self.close()

    def recv(self):
        if self.socket_obj() == -1:
            return -1
        try:
            started = time()
            file_name, data = self.recv_file()
            chdir(self.home)
            File.write(file_name, data)
            self.display('Time-elapsed: {}(sec)'.format(time() - started))
        except:
            pass
        finally:
            self.close()
