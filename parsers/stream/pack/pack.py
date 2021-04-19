import time


class BytesPack(bytes):
    def __new__(cls, value, t0=None):
        slf = super().__new__(cls, value)
        if t0 is None:
            t0 = time.time()
        slf.t0 = t0
        return slf
