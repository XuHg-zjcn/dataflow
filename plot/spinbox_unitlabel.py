# some code copy from https://blog.csdn.net/qq_38641985/article/details/83377355
import math
import re
from numbers import Number

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget, QAbstractSpinBox, QLabel, QHBoxLayout

from mylibs.my_list_set import BinarySearch
from mylibs.my_ordered_dict import MyOrderedDict

dict_10x = {'y': -24, 'z': -21, 'a': -18, 'f': -15,
            'p': -12, 'n': -9, 'μ': -6, 'm': -3,
            'c': -2, 'd': -1, '': 0, 'da': 1, 'h': 2,
            'k': 3, 'M': 6, 'G': 9, 'T': 12,
            'P': 15, 'E': 18, 'Z': 21, 'Y': 24}
list_2x = ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi', 'Yi']
re_comp = re.compile(r'^\[(.*)\](.*)$')

inv_10x = {v: k for k,v in dict_10x.items()}
#       i =    0  3/3  6/3 ... 24/3 -24/3 ... -6/3 -3/3
# list_2x =  ['', 'k', 'M', ...,'Y', 'y', ..., 'μ', 'm']
list_10x = [inv_10x[i] for i in range(0, 25, 3)]\
          +[inv_10x[i] for i in range(-24, -2, 3)]


def _level_str2index(x: str) -> (int, int):
    """
    :param x: input string
    :return: (int base, int exp), base**exp == value of level
    """
    if x in list_10x:
        i = list_10x.index(x)
        i = i if i <= len(list_10x)//2 else i-len(list_10x)
        return 1000, i
    elif x in list_2x:
        return 1024, list_2x.index(x)
    elif x == '1':
        return 0, 0  # don't modify, see Line:67-70
    elif x == 'u':
        return 1000, -2
    else:
        raise ValueError(f"unknown orders of magnitude '{x}'")


def _level_str2float(x: str) -> float:
    """
    :param x: input string
    :return: orders of magnitude value
    """
    base, exp = _level_str2index(x)
    return base ** exp


def _parser_units_str(units: str) -> dict:
    lv_str, base_unit = re_comp.match(units).groups()
    lv_split = lv_str.replace(' ', '').split(',')
    ret = {}
    for s in lv_split:
        if ':' in s:
            k, v = s.split(':')
            ret[k+base_unit] = v
        elif '-' in s:
            L, R = s.split('-')
            Lb, Le = _level_str2index(L)
            Rb, Re = _level_str2index(R)
            assert Lb == Rb or Lb * Rb == 0, "range endpoint must same base"\
                                             "or at least endpoint is '1'"
            base = Lb or Rb
            assert Le <= Re, 'range endpoint must left <= right'
            if base == 1000:
                for e in range(Le, Re + 1):
                    ret[list_10x[e]+base_unit] = 1000**e
            elif base == 1024:
                for e in range(Le, Re + 1):
                    ret[list_2x[e]+base_unit] = 1024**e
            elif base == 0:
                ret[base_unit] = 1
            else:
                raise ValueError(f'not expected base={base}')
    return ret


class MySpinBox(QAbstractSpinBox):
    def __init__(self, parent, initText='1'):
        super().__init__(parent)
        self.parent = parent
        self.lineEdit().setText(initText)
        self.enable = QAbstractSpinBox.StepUpEnabled | QAbstractSpinBox.StepDownEnabled

    def stepEnabled(self):
        return self.parent.stepEnabled()

    def stepBy(self, steps: int):
        old = int(self.lineEdit().text())
        v_new = self.parent.stepBy(old, steps)
        self.lineEdit().setText(str(v_new))

    def number(self):
        return int(self.lineEdit().text())


