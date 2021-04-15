class MyOrderedDict:
    def __init__(self, keys: list, values: list):
        assert len(keys) == len(values), 'number of keys and values not equal'
        assert len(keys) == len(set(keys)), 'has repeated in keys'
        self.keys = keys
        self.values = values

    # can't keep sorted if operate after create.
    @staticmethod
    def fromSortedKeys(d, *args, **kwargs):
        keys = sorted(d.keys(), *args, **kwargs)
        values = [d[k] for k in keys]
        return MyOrderedDict(keys, values)

    @staticmethod
    def fromSortedValues(d, *args, **kwargs):
        values = sorted(d.values(), *args, **kwargs)
        d_inv = {v: k for k, v in d.items()}
        keys = [d_inv[v] for v in values]
        return MyOrderedDict(keys, values)

    def v2k(self, value):
        i = self.values.index(value)
        return self.keys[i]

    def k2v(self, key):
        i = self.keys.index(key)
        return self.values[i]

    def v2i(self, value):
        return self.values.index(value)

    def k2i(self, key):
        return self.keys.index(key)

    def get(self, key, default=None):
        if key in self.keys:
            return self.k2v(key)
        else:
            return default

    def __contains__(self, key):
        return self.keys.__contains__(key)

    def __setitem__(self, key, value):
        if key in self.keys:
            i = self.keys.index(key)
            self.keys[i] = value
        else:
            self.keys.append(key)
            self.values.append(value)

    def __getitem__(self, item):
        return self.k2v(item)

    def __eq__(self, other):
        return self.keys == other.keys and self.values == other.values

    def __len__(self):
        assert len(self.values) == len(self.keys)
        return len(self.values)

    def pop(self, k, d=None):
        if k in self.keys:
            i = self.keys.index(k)
            self.keys.pop(i)
            return self.values.pop(i)
        elif d is not None:
            return d
        else:
            raise KeyError(k)

    def popitem(self):
        k = self.keys.pop()
        v = self.values.pop()
        return k, v

    def update(self):
        raise NotImplementedError

    def setdefault(self, key, default=None):
        if key not in self:
            self[key] = default

    def copy(self):
        return MyOrderedDict(self.keys.copy(), self.values.copy())

    def swap_kv(self):
        vs = set()
        for i, v in enumerate(self.values):
            if v in vs:
                i0 = self.values.index(v)
                raise ValueError("can't swap keys and values, because values has repeat, "
                                 f"one is v[{i0}]=v[{i}]={v}")
        self.keys, self.values = self.values, self.keys
