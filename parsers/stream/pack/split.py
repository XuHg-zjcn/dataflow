from threading import Thread

from parsers.stream.byte import WByteStSplit
from parsers.stream.pack import BytesPack
from parsers.stream.pack import RPackSt


class RPackStSplit(Thread):
    def __init__(self, f):
        super().__init__()
        self.f = f
        self.st = [RPackSt(self, 0)]

    def run(self):
        while True:
            sid, pid = self.f.read(2)
            stream = self.st[sid]
            assert pid == stream.pack_count, 'pack id error'
            size = stream.r_len
            if size is None:
                size = int(self.f.read(2))
            stream.r_queue.put(BytesPack(self.f.read(size)))
            stream.pack_count += 1


class WPackStSplit(WByteStSplit):
    pass
