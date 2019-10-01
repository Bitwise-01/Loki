# Date: 06/02/2018
# Author: Pure-L0G1C
# Description: Session

import json
import socket
from time import sleep
from lib.info import Information
from socket import timeout as TimeOutError


class Session(object):

    def __init__(self, session):
        self.session = session
        self.sys_info = Information().get_info()

    def shutdown(self):
        try:
            self.session.shutdown(socket.SHUT_RDWR)
            self.session.close()
        except:
            pass

    def initial_communication(self):
        sleep(0.5)
        self.send(args=self.sys_info)
        services = self.recv()
        return services

    def connect(self, ip, port):
        try:
            self.session.connect((ip, port))
            print('Establishing a secure connection ...')
            return self.initial_communication()
        except:
            pass

    def struct(self, code=None, args=None):
        return json.dumps({'code': code, 'args': args}).encode()

    def send(self, code=None, args=None):
        data = self.struct(code, args)
        try:
            self.session.sendall(data)
        except:
            pass

    def recv(self, size=4096):
        try:
            return json.loads(self.session.recv(size))
        except TimeOutError:
            return -1
        except:
            pass
