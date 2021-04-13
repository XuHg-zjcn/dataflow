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
        self.edit_sDiv.valueChanged.connect(self.sDiv_slot)
        self.osc = osc
        self.plotwidget.getAxis('bottom').setLabel('time', 's')
        wvi = WaveItem(osc.ap.arr_buf)
        self.plotwidget.addItem(wvi)
        wvi.start()
        # TODO: default value move to config file
        self.label_sDiv.setText('ms/div')
        self.edit_sDiv.setValue(50)

    def sDiv_change_unit(self, change=0):
        """change=-1, smaller unit, change=0 not change, change=1, bigger unit"""
        text_old = self.label_sDiv.text()
        i_old = sDiv_label.index(text_old)
        i_new = i_old + change
        if change != 0:
            text_new = sDiv_label[i_new]
            self.label_sDiv.setText(text_new)
        return sDiv_value[i_new]

    def sDiv_slot(self, sDiv):
        sDiv_d = {3:5, 4:2, 6:10, 9:5,
                  11:20, 19:10, 21:50, 49:20, 51:100, 99:50,
                  101:200, 199:100, 201:500, 499:200}
        pass_set = {1, 2, 5, 10, 20, 50, 100, 200, 500}
        v = self.sDiv_change_unit()
        if v == 1 and sDiv == 51:  # 50s/div -> 1min/div
            self.sDiv_change_unit(1)
            self.edit_sDiv.setValue(1)
        elif sDiv in pass_set:
            pass
        elif sDiv in sDiv_d:
            self.edit_sDiv.setValue(sDiv_d[sDiv])
        elif sDiv == 0:
            self.sDiv_change_unit(-1)
            # 1min/div -> 50s/div
            self.edit_sDiv.setValue(500 if v == 60 else 50)
        elif sDiv == 501:
            self.sDiv_change_unit(1)
            self.edit_sDiv.setValue(1)
        else:
            raise ValueError(f'sDiv_slot {sDiv}')
        sDiv_sec = self.sDiv_change_unit(0) * self.edit_sDiv.value()
        sps = 32/sDiv_sec
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
