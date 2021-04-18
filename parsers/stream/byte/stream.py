from parsers.buffer.bytebuffer import BlockingByteBuffer


class ByteSt:
    def __init__(self, spt, sid):
        self.spt = spt
        self.sid = sid


class RByteSt(ByteSt):
    def __init__(self, spt, sid):
        super().__init__(spt, sid)
        self.r_buf = BlockingByteBuffer()
        self.r_len = None  # default length of pack
        self.pack_count = 0

    def read(self, n):
        return self.r_buf.get(n)


class WByteSt(ByteSt):
    def __init__(self, spt, sid):
        super().__init__(spt, sid)
        self.w_len = None  # default length of pack
        self.pack_count = 0

    def write(self, data):
        self.spt.send(self.sid, data)
        self.pack_count += 1


class RWByteSt(RByteSt, WByteSt):
    def __init__(self, spt, sid):
        RByteSt.__init__(self, spt, sid)
        WByteSt.__init__(self, spt, sid)
