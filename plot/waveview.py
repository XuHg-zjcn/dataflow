# -*- coding: utf-8 -*-
"""
Various methods of drawing scrolling plots.
"""
from threading import Thread
import time

import pyqtgraph as pg


class WaveViewItem(pg.PlotItem, Thread):
    def __init__(self):
        super().__init__()
        self.signals = []
        self.showGrid(x=True, y=True)
        self.getAxis('bottom').setLabel('time', 's')

    def add_signal(self, signal):
        p = self.plot()
        self.signals.append((signal, p))

    def run(self):
        while True:
            t0 = time.time()
            for sig, p in self.signals:
                p.setData(sig.get_last_frames(512))
                sig.get_frames(32)
            t1 = time.time()
            print(32/(t1-t0))


## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys
    win = pg.GraphicsLayoutWidget(show=True)
    win.setWindowTitle('pyqtgraph example: Scrolling Plots')
    win.addItem()

    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
