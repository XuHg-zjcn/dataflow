from threading import Condition

import numpy as np


def _unpack_indexes(indexes):
    if isinstance(indexes, tuple):
        return indexes[0], list(indexes[1:])
    else:
        return indexes, []


class ArrayBuffer(np.ndarray):
    """
    head and tail relationship diagram:                               index
          _________        _________        _________        __________ -s0
         |        |       |        |       |        |       |        |
         |        |       |        |       |        |  head_|        |
         |        |  head_|        |       |        |       |////////|
         |________|       |////////|       |________|       |////////|_ 0
    head_|        |       |////////|       |        |       |////////|
         |////////|       |_tail///|  head-|-tail   |       |_tail///|
         |_tail///|       |        |       |        |       |        |
         |________|       |________|       |________|       |________|_ s0

         single area      double area         empty            full
         head < tail     head <0< tail    head == tail    tail = head+s0

    s0 = self.shape[0]
    frames store in buffer = tail - head
    below relationship in always keep if program without error:
        -s0 <= head <= tail < s0

    new data will append to tail
    get data will pop from head
    """
    def __new__(cls, shape, dtype):
        slf = super().__new__(cls, shape, dtype)
        # tail=-1: full, tail=head: empty
        slf.head = 0  # head of data, method `get` will get data from head
        slf.tail = 0  # tail of data, new data will put after tail
        slf.total_put = 0
        slf.keep_last = 0
        slf.cond_get = Condition()
        slf.cond_put = Condition()
        return slf

    def __getitem__(self, item):
        """
        get frames allow double area

           value        self
               ________ -s0
               |      |
           0  _|      |_ item[0].start
        l1     |//////|     sli1
           cut_|//////|_ 0
        l2     |//////|     sli2
           v0 _|//////|_ item[0].stop
               |      |
               |______|_ s0

        v0 = value.shape[0]

        |start| stop|
        |  <0 |  =0 | only area l1
        |  <0 |  >0 | area l1 and l2
        |  <0 | None| equiv to stop=0
        | >=0 |   x | only area l2
        --------------
        :param item: slice
        :return: frames of slice
        """
        fsli, oindex = _unpack_indexes(item)
        if isinstance(fsli, slice):
            if isinstance(fsli.start, int) and fsli.start < 0:
                if not isinstance(fsli.stop, int):
                    pass
                elif fsli.stop == 0:
                    fsli = slice(fsli.start, None, fsli.step)
                elif fsli.stop > 0:
                    sli1 = slice(fsli.start, None, fsli.step)  # -fsli.start elems
                    sli2 = slice(None, fsli.stop, fsli.step)   # fsli.stop elems
                    l1 = super().__getitem__(tuple([sli1]+oindex))
                    l2 = super().__getitem__(tuple([sli2]+oindex))
                    return np.concatenate((l1, l2))
        elif isinstance(fsli, int):
            pass
        else:
            raise TypeError('unsupported type first index')
        oindex.insert(0, fsli)
        return super().__getitem__(tuple(oindex))

    def __setitem__(self, key, value):
        fsli, oindex = _unpack_indexes(key)
        if isinstance(fsli, slice):
            if isinstance(fsli.start, int) and fsli.start < 0:
                if not isinstance(fsli.stop, int):
                    pass
                elif fsli.stop == 0:
                    fsli = slice(fsli.start, None, fsli.step)
                elif fsli.stop > 0:
                    assert (fsli.stop - fsli.start)//(fsli.step or 1) == value.shape[0]
                    sli1 = slice(fsli.start, None, fsli.step)  # -fsli.start elems
                    sli2 = slice(None, fsli.stop, fsli.step)   # fsli.stop elems
                    cut = -fsli.start
                    l1 = value[:cut]
                    l2 = value[cut:]
                    super().__setitem__(tuple([sli1]+oindex), l1)
                    super().__setitem__(tuple([sli2]+oindex), l2)
        elif isinstance(fsli, int):
            pass
        else:
            raise TypeError('unsupported type first index')
        oindex.insert(0, fsli)
        return super().__setitem__(tuple(oindex), value)

    def frames(self):
        """
        :return: number of frames store in buffer, not include keep_last
        """
        return self.tail - self.head - self.keep_last

    def free_space(self):
        """
        :return: number of frames can put into buffer
        """
        return self.shape[0] - (self.tail - self.head)

    def put_bytes(self, data: bytes):
        tmp = np.frombuffer(data, dtype=self.dtype)
        tmp = tmp.reshape([-1] + list(self.shape[1:]))
        self.put_arr(tmp)

    def put_arr(self, arr, blocking=True, timeout=None):
        """
        put frame(s) into buffer
        if buffer space not enough to put all frames once,
        blocking=True, will want `get_frames` multiple,
        blocking=False, will raise Error.

        :param arr: array like object
        :param blocking: bool
        :param timeout:
        """
        arr = np.array(arr)  # convert to numpy array
        if arr.ndim == self.ndim-1:
            arr = arr[np.newaxis, ...]
        if self.ndim > 1:    # check shape
            assert self.shape[1:] == arr.shape[-(self.ndim-1):],\
                   (f'put array shape{arr.shape} last {self.ndim-1} dims'
                    f'must same to frame shape{self.shape[1:]}')
        if not blocking and arr.shape[0] > self.free_space():
            raise BufferError('buffer space not enough, you can use blocking put multiply times')
        self.cond_put.acquire()
        self.cond_get.acquire()
        while True:
            # calc how many frames can put into buffer
            tail2 = min(self.head+self.shape[0], self.tail+arr.shape[0])
            frames = tail2 - self.tail
            if tail2 >= self.shape[0]:  # shift head, tail
                self.head -= self.shape[0]  # s0 <= tail2 <= head+s0
                self.tail -= self.shape[0]  # tail >= head
                tail2 -= self.shape[0]
            self[self.tail: tail2] = arr[:frames]  # frames want write to `self.buf_arr`
            arr = arr[frames:]    # clear already write in `tmp`
            self.tail = tail2     # update `tail`
            self.total_put += frames
            self.cond_put.notify()
            if arr.shape[0] == 0:
                break             # all frame already put
            self.cond_get.wait()  # wait has space
        self.cond_put.release()
        self.cond_get.release()

    def get_frames(self, N_frame, blocking=True, timeout=None, copy=False):
        """
        get frames from buffer.

        :param N_frame:
        :param blocking:
        :param timeout:
        :param copy: if True, copy array before return, free space now,
                     if False, don't copy array, return slice of buffer,
                     release space in call the method next time,
                     after this, data maybe change.
        :return: np.array
        """
        self.head += self.keep_last  # free space in last call the method
        self.keep_last = 0

        if N_frame > self.shape[0]:
            raise BufferError("can't get frames once more than buffer capacity")
        if N_frame > self.frames():
            if not blocking:
                raise BufferError("not enough frames in buffer, you can use blocking want")
            else:
                self.cond_put.acquire()
                while N_frame > self.frames():
                    self.cond_put.wait()
                self.cond_put.release()
        ret = self[self.head: self.head + N_frame]

        if copy:
            ret = ret.copy()
        if copy or ret.base is not self:  # ret already a independent array
            self.head += N_frame    # maybe __getitem__ call np.concatenate
        else:                       # release space in next call the method
            self.keep_last = N_frame
        self.cond_get.acquire()
        self.cond_get.notify()
        self.cond_get.release()
        return ret

    def get_last_frames(self, n):
        return self[self.tail-n: self.tail]

    def reset(self):
        """reset buffer pointer, data will overwrite, but not clear now."""
        self.head = 0
        self.tail = 0

    def print_state(self):
        total_get = self.total_put - self.frames()
        print('numpy array buffer info:')
        print(f'shape={self.shape}, dtype={self.dtype}, {self.nbytes} bytes')
        print(f'total put: {self.total_put}, get: {total_get}')
        print(f'head:{self.head}, tail:{self.tail}')
        print(f'free space:{self.free_space()}, store:{self.frames()}, keep_last:{self.keep_last}')


# test code
if __name__ == "__main__":
    import time
    from threading import Thread

    abuf = ArrayBuffer((10, 4), np.uint8)
    abuf.put_arr([1, 2, 3, 4])
    abuf.put_arr([11, 22, 33, 44])
    abuf.put_arr([10, 20, 30, 40])
    abuf.put_bytes(b'1234abcd')
    print(abuf)
    print(abuf.get_frames(3))  # [[ 1  2  3  4], [11 22 33 44], [10 20 30 40]]
    print(abuf.get_frames(2))  # [[ 49  50  51  52], [ 97  98  99 100]]
    abuf.print_state()
    # fill use free_space and frames
    abuf.put_arr([[1,2,3,4] for i in range(abuf.free_space())])
    print(abuf.get_frames(abuf.frames()))  # will blocking
    abuf.print_state()

    def put10(buf):
        for i in range(10):
            buf.put_arr([i, i+10, i+20, i+30])
            time.sleep(0.5)

    print(abuf.frames())
    thr = Thread(target=put10, args=(abuf,))
    thr.start()
    time.sleep(1)
    print(abuf.frames())

    while True:
        print(abuf.get_frames(1))
