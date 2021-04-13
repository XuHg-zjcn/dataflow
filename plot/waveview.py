# -*- coding: utf-8 -*-
"""
Various methods of drawing scrolling plots.
"""
from threading import Thread
import time

import pyqtgraph as pg


class WaveItem(pg.PlotCurveItem, Thread):
    def __init__(self, signal):
        super().__init__()
        self.signal = signal

    def run(self):
        i = 0
        t0 = time.time()
        while True:
            y = self.signal.get_last_frames(128)
            self.setData(y)
            self.signal.get_frames(128)
            i += 1
            t1 = time.time()  # TODO: show kb/s on GUI
            if t1 - t0 > 5:
                print(128*i / (t1 - t0))
                t0 = time.time()
                i = 0


## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys
    win = pg.GraphicsLayoutWidget(show=True)
    win.setWindowTitle('pyqtgraph example: Scrolling Plots')
    win.addItem()

    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        pg.QtGui.QApplication.instance().exec_()
