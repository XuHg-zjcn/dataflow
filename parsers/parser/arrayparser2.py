import time

from PyQt5.QtCore import QThread, QMutex

from parsers.stream.pack import RPackSt


class ArrayParser2(QThread):
    def __init__(self, p_st: RPackSt, a_buf):
        """
        :param p_st:   input byte pack stream
        :param a_buf:  output array buffer
        """
        super().__init__()
        self.a_buf = a_buf
        self.p_st = p_st
        self.mutex = QMutex()
        self.pause = False

    def run(self):
        while True:
            if self.pause:  # for other thread lock
                time.sleep(0.001)
            self.mutex.lock()
            pack = self.p_st.get_pack()
            self.a_buf.put_bytes(pack)
            self.mutex.unlock()
