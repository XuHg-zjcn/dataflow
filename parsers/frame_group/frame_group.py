import time


class FrameGroup:
    def __init__(self, gid, fid, sr:float=None, t0=None):
        """
        :param gid: group id
        :param fid: first frame id
        :param sr: sample rate(Hz)
        :param t0: time of first frame
        """
        if t0 is None:
            t0 = time.time()
        self.gid = gid
        self.fid = fid
        self.sr = sr
        self.t0 = t0
        self._length = None

    @property
    def length(self):
        return self._length

    @length.setter
    def length(self, value):
        self._length = value
        if self.sr is None:
            now = time.time()
            self.sr = value / (now - self.t0)
