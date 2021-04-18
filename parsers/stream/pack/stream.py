from queue import Queue

from parsers.stream.pack import BytesPack


class PackStream:
    def __init__(self, spt, sid):
        self.spt = spt
        self.sid = sid


class ReadPackStream(PackStream):
    def __init__(self, spt, sid):
        super().__init__(spt, sid)
        self.r_queue = Queue()
        self.r_len = None  # default length of pack
        self.pack_count = 0

    def get_pack(self, blocking, timeout):
        return self.r_queue.get(blocking, timeout)


class WritePackStream(PackStream):
    def __init__(self, spt, sid):
        super().__init__(spt, sid)
        self.w_len = None  # default length of pack
        self.pack_count = 0

    def send_pack(self, pack: BytesPack):
        self.spt.send(self.sid, pack)
        self.pack_count += 1


class RWPackStream(ReadPackStream, WritePackStream):
    def __init__(self, spt, sid):
        ReadPackStream.__init__(self, spt, sid)
        WritePackStream.__init__(self, spt, sid)