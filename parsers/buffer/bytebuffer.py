from threading import Condition


class ByteBuffer(bytearray):
    def __init__(self):
        super().__init__()

    def put(self, data: bytes):
        self.extend(data)

    def get(self, n: int):
        ret = self[:n]
        self[:n] = b''
        return ret

    def get_all(self):
        ret = self[:]
        self.clear()
        return ret


class BlockingByteBuffer(ByteBuffer):
    def __init__(self):
        super().__init__()
        self.cond = Condition()

    def put(self, data: bytes):
        super().put(data)
        self.cond.acquire()
        self.cond.notify()
        self.cond.release()

    def get(self, n: int, blocking=True):
        if blocking:
            self.cond.acquire()
            while len(self) < n:
                self.cond.wait()
            self.cond.release()
        return super().get(n)


if __name__ == '__main__':
    import time
    buf = ByteBuffer()
    b = bytes(range(256))
    t0 = time.time()
    for i in range(100000):
        buf.put(b)
    t1 = time.time()
    print(100000*len(b)/(t1-t0)/1e6,'MB/s')
