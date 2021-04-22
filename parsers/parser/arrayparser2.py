from threading import Thread

from parsers.stream.pack import RPackSt


class ArrayParser2(Thread):
    def __init__(self, p_st: RPackSt, a_buf):
        """
        :param p_st:   input byte pack stream
        :param a_buf:  output array buffer
        """
        super().__init__()
        self.a_buf = a_buf
        self.p_st = p_st

    def run(self):
        while True:
            pack = self.p_st.get_pack()
            self.a_buf.put_bytes(pack)
