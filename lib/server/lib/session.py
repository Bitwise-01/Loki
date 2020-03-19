# Date: 06/02/2018
# Author: Pure-L0G1C
# Description: Session

import time
import json
import socket


class Session(object):

    def __init__(self, session, ip):
        self.ip = ip[0]
        try:
            self.session = session
        except:
            pass

    def initial_communication(self):
        try:
            data = self.recv()
            return data
        except:
            pass

    def close(self):
        try:
            self.session.close()
            self.session.shutdown(socket.SHUT_RDWR)
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
        except:
            pass
