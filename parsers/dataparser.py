from collections import namedtuple
from threading import Thread

import numpy as np

from parsers.bytebuffer import ByteBuffer
from parsers.arraybuffer import ArrayBuffer

"""
frame: min time unit
packet: a group of frame though cal `get`

example:
a stereo audio sample rate is 44100Hz
frame shape (2,)
packet shape (n, 2)
n = packet length time * 44100
"""


class DataParser(Thread):
    def __init__(self, f, buff_kb=1024):
        """
        :param f: file
        :param cache: cache size (KiB)
        """
        self.f = f
        super().__init__()

    def get(self):
        pass


Packet = namedtuple('packet', 'array timestamp')


class ArrayParser(DataParser):
    def __init__(self, f, buff_kb, frame_shape, dtype,
                 iopack_bytes=1024, frame_per_pack=1):
        """
        :param f:            call `read` for get data
        :param buff_kb:      numpy cache
        :param frame_shape:  shape of a frame
        :param dtype:        numpy dtype
        :param iopack_bytes: bytes per read
        :param frame_per_pack: number of frame in a packet
        """
        super().__init__(f, buff_kb)
        if isinstance(frame_shape, int):
            frame_shape = (frame_shape,)
        self.frame_shape = tuple(frame_shape)
        self.frame_per_pack = frame_per_pack

        self.dtype = dtype
        fb = self.frame_bytes
        n = iopack_bytes/fb
        if n >= 1:
            iopack_bytes = int(n)*fb
        elif n > 0.2:
            iopack_bytes = fb/int(1/n)
        self.iopack_bytes = iopack_bytes
        buf_frames = int(buff_kb*1024/fb)
        self.arr_buf = ArrayBuffer([buf_frames]+list(frame_shape), dtype)

    @property
    def frame_bytes(self):
        elem_bytes = np.dtype(self.dtype).itemsize
        return np.prod(self.frame_shape)*elem_bytes

    def run(self):
        if self.iopack_bytes < self.frame_bytes:
            while True:
                byte_buf = ByteBuffer()
                byte_buf.put(self.f.read(self.iopack_bytes))
                if len(byte_buf) >= self.frame_bytes:
                    data = byte_buf.get(self.frame_bytes)
                    self.arr_buf.put_bytes(data)
        while True:
            data = self.f.read(self.iopack_bytes)
            self.arr_buf.put_bytes(data)
