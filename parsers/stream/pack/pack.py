import time


class BytesPack(bytes):
    def __init__(self, value, t0=None):
        super().__init__(value)
        if t0 is None:
            t0 = time.time()
        self.t0 = t0
