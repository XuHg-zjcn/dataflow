import struct
import time

from PyQt5.QtCore import QThread, QMutex

from parsers.stream.byte import WByteStSplit
from parsers.stream.pack import BytesPack
from parsers.stream.pack import RPackSt


class RPackStSplit(QThread):
    def __init__(self, f):
        super().__init__()
        self.f = f
        self.st = [RPackSt(self, 0)]
        self.sid = 0
        self.mutex = QMutex()
        self.pause = False

    def run(self):
        while True:
            if self.pause:  # for other thread lock
                time.sleep(0.001)
            self.mutex.lock()
            pack = self.f.read(64)  # max pack size = 65536
            if self.sid is None:
                sid, pid = struct.unpack('BB', pack[:2])
            else:
                sid = self.sid
            stream = self.st[sid]
            # assert pid == stream.pack_count, 'pack id error'
            size = stream.r_len
            # assert pid == stream.pack_count, 'pack id error'
            assert size is None or len(pack) == size,\
                f'req length{size}, but get len{len(pack)}'
            stream.r_queue.put(BytesPack(pack))
            stream.pack_count += 1
            self.mutex.unlock()


class WPackStSplit(WByteStSplit):
    pass
