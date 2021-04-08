class ByteBuffer(bytearray):
    def __init__(self):
        super().__init__()

    def put(self, data: bytes):
        self.extend(data)

    def get(self, n: int):
        ret = self[:n]
        self[:n] = b''
        return ret


if __name__ == '__main__':
    import time
    buf = ByteBuffer()
    b = bytes(range(256))
    t0 = time.time()
    for i in range(100000):
        buf.put(b)
    t1 = time.time()
    print(100000*len(b)/(t1-t0)/1e6,'MB/s')
