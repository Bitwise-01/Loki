# Date: 08/24/2018
# Author: Pure-L0G1C
# Description: Arguments

from os import path
from re import match
from argparse import ArgumentParser


class Args(object):

    def __init__(self):
        self.ip = None
        self.port = None
        self.name = None
        self.type = None
        self.hide = None
        self.wait = None
        self.icon = None
        self.delay = None
        self.persist = None

    def error(self, error):
        print('Error: {}'.format(error))

    def get_args(self):
        parser = ArgumentParser()

        parser.add_argument('-i',
                            '--ip',
                            required=True,
                            help='the ip of the C&C server. \
                            Example: -i 127.0.0.1')

        parser.add_argument('-p',
                            '--ports',
                            required=True,
                            help='the port of the C&C server. \
                            Example: -p 8080')

        parser.add_argument('-n',
                            '--name',
                            required=True,
                            help='the name of the output file. \
                            Example: -n myvirus')

        parser.add_argument('-d',
                            '--delay',
                            default=17,
                            help='time in seconds before upacking. \
                            Example: -d 17')

        parser.add_argument('-w',
                            '--wait',
                            default=17,
                            help='time in seconds before calling C&C. \
                            Example: -w 17')

        parser.add_argument('-t',
                            '--type',
                            default='exe',
                            help='the output type.\
                            Example: -t python \
                            Example: -t exe')

        parser.add_argument('-ic',
                            '--icon',
                            default=None,
                            help='the output type.\
                            Example: -ic FILE.ico \
                            Example: -ic FILE.exe')

        parser.add_argument('-hd',
                            '--hide',
                            default=False,
                            action='store_true',
                            help='hide the executable when executed. \
                            Example: --hide')

        parser.add_argument('-ap',
                            '--autopersist',
                            default=False,
                            dest='persist',
                            action='store_true',
                            help='Auto persist when executed. \
                            Example: -ap')

        return parser.parse_args()

    def set_args(self):
        args = self.get_args()
        self.ip = args.ip
        self.port = args.ports
        self.name = args.name
        self.type = args.type
        self.hide = args.hide
        self.wait = args.wait
        self.icon = args.icon
        self.delay = args.delay
        self.persist = args.persist

        if any([not self.valid_ip, not self.valid_port, not self.valid_type, not self.valid_wait, not self.valid_delay, not self.valid_icon]):
            return False
        return True

    @property
    def valid_ip(self):
        if not match(r'^(?!0)(?!.*\.$)((1?\d?\d|25[0-5]|2[0-4]\d)(\.|$)){4}$', self.ip):
            self.error('Invalid IP address')
            return False
        return True

    @property
    def valid_port(self):
        #  check if number
        for item in self.port:
            if not item.isdigit():
                return False

        # check if number starts with a zero
        if int(self.port[0]) == 0:
            return False

        # check if number is larger than 65535
        if int(self.port) > 65535:
            return False
        self.port = int(self.port)
        return True

    @property
    def valid_type(self):
        if not any([self.type == 'exe', self.type == 'python']):
            self.error('Invalid type')
            return False
        self.type = True if self.type == 'exe' else False
        return True

    @property
    def valid_icon(self):
        if not self.icon:
            return True
        if not path.exists(self.icon):
            self.error(
                'Check your path to your icon, `{}` does not exist'.format(self.icon))
            return False
        else:
            if not any([self.icon.endswith('exe'), self.icon.endswith('ico')]):
                self.error('Icon file must be a .ico or .exe')
                return False
        return True

    @property
    def valid_delay(self):
        delay = str(self.delay)
        if not delay.isdigit():
            self.error('Delay must be a number')
            return False
        elif int(delay) < 17:
            self.error('Delay must not be less than 17')
            return False
        else:
            self.delay = int(delay)
        return True

    @property
    def valid_wait(self):
        wait = str(self.wait)
        if not wait.isdigit():
            self.error('Wait must be a number')
            return False
        elif int(wait) < 17:
            self.error('Wait must not be less than 17')
            return False
        else:
            self.wait = int(wait)
        return True
