import numpy as np
from PyQt5.QtCore import pyqtSignal, QObject

from parsers.frame_group.arrbuf_head import ArrBufHeadPut, ArrBufHeadGet
from parsers.frame_group.grouplist import GroupList


def _unpack_indexes(indexes):
    if isinstance(indexes, tuple):
        return indexes[0], list(indexes[1:])
    else:
        return indexes, []


def kb2frames(frame_shape, dtype, kb):
    elem_bytes = np.dtype(dtype).itemsize
    elems = int(np.prod(frame_shape))
    bytes_frame = elems * elem_bytes
    Bytes = kb * 1024
    return Bytes // bytes_frame


class ArrayBuffer2:
    """
    array buffer single input multiply output.
    not blocking for put data, auto overwrite.
    # TODO: auto extend, keep data until all heads geted.

     ______________________________________________
    |/////////|||||||||||||||||||||||||||||||||||||   numpy array
    | Group5 | Group1 | Group2 | G3 |   Group 4   |   FrameGroup
             ^              |            |
             |              v            v
         put_head      get_head0     get_head1        Heads

    in cycle write buffer:
    frame id(fid) keep increase, index will reset to 0 during overflow.
    """
    def __init__(self, shape, dtype, kb=None):
        if shape[0] is None:
            frames = kb2frames(shape[1:], dtype, kb)
            shape = (frames, *shape[1:])
        self.arr = np.ndarray(shape, dtype)
        self.groups = GroupList(self)  # list faster than queue by test.
        self.put_head = ArrBufHeadPut(self, self.groups[0])
        self.get_heads = []
        self.total_put = 0

    def is_gettable(self, fid):
        if fid >= self.total_put:
            return False  # no putted
        elif fid < self.total_put - self.arr.shape[0]:
            return False  # already overwrite
        else:
            return True

    def fid2index(self, fid, check=True):
        if check:
            assert self.is_gettable(fid), 'not gettable'
        return fid % (self.arr.shape[0])

    def put_arr(self, arr):
        arr = np.array(arr)  # convert to numpy array
        if arr.ndim == self.arr.ndim-1:
            arr = arr[np.newaxis, ...]
        if self.arr.ndim > 1:  # check shape
            assert self.arr.shape[1:] == arr.shape[-(self.arr.ndim-1):],\
                   (f'put array shape{arr.shape} last {self.arr.ndim-1} dims'
                    f'must same to frame shape{self.arr.shape[1:]}')
        start = self.fid2index(self.put_head.fid(), check=False)
        stop = start + arr.shape[0]
        if stop <= self.arr.shape[0]:
            self.arr[start:stop] = arr
        else:
            spt = self.arr.shape[0] - start
            stop -= self.arr.shape[0]
            self.arr[start:] = arr[:spt]
            self.arr[:stop] = arr[spt:]
        self.put_head.offset += arr.shape[0]
        self.total_put += arr.shape[0]

    def put_bytes(self, data: bytes):
        tmp = np.frombuffer(data, dtype=self.arr.dtype)
        tmp = tmp.reshape([-1] + list(self.arr.shape[1:]))
        self.put_arr(tmp)

    def __getitem__(self, item):
        fsli, oindex = _unpack_indexes(item)
        if isinstance(fsli, int):
            fsli = self.fid2index(fsli)
        elif isinstance(fsli, slice):
            start = fsli.start or 0
            stop = fsli.stop or self.total_put - 1
            step = fsli.step
            length = stop - start
            assert length <= self.arr.shape[0], 'already overwrite'
            start = self.fid2index(start)
            stop = start + length
            if stop > self.arr.shape[0]:
                stop -= self.arr.shape[0]
                c1 = self.arr[tuple([slice(start, None, step)]+oindex)]
                c2 = self.arr[tuple([slice(None, stop, step)]+oindex)]
                return np.concatenate((c1, c2))
        else:
            raise TypeError('unsupported type')
        oindex.insert(0, fsli)
        return self.arr[tuple(oindex)]

    def add_head(self):
        head = ArrBufHeadGet(self, self.groups[-1])
        self.get_heads.append(head)


class PyQtArrayBuffer(ArrayBuffer2, QObject):
    new_data = pyqtSignal(np.ndarray)

    def __init__(self, *args, **kwargs):
        ArrayBuffer2.__init__(self, *args, **kwargs)
        QObject.__init__(self)

    def put_arr(self, arr):
        super().put_arr(arr)
        self.new_data.emit(arr)
