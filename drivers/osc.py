import struct

import numpy as np

from drivers.usbd import USBDevice
from parsers.buffer.nxtranbuf import NxTranBufRead
from parsers.parser.arrayparser2 import ArrayParser2
from parsers.stream.pack import RPackStSplit


class MyOscConfig:
    def __init__(self, ContinuousConvMode=False, Channel=1, SamplingTime=2, sps=10000):
        self.ContinuousConvMode = ContinuousConvMode
        self.Channel = Channel
        self.SamplingTime = SamplingTime
        self.TIM_AutoLoad = 84000000//sps-1  # TODO: read STM32 clock
        self.TIM_Compare = self.TIM_AutoLoad//2
        self._sps = sps

    @property
    def sps(self):
        return self._sps

    @sps.setter
    def sps(self, value):
        self.TIM_AutoLoad = int(84000000//value)-1
        self.TIM_Compare = self.TIM_AutoLoad//2
        self._sps = 84000000/(self.TIM_AutoLoad + 1)

    def usb_pack(self):
        return struct.pack('IIIII',
                           self.ContinuousConvMode,
                           self.Channel,
                           self.SamplingTime,
                           self.TIM_AutoLoad,
                           self.TIM_Compare)


class Oscilloscope:
    def __init__(self, usbd: USBDevice):
        self.usbd = usbd
        self.conf = MyOscConfig()
        self.t_buf = NxTranBufRead(usbd)
        self.split = RPackStSplit(self.t_buf)
        self.split.st[0].r_len = 64
        self.split.start()
        p_st = self.split.st[0]
        self.ap = ArrayParser2(p_st, None, np.uint16, 100)
        self.ap.a_buf.add_head()
        self.ap.start()

    @property
    def sps(self):
        return self.conf.sps

    @sps.setter
    def sps(self, value):
        if value != self.conf.sps:
            self.conf.sps = value
            pack = self.conf.usb_pack()
            print(self.conf.sps, 'sps')
            self.usbd.write(pack)
