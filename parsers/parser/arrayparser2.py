from threading import Thread

from parsers.frame_group.arrbuf2 import ArrayBuffer2
from parsers.stream.pack import RPackSt


class ArrayParser2(Thread):
    def __init__(self, p_st: RPackSt, frame_shape, dtype, buff_kb):
        """
        :param p_st:      pack stream
        :param frame_shape:  shape of a frame
        :param buff_kb:      numpy cache size
        :param dtype:        numpy dtype
        """
        super().__init__()
        if frame_shape is None:
            frame_shape = ()
        buf_shape = (None, *frame_shape)
        self.a_buf = ArrayBuffer2(buf_shape, dtype, buff_kb)
        self.p_st = p_st

    def run(self):
        while True:
            pack = self.p_st.get_pack()
            self.a_buf.put_bytes(pack)
