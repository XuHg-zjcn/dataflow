import struct

import numpy as np

from drivers.usbd import USBDevice
from parsers.dataparser import ArrayParser


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
        self.ap = ArrayParser(usbd, 100, None, np.uint16, 128)
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
