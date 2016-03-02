import math
from copy import deepcopy

# http://www.siafoo.net/article/57
# http://math.ucr.edu/home/baez/octonions/node5.html

class Construction(object):

    @classmethod
    def construct(cls, order=4):
        log_2 = math.log(order, 2)
        if log_2 < 1 or int(log_2) != log_2:
            raise ValueError("'order' must two or higher and a power of two.")

        if order == 2:
            return Complex()
        else:
            return Construction(Construction.construct(order/2),
                                Construction.construct(order/2))

    def __init__(self, a, b):
        if not isinstance(a, Construction) or not isinstance(b, Construction):
            raise ValueError("'a' and 'b' must both be Construction class instances.")
        if a.order != b.order:
            raise ValueError("'a' and 'b' parameters must both have the same order.")
        self.order = a.order * 2
        self.a = a
        self.b = b

    def c(self):
        """
        conjugate
        """
        clone = deepcopy(self)
        return clone._in_place_c()

    def _c(self):
        self.a = self.a._c()
        self.b = -(self.b)

    def _index_check(self, key):
        if int(key) != key:
            raise ValueError("Bad index: {}".format(key))
        if 0 > key >= order:
            raise ValueError("Index must be an integer from zero to {}".format(self.order))

    def __getitem__(self, key):
        self._index_check(key)
        new_idx = key % (order / 2)
        if key < order / 2:
            return self.a[new_idx]
        else:
            return self.b[new_idx]

    def __setitem__(self, key, value):
        self._index_check(key)
        new_idx = key % (order / 2)
        if key < order / 2:
            self.a[new_idx] = value
        else:
            self.b[new_idx] = value

    def __mul__(self, other):
        clone = deepcopy(self)
        # (a, b)(c, d) = (ac - db*, a*d + cb)
        # this is (a, b)
        clone.a = self.a * other.a - other.b * self.b.c()
        clone.b = self.a.c() * other.b + other.a * self.b
        return clone

    def __add__(self, other):
        clone = deepcopy(self)
        clone.a = self.a + other.a
        clone.b = self.b + other.b
        return clone

    def __sub__(self, other):
        clone = deepcopy(self)
        clone.a = self.a - other.a
        clone.b = self.b - other.b
        return clone

class Complex(Construction):

    def __init__(self, a=0, b=0):
        self.a = float(a)
        self.b = float(b)
        self.order = 2

    def _c(self):
        self.b = -(self.a)

    def __getitem__(self, key):
        self._index_check(key)
        if key == 0:
            return self.a
        elif key == 1:
            return self.b

    def __setitem__(self, key, value):
        self._index_check(key)
        if key == 0:
            self.a = float(value)
        elif key == 1:
            return self.b = float(value)

    def __mul__(self, other):
        clone = deepcopy(self)
        # (a, b)(c, d) = (ac - db, ad + cb)
        # this is (a, b)
        clone.a = self.a * other.a - other.b * self.b
        clone.b = self.a * other.b + other.a * self.b
        return clone
