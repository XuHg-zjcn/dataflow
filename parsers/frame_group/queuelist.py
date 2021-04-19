class QueueList(list):
    """
    pop item keep index.

    ['o', slice], ['o', int] will use original index
    """
    def __init__(self):
        super().__init__()
        self._total_pops = 0

    @property
    def total_pops(self):
        return self._total_pops

    @property
    def total_puts(self):
        return self._total_pops + len(self)

    def pop(self, index=0):
        """

        :param index: don't change value.
        :return: pop at 0
        """
        self._total_pops += 1
        return super().pop(index)

    def _slice_convert(self, sli):
        if isinstance(sli, int):
            if sli >= 0:
                sli -= self._total_pops
            return sli
        elif isinstance(sli, slice):
            start = sli.start
            stop = sli.stop
            if start is not None and start >= 0:
                start -= self._total_pops
            if stop is not None and stop >= 0:
                stop -= self._total_pops
            return slice(start, stop, sli.step)
        elif isinstance(sli, tuple) and len(sli) == 2 and sli[0] == 'o':
            return sli[1]
        else:
            raise TypeError(f'unsupported indices type: {type(sli)}')

    def __getitem__(self, item):
        return super().__getitem__(self._slice_convert(item))

    def __setitem__(self, key, value):
        return super().__setitem__(self._slice_convert(key), value)
