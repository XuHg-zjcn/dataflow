from parsers.frame_group.frame_group import FrameGroup
from parsers.frame_group.queuelist import QueueList


class GroupList(QueueList):
    def __init__(self, a_buf):
        """
        :param a_buf: array buffer
        """
        super().__init__()
        self.a_buf = a_buf
        self.append(FrameGroup(0, 0))

    def auto_remove(self):
        until = self.a_buf.total_put - self.a_buf.arr.shape[0]
        while self['o', 0].fid > until:
            self.pop(0)

    def next_group(self, length):
        g0 = self['o', -1]
        g0.length = length
        g1 = FrameGroup(g0.gid+1, g0.fid+length)
        self.append(g1)
        self.auto_remove()
