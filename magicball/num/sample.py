from itertools import product, combinations
from functools import lru_cache, reduce
from operator import and_, or_
from sympy.sets import Set, Intersection, Union, Complement, EmptySet
from sympy.sets.sets import UniversalSet
from sympy.utilities import lambdify
from magicball.symplus.setplus import AbstractSet


def boolarray(bits):
    if bits >= 0:
        return map(lambda b: b=='1', bin(bits)[:1:-1])
    else:
        return map(lambda b: b=='1', bin(bits)[:2:-1])

def setbit1(bits, index):
    return bits|(1<<index)

def setbit0(bits, index):
    return bits&~(1<<index)

def getbit(bits, index):
    return bits&(1<<index) != 0

def bitmap(func, sample):
    bits = 0
    t = 1
    for elem in sample:
        if func(elem):
            bits |= t
        t <<= 1
    return bits


class Sample:
    def __init__(self, iter_getter):
        self._getter = iter_getter

    def __iter__(self):
        return self._getter()

    @lru_cache(maxsize=128)
    def _get_bits(self, aset):
        if isinstance(aset, AbstractSet):
            f = lambdify(aset.variables, aset.expr)
            if len(aset.variables) == 1:
                return bitmap(f, self)
            else:
                return bitmap(lambda v: f(*v), self)
        else:
            return bitmap(lambda v: v in aset, self)

    def get_bits(self, aset):
        if isinstance(aset, Intersection):
            return reduce(and_, map(self.get_bits, aset.args))
        elif isinstance(aset, Union):
            return reduce(or_, map(self.get_bits, aset.args))
        elif isinstance(aset, Complement):
            return self.get_bits(aset.args[0]) &~ self.get_bits(aset.args[1])
        elif isinstance(aset, EmptySet):
            return 0
        elif isinstance(aset, UniversalSet):
            return -1
        elif isinstance(aset, Set):
            return self._get_bits(aset)
        else:
            raise TypeError

    def is_disjoint(self, aset1, aset2):
        return self.get_bits(aset1) & self.get_bits(aset2) == 0

    def is_subset(self, aset1, aset2):
        return self.get_bits(aset1) &~self.get_bits(aset2) == 0

    def equal(self, aset1, aset2):
        return self.get_bits(aset1) == self.get_bits(aset2)

def cube_sample(length=1, n=50):
    return map(lambda v: (v[0]/n, v[1]/n, v[2]/n),
               product(range(-length*n, length*n+1), repeat=3))


def spsetsimp(sample, aset, ran=-1):
    if isinstance(aset, Intersection):
        args = []
        bits = sample.get_bits(aset) & ran
        for arg in aset.args:
            args_ = set(args) - {arg}
            bits_ = sample.get_bits(Intersection(*args_)) & ran
            if bits_ != bits:
                args.append(arg)
        for i, arg in enumerate(args):
            args_ = set(args) - {arg}
            bits_ = sample.get_bits(Intersection(*args_)) & ran
            args[i] = spsetsimp(sample, arg, bits_)
        return Intersection(*args)
    elif isinstance(aset, Union):
        args = []
        bits = sample.get_bits(aset) & ran
        for arg in aset.args:
            args_ = set(args) - {arg}
            bits_ = sample.get_bits(Union(*args_)) & ran
            if bits_ != bits:
                args.append(arg)
        for i, arg in enumerate(args):
            args_ = set(args) - {arg}
            bits_ = sample.get_bits(Union(*args_)) & ran
            args[i] = spsetsimp(sample, arg, ~bits_)
        return Union(*args)
    elif isinstance(aset, Set):
        if isinstance(aset, (EmptySet, UniversalSet)):
            return aset
        else:
            bits = sample.get_bits(aset) & ran
            if bits == 0:
                return EmptySet()
            elif bits == ran:
                return UniversalSet()
            else:
                return aset
    else:
        raise TypeError('aset is not set: %r' % aset)