class SpinBoxUnitLabel(QWidget):
    valueChange = pyqtSignal(float)

    def initUI(self, nums=None, units=None, init_value=1, limit_range=(None, None)):
        """
        :param nums: list of numbers show on SpinBox, default value:
            [1, 2, 5, 10, 20, 50, 100, 200, 500]

        :param units: unit name->level dict or string expression
            dict form: {'name1': level1, 'name2': level2}
                example: {'ms: 1e-3, 's': 1, 'min': 60, 'hour': 3600, 'days': 86400}
            expression form: '[y, z, a, f, p, n, μ/u, m, (c, d),
                              1, (da, h), k, M, G, T, P, E, Z, Y,
                              Ki, Mi, Gi, Ti, Pi, Ei, Zi, Yi,
                              str:float]base_unit'
                in square brackets, use comma split:
                single |'*'         | SI Order of magnitude headings
                range  |'*-*'       | skip 'c', 'd', 'da', 'h', contains both endpoints
                custom |'str:float' | user custom

                '1' will doesn't show.
                'c', 'd', 'da', 'h' can only in single, can't be range endpoint
                if '*i' in range endpoint, another range must '1' or also '*i'
                example: '[μ-k,c]m', '[μ-1]V', '[h]pa', '[1-Ti]Bytes', '[1, w:1e4]RMB'
            default value is [y-Y]
        :param init_value: init value
        :param limit_range: range of value limit
        """
        if nums is None:
            nums = [1, 2, 5, 10, 20, 50, 100, 200, 500]
        else:
            nums = sorted(nums)
        self.nums = nums
        if units is None:
            units = '[y-Y]'
        if isinstance(units, str):
            units = _parser_units_str(units)
        self.units = MyOrderedDict.fromSortedValues(units)
        self.init_value = init_value
        num, label = self._FindValueNeatest(self.init_value)
        self.spinbox = MySpinBox(self, str(num))
        self.label = QLabel(label)
        self.limit_range = limit_range
        hbox = QHBoxLayout()
        hbox.addWidget(self.spinbox)
        hbox.addWidget(self.label)
        self.setLayout(hbox)

    def value(self):
        text = self.label.text()
        return self.spinbox.number() * self.units[text]

    def _FindValueNeatest(self, value):
        unit_i = BinarySearch(self.units.values, value / self.nums[0])
        assert 0 <= unit_i, 'value too small'
        unit_name = self.units.keys[int(unit_i)]
        unit_value = self.units.values[int(unit_i)]

        show_value = value / unit_value
        value_i = BinarySearch(self.nums, show_value)
        show_value2 = self.nums[round(value_i)]
        return show_value2, unit_name

    def setValueNeatest(self, value):
        show_value2, unit_name = self._FindValueNeatest(value)
        self.label.setText(unit_name)
        self.spinbox.lineEdit().setText(str(show_value2))

    def unit_change(self, diff):
        """
        change unit label, return number should

        :param diff: -1, 0, 1
        :return:
        """
        assert diff in {-1, 0, 1}
        value = self.value()
        old_unit = self.label.text()
        unit_i = self.units.k2i(old_unit)
        unit_i += diff
        if unit_i < 0:
            raise ValueError('no smaller unit')
        if unit_i >= len(self.units):
            raise ValueError('no bigger unit')
        new_unit = self.units.keys[unit_i]
        num = value / self.units.values[unit_i]
        return num, new_unit

    def stepBy(self, old, steps):
        """
        call by MySpinBox
        :param old: old number in spinbox
        :param steps: -1 or 1
        :return: new number in spinbox
        """
        ni = self.nums.index(old)
        ni += steps
        if ni < 0:
            num, new_unit = self.unit_change(-1)
            ni = BinarySearch(self.nums, num)
            ni = math.ceil(ni) - 1  # ni-1 <= ni' < ni, ni' is integrate
            self.label.setText(new_unit)
        elif ni >= len(self.nums):
            num, new_unit = self.unit_change(1)
            ni = BinarySearch(self.nums, num)
            self.label.setText(new_unit)
            ni = math.floor(ni) + 1  # ni < ni' <= ni+1, ni' is integrate
        else:
            new_unit = self.label.text()
        unit_value = self.units[new_unit]
        new_num = self.nums[ni]
        self.valueChange.emit(new_num * unit_value)
        return new_num

    def stepEnabled(self):
        num = self.spinbox.number()
        unit = self.label.text()
        ret = QAbstractSpinBox.StepUpEnabled | QAbstractSpinBox.StepDownEnabled
        if unit == self.units.keys[-1] and num == self.nums[-1]:
            ret &= ~QAbstractSpinBox.StepUpEnabled
        if unit == self.units.keys[0] and num == self.nums[0]:
            ret &= ~QAbstractSpinBox.StepDownEnabled
        value = self.units[unit] * num
        lower, upper = self.limit_range  # bounds
        if isinstance(lower, Number) and value <= lower:
            ret &= ~QAbstractSpinBox.StepDownEnabled
        if isinstance(upper, Number) and value >= upper:
            ret &= ~QAbstractSpinBox.StepUpEnabled
        return ret
