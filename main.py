import numpy as np

from drivers.usbd import USBDevice
from parsers.dataparser import ArrayParser

if __name__ == '__main__':
    usbd = USBDevice(idVendor=0xffff)
    ap = ArrayParser(usbd, 100, 8, np.uint16, 64)
    ap.start()
    while True:
        frame = ap.arr_buf.get_frames(1)
        print(frame)
