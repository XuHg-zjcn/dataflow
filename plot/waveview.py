# -*- coding: utf-8 -*-
"""
Various methods of drawing scrolling plots.
"""
from threading import Thread

import pyqtgraph as pg


class WaveViewItem(pg.PlotItem, Thread):
    def __init__(self):
        super().__init__()
        self.signals = []

    def add_signal(self, signal):
        p = self.plot()
        self.signals.append((signal, p))

    def run(self):
        while True:
            for sig, p in self.signals:
                print(sig.get_frames(1)[0, 0])
                p.setData(sig[:, 0])


## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys
    win = pg.GraphicsLayoutWidget(show=True)
    win.setWindowTitle('pyqtgraph example: Scrolling Plots')
    win.addItem()

    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
