# Date: 08/31/2018
# Author: Pure-L0G1C
# Description: File manager


class File(object):

    chunk_size = (64 << 10) - 1

    @classmethod
    def read(cls, file, _bytes=True):
        with open(file, 'rb' if _bytes else 'rt') as f:
            while True:
                data = f.read(cls.chunk_size)
                if data:
                    yield data
                else:
                    break

    @classmethod
    def write(cls, file, data):
        with open(file, 'wb') as f:
            for n in range(0, len(data), cls.chunk_size):
                _max = n + cls.chunk_size
                _data = data[n:_max]
                f.write(_data.encode() if isinstance(_data, str) else _data)
