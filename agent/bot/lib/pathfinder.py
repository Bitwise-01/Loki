# Date: 08/31/2018
# Author: Pure-L0G1C
# Description: Finds a random path

import os
from random import randint
from getpass import getuser


class Finder(object):

    root_dir = os.path.abspath(os.path.sep) + os.path.sep + \
        'Users' + os.path.sep + getuser() + os.path.sep + 'AppData'

    @staticmethod
    def is_bad(root, dirs, files):
        return not all([len(dirs), len(files), len(os.path.normpath(root).split(os.sep)) >= 5])

    @staticmethod
    def choice(items):
        for _ in range(randint(3, 10)):
            n = randint(0, len(items)-1)
        return items[n]

    @classmethod
    def find(cls):
        paths = []
        for root, dirs, files in os.walk(cls.root_dir, topdown=True):
            if cls.is_bad(root, dirs, files):
                continue
            _dir = cls.choice(dirs)
            if '.' in _dir:
                continue
            else:
                path = root + os.path.sep + _dir
                paths.append(path)
        return cls.choice(paths) + os.path.sep
