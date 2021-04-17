import numpy as np


class PrintRandAsFile:
    """
    the class only for test.

    write -> print
    read -> random bytes, print info
    """
    @staticmethod
    def read(n):
        print(f'Generate {n} random bytes')
        arr = np.random.randint(0, 256, n).astype(np.uint8)
        return bytes(arr)

    @staticmethod
    def write(data):
        print(data)
