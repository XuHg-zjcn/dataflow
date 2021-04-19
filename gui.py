import sys

from PyQt5.QtWidgets import QApplication, QMainWindow

from drivers.osc import Oscilloscope
from drivers.usbd import USBDevice
from plot.main_window import Ui_MainWindow
from plot.waveview import WaveItem

sDiv_label = ['ns/div', 'μs/div', 'ms/div', 's/div', 'min/div']
sDiv_value = [1e-9, 1e-6, 1e-3, 1, 60]


class MyUi_MainWindow(Ui_MainWindow):
    def __init__(self, win, osc):
        self.setupUi(win)
        self.widget.initUI(units='[u-1]s/div', limit_range=(1e-5, 0.1))
        self.osc = osc
        self.plotwidget.getAxis('bottom').setLabel('time', 's')
        wvi = WaveItem(osc.ap.a_buf)
        self.plotwidget.addItem(wvi)
        wvi.start()
        self.widget.setValueNeatest(0.1)
        # TODO: default value move to config file
        self.widget.valueChange.connect(self.sDiv_slot)

    def sDiv_slot(self, sDiv_sec):
        sps = 32 / sDiv_sec
        if sps > 50000:
            sps = 50000  # max sampling rate
        elif sps < 10:
            sps = 10     # min sampling rate
        self.osc.sps = sps
        self.plotwidget.getAxis('bottom').setScale(1/self.osc.sps)


if __name__ == '__main__':
    app = QApplication([])
    win = QMainWindow()
    win.setWindowTitle('STM32 USB Oscilloscope')
    usbd = USBDevice(idVendor=0xffff)
    osc = Oscilloscope(usbd)
    ui = MyUi_MainWindow(win, osc)
    win.show()
    sys.exit(app.exec_())
