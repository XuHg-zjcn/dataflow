import math

from parsers.buffer.bytebuffer import ByteBuffer


class NxTranBuf:
    """
    per packet in same size.
    """
    def __init__(self, f):
        super().__init__()
        self.f = f


class NxTranBufRead(NxTranBuf):
    def __init__(self, f, r_size=64):
        super().__init__(f)
        self.r_size = r_size
        self.r_buf = ByteBuffer()

    def read(self, n):
        if n > len(self.r_buf):
            s = n - len(self.r_buf)
            s = math.ceil(s / self.r_size) * self.r_size
            self.r_buf.put(self.f.read(s))
        return self.r_buf.get(n)


class NxTranBufWrite(NxTranBuf):
    def __init__(self, f, w_size=64):
        super().__init__(f)
        self.w_size = w_size
        self.w_buf = ByteBuffer()

    def write(self, data):
        self.w_buf.put(data)
        while len(self.w_buf) >= self.w_size:
            self.f.write(self.w_buf.get(self.w_size))


class NxTranBufRW(NxTranBufRead, NxTranBufWrite):
    def __init__(self, f, r_size=1, w_size=1):
        NxTranBufRead.__init__(self, f, r_size)
        NxTranBufWrite.__init__(self, f, w_size)
