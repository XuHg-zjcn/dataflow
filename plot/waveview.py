# -*- coding: utf-8 -*-
"""
Various methods of drawing scrolling plots.
"""
import pyqtgraph as pg


class WaveItem(pg.PlotCurveItem):
    def __init__(self, signal):
        """
        :param signal: ArrayBuffer2
        """
        self.signal = signal
        super().__init__()

    def upd(self):
        y = self.signal.put_head.get_last(128)
        self.setData(y)


## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys
    from PyQt5 import QtCore
    win = pg.GraphicsLayoutWidget(show=True)
    win.setWindowTitle('pyqtgraph example: Scrolling Plots')
    win.addItem()

    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        pg.QtGui.QApplication.instance().exec_()
