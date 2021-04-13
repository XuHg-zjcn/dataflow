import time
from drivers.osc import Oscilloscope
from drivers.usbd import USBDevice


if __name__ == '__main__':
    usbd = USBDevice(idVendor=0xffff)
    osc = Oscilloscope(usbd)
    osc.sps = 500000
    n = 64
    while True:
        t0 = time.time()
        b = usbd.read(n)
        t1 = time.time()
        print(len(b)/(t1 - t0))