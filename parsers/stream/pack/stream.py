from queue import Queue

from parsers.stream.pack import BytesPack


class PackSt:
    def __init__(self, spt, sid):
        self.spt = spt
        self.sid = sid


class RPackSt(PackSt):
    def __init__(self, spt, sid):
        super().__init__(spt, sid)
        self.r_queue = Queue()
        self.r_len = None  # default length of pack
        self.pack_count = 0

    def get_pack(self, blocking, timeout):
        return self.r_queue.get(blocking, timeout)


class WPackSt(PackSt):
    def __init__(self, spt, sid):
        super().__init__(spt, sid)
        self.w_len = None  # default length of pack
        self.pack_count = 0

    def send_pack(self, pack: BytesPack):
        self.spt.send(self.sid, pack)
        self.pack_count += 1


class RWPackSt(RPackSt, WPackSt):
    def __init__(self, spt, sid):
        RPackSt.__init__(self, spt, sid)
        WPackSt.__init__(self, spt, sid)
