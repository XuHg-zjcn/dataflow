from threading import Thread

from parsers.stream.byte import RByteSt, WByteSt


class RByteStSplit(Thread):
    def __init__(self, f):
        super().__init__()
        self.f = f
        self.st = [RByteSt(self, 0)]

    def run(self):
        while True:
            sid, pid = self.f.read(2)
            stream = self.st[sid]
            assert pid == stream.pack_count, 'pack id error'
            size = stream.r_len
            if size is None:
                size = int(self.f.read(2))
            stream.r_buf.put(self.f.read(size))
            stream.pack_count += 1


class WByteStSplit:
    def __init__(self, f):
        super().__init__()
        self.f = f
        self.st = [WByteSt(self, 0)]

    def send(self, sid, data):
        stream = self.st[sid]
        head = [sid, stream.pack_count % 0xff]
        ld = len(data)
        if stream.w_len is None:
            assert ld <= 65535, 'only support max length 65535'
            head.append(ld // 256)
            head.append(ld % 256)
        else:
            assert ld == stream.w_len, 'len(data) != default length'
        self.f.write(bytes(head))
        self.f.write(data)
