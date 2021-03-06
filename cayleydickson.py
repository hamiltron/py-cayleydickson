import math
from copy import deepcopy

# http://www.siafoo.net/article/57
# http://math.ucr.edu/home/baez/octonions/node5.html

class Construction(object):

    @classmethod
    def construct(cls, order):
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
        clone.a = self.a.c()
        clone.b = -(self.b)
        return clone

    def mag(self):
        return math.sqrt(self.norm())

    def scale(self, scale):
        clone = deepcopy(self)
        for idx in range(self.order):
            clone[idx] *= scale
        return clone

    def norm(self):
        norm_sum = 0
        for idx in range(self.order):
            norm_sum += self[idx] ** 2
        return norm_sum

    def inv(self):
        return self.c().scale(1.0 / self.norm())

    def rot(self, other):
        return other * self * other.inv()

    def _index_check(self, key):
        if int(key) != key:
            raise ValueError("Bad index: {}".format(key))
        if 0 > key >= order:
            raise ValueError("Index must be an integer from zero to {}".format(self.order))

    def __getitem__(self, key):
        self._index_check(key)
        new_idx = key % (self.order / 2)
        if key < self.order / 2:
            return self.a[new_idx]
        else:
            return self.b[new_idx]

    def __setitem__(self, key, value):
        self._index_check(key)
        new_idx = key % (self.order / 2)
        if key < self.order / 2:
            self.a[new_idx] = value
        else:
            self.b[new_idx] = value

    def __mul__(self, other):
        clone = deepcopy(self)
        # (a, b)(c, d) = (ac - d*b, da + bc*)
        # this is (a, b)
        clone.a = self.a * other.a - other.b.c() * self.b
        clone.b = other.b * self.a + self.b * other.a.c()
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

    def __neg__(self):
        clone = deepcopy(self)
        clone.a = -(self.a)
        clone.b = -(self.b)
        return clone

    def __eq__(self, other):
        return self.a == other.a and self.b == other.b

    def __ne__(self, other):
        return not self == other

    def __repr__(self):
        return "({}, {})".format(str(self.a), str(self.b))


class Complex(Construction):

    def __init__(self, a=0, b=0):
        self.a = float(a)
        self.b = float(b)
        self.order = 2

    def c(self):
        clone = deepcopy(self)
        clone.b = -(self.b)
        return clone

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
            self.b = float(value)

    def __mul__(self, other):
        clone = deepcopy(self)
        # (a, b)(c, d) = (ac - db, ad + cb)
        # this is (a, b)
        clone.a = self.a * other.a - other.b * self.b
        clone.b = self.a * other.b + other.a * self.b
        return clone

    def __repr__(self):
        return "({:.3f}, {:.3f})".format(self.a, self.b)


def Quaternion():
    return Construction.construct(4)


def Octonian():
    return Construction.construct(8)


def q_vector(x, y, z):
    q = Quaternion()
    q[1] = x
    q[2] = y
    q[3] = z
    return q


def q_rotation(angle, x, y, z):
    vec_mag = math.sqrt(x ** 2 + y ** 2 + z ** 2)
    q = Quaternion()
    half_angle = angle / 2.0
    vector_scale = math.sin(half_angle)
    q[0] = math.cos(half_angle)
    q[1] = x * vector_scale / vec_mag
    q[2] = y * vector_scale / vec_mag
    q[3] = z * vector_scale / vec_mag
    return q


def q_rotation_between(q1, q2):
    if (q1.order != 4 or q2.order != 4):
        raise ValueError("Both parameters must be quaternions")
    q1[0] = 0
    q2[0] = 0
    dot = q1[1] * q2[1] + q1[2] * q2[2] + q1[3] * q2[3]
    angle = math.acos(dot / q1.mag() / q2.mag())
    x = q1[2] * q2[3] - q1[3] * q2[2]
    y = q1[3] * q2[1] - q1[1] * q2[3]
    z = q1[1] * q2[2] - q1[2] * q2[1]
    # this will handle normalization
    return q_rotation(angle, x, y, z)

# ----------------- testing -------------------------

def compare_mul_table(bases, table):
    order = len(bases)
    for row in range(order):
        for col in range(order):
            val = bases[row] * bases[col]
            exp = expected[row][col]
            try:
                assert val == exp
            except AssertionError as e:
                print("r {} c {} ... {} * {} should be {}, is {}".format(
                        row, col, bases[row], bases[col], exp, val))
                raise

if __name__ == "__main__":
    one = Construction.construct(2)
    one[0] = 1
    unit_i = Construction.construct(2)
    unit_i[1] = 1

    assert one * one == one
    assert one * unit_i == unit_i
    assert unit_i * one == unit_i
    assert unit_i * unit_i == -(one)
    assert -(one) * unit_i == -(unit_i)
    assert (one + unit_i )[0] == 1
    assert (one + unit_i )[1] == 1

    # quaternions
    q = []
    for i in range(4):
        cd = Construction.construct(4)
        cd[i] = 1
        q.append(cd)

    assert (q[0] + q[1])[0] == 1
    assert (q[0] + q[1])[1] == 1
    assert (q[0] + q[1])[2] == 0
    assert (q[0] + q[1])[3] == 0
    assert (q[0] + q[2])[2] == 1
    assert (q[0] + q[3])[3] == 1

    expected = [[q[0], q[1], q[2], q[3]],
                [q[1], -q[0], q[3], -q[2]],
                [q[2], -q[3], -q[0], q[1]],
                [q[3], q[2], -q[1], -q[0]]]

    compare_mul_table(q, expected)

    # octonians
    o = []
    for i in range(8):
        cd = Construction.construct(8)
        cd[i] = 1
        o.append(cd)

    expected = [[o[0], o[1], o[2], o[3], o[4], o[5], o[6], o[7]],
                [o[1], -o[0], o[3], -o[2], o[5], -o[4], -o[7], o[6]],
                [o[2], -o[3], -o[0], o[1], o[6], o[7], -o[4], -o[5]],
                [o[3], o[2], -o[1], -o[0], o[7], -o[6], o[5], -o[4]],
                [o[4], -o[5], -o[6], -o[7], -o[0], o[1], o[2], o[3]],
                [o[5], o[4], -o[7], o[6], -o[1], -o[0], -o[3], o[2]],
                [o[6], o[7], o[4], -o[5], -o[2], o[3], -o[0], -o[1]],
                [o[7], -o[6], o[5], o[4], -o[3], -o[2], o[1], -o[0]]]

    compare_mul_table(o, expected)
