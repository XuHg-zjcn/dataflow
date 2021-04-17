from threading import Thread

from parsers.comm.stream import ReadStream, WriteStream


class ReadStreamSplit(Thread):
    def __init__(self, f, size):
        super().__init__()
        self.f = f
        self.size = size
        self.st = [ReadStream(self, 0)]

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


class WriteStreamSplit:
    def __init__(self, f, size):
        super().__init__()
        self.f = f
        self.size = size
        self.st = [WriteStream(self, 0)]

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
