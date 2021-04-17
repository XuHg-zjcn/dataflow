from parsers.buffer.bytebuffer import ByteBuffer


class CutTranBuf:
    """
    hold data util min packet size.
    """
    def __init__(self, f):
        super().__init__()
        self.f = f


class CutTranBufRead(CutTranBuf):
    def __init__(self, f, r_size=1):
        super(CutTranBuf, self).__init__(f)
        self.r_size = r_size
        self.r_buf = ByteBuffer()

    def read(self, n):
        if n > len(self.r_buf):
            s = n - len(self.r_buf)
            s = min(s, self.r_size)
            self.r_buf.put(self.f.read(s))
        return self.r_buf.get(n)


class CutTranBufWrite(CutTranBuf):
    def __init__(self, f, w_size=1):
        super().__init__(f)
        self.w_size = w_size
        self.w_buf = ByteBuffer()

    def write(self, data):
        self.w_buf.put(data)
        if len(self.w_buf) >= self.w_size:
            self.f.write(self.w_buf.get_all())


class CutTranBufRW(CutTranBufRead, CutTranBufWrite):
    def __init__(self, f, r_size=1, w_size=1):
        CutTranBufRead.__init__(self, f, r_size)
        CutTranBufWrite.__init__(self, f, w_size)
