"""the file is dumped, please run ./gui.py"""
"""
import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui

from drivers.usbd import USBDevice
from parsers.dataparser import ArrayParser
from plot.waveview import WaveItem"""

if __name__ == '__main__':
    print('the file is dumped, please run ./gui.py')

    """import sys
    usbd = USBDevice(idVendor=0xffff)
    ap = ArrayParser(usbd, 100, None, np.uint16, 128)
    ap.start()

    win = pg.GraphicsLayoutWidget(show=True)
    win.setWindowTitle('WaveItem')

    wvi = WaveItem(ap.arr_buf)
    win.addItem(wvi)
    wvi.start()

    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()"""
