import struct

import numpy as np

from drivers.usbd import USBDevice
from parsers.buffer.nxtranbuf import NxTranBufRead
from parsers.frame_group.arrbuf2 import PyQtArrayBuffer
from parsers.parser.arrayparser2 import ArrayParser2
from parsers.stream.pack import RPackStSplit

max_pack_size = 32 # sample
sec_pack = 0.02    # used to set pack size, in slow sample rate


class MyOscConfig:
    def __init__(self, ContinuousConvMode=False, Channel=1, SamplingTime=2, sps=10000):
        self.ContinuousConvMode = ContinuousConvMode
        self.Channel = Channel
        self.SamplingTime = SamplingTime
        self.TIM_AutoLoad = 84000000//sps-1  # TODO: read STM32 clock
        self.TIM_Compare = self.TIM_AutoLoad//2
        self._sps = sps
        self._pack_size = max_pack_size
        self._num_packs = 0

    @property
    def sps(self):
        return self._sps

    @sps.setter
    def sps(self, value):
        self.TIM_AutoLoad = int(84000000//value)-1
        self.TIM_Compare = self.TIM_AutoLoad//2
        self._sps = 84000000/(self.TIM_AutoLoad + 1)
        Byte = int(self._sps * sec_pack)
        self._pack_size = min(max(Byte, 1), 32)

    def usb_pack(self):
        return struct.pack('IIIIIII',
                           self.ContinuousConvMode,
                           self.Channel,
                           self.SamplingTime,
                           self.TIM_AutoLoad,
                           self.TIM_Compare,
                           self._pack_size,
                           self._num_packs)

    @property
    def pack_size(self):
        return self._pack_size


class Oscilloscope:
    def __init__(self, usbd: USBDevice):
        self.usbd = usbd
        self.conf = MyOscConfig()
        self.t_buf = NxTranBufRead(usbd)
        # split
        self.split = RPackStSplit(self.t_buf)
        p_st = self.split.st[0]
        p_st.r_len = 64
        # array buffer
        self.a_buf = PyQtArrayBuffer((None,), np.uint16, 100)
        self.a_buf.add_head()
        # parser
        self.ap = ArrayParser2(p_st, self.a_buf)
        self.sps = 1000
        self.ap.start()
        self.split.start()

    @property
    def sps(self):
        return self.conf.sps

    def pause_all(self):
        self.split.pause = True
        self.ap.pause = True
        self.split.mutex.lock()
        self.ap.mutex.lock()

    def resume_all(self):
        self.split.pause = False
        self.ap.pause = False
        self.split.mutex.unlock()
        self.ap.mutex.unlock()

    @sps.setter
    def sps(self, value):
        if value != self.conf.sps:
            self.conf.sps = value
            pack = self.conf.usb_pack()
            p_st = self.split.st[0]
            # operate in pause mode
            self.pause_all()
            while p_st.r_queue.qsize() > 0:
                p_st.r_queue.get()
            self.t_buf.clear()
            self.t_buf.r_size = self.conf.pack_size*2
            self.split.st[0].r_len = self.conf.pack_size*2
            self.usbd.write(pack)
            self.resume_all()

            print(self.conf.sps, 'sps')
