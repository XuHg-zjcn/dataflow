class ArrBufHead:
    def __init__(self, a_buf, curr_g, offset=0):
        """
        :param a_buf: array buffer
        :param curr_g: current group
        :param offset: offset of group
        """
        self.a_buf = a_buf
        self.curr_g = curr_g
        self._offset = offset

    def fid(self):
        return self.curr_g.fid + self._offset


class ArrBufHeadPut(ArrBufHead):
    """
    per array buffer can only one put head.
    """
    def __init__(self, a_buf, curr_g, fpg=None):
        """
        :param a_buf: array buffer
        :param curr_g: current group
        :param fpg: auto split frames per group.
        """
        super().__init__(a_buf, curr_g)
        self.fpg = fpg

    def next_group(self, length=None):
        length = length or self.offset
        assert length <= self.offset, 'frames not enough'

    @property
    def offset(self):
        return self._offset

    @offset.setter
    def offset(self, value):
        self._offset = value
        if self.fpg and self.offset >= self.fpg:
            self.next_group(self.fpg)

    def get_last(self, n):
        fid = self.fid()
        return self.a_buf[max(fid-n, 0):fid]


class ArrBufHeadGet(ArrBufHead):
    """
    an array buffer can have many get head.
    """
    def get_frames(self, n):
        fid = self.fid()
        fid_e = fid+n

        self.a_buf.cond.acquire()
        while self.a_buf.total_put <= fid_e:
            self.a_buf.cond.wait()
        self.a_buf.cond.release()

        ret = self.a_buf[fid: fid+n]
        self._offset += n
        while self.curr_g.length and self._offset <= self.curr_g.length:
            self.next_group()
        return ret

    def next_group(self):
        self._offset -= self.curr_g.length
        self.curr_g = self.a_buf.groups[self.curr_g.gid+1]

    def get_group(self):
        fid = self.fid()
        if self.curr_g.length is None:
            return self.a_buf[fid:]
        else:
            return self.a_buf[fid: fid+self.curr_g.length]
