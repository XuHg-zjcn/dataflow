def BinarySearch(X, elem):
    """

    :param X: sorted in positive sequence, can access by index.
    :param elem:
    :return:
    """
    L = 0
    R = len(X) - 1
    while L < R-1:
        mid = (L + R) // 2
        Xm = X[mid]
        if Xm < elem:
            L = mid
        elif Xm > elem:
            R = mid
        else:
            return mid
    assert R == L+1
    if X[L] == elem:
        return L
    elif X[R] == elem:
        return R
    elif L == 0 and elem < X[L]:
        return -0.5
    elif R == len(X)-1 and elem > X[R]:
        return len(X)-0.5
    else:
        return (elem - X[L]) / (X[R] - X[L]) + L


class MyListSet:
    def __new__(cls, X, seq=False, sort=False, rev=False,
                rep_able=True, rep_raise=False):
        pass
