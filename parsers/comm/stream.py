from parsers.buffer.bytebuffer import BlockingByteBuffer


class Stream:
    def __init__(self, spt, sid):
        self.spt = spt
        self.sid = sid


class ReadStream(Stream):
    def __init__(self, spt, sid):
        super().__init__(spt, sid)
        self.r_buf = BlockingByteBuffer()
        self.r_len = None  # default length of pack
        self.pack_count = 0

    def read(self, n):
        return self.r_buf.get(n)


class WriteStream(Stream):
    def __init__(self, spt, sid):
        super().__init__(spt, sid)
        self.w_len = None  # default length of pack
        self.pack_count = 0

    def write(self, data):
        self.spt.send(self.sid, data)
        self.pack_count += 1


class RWStream(ReadStream, WriteStream):
    def __init__(self, spt, sid):
        ReadStream.__init__(self, spt, sid)
        WriteStream.__init__(self, spt, sid)
