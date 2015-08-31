from sympy.core import Basic, Lambda
from sympy.functions import Piecewise
from sympy.sets import Set, FiniteSet, ProductSet, Interval
from magicball.symplus.util import *


class FreeMonoid(Set):
    def __new__(cls, alphabet):
        if not isinstance(alphabet, FiniteSet):
            raise TypeError
        return Set.__new__(cls, alphabet)

    @property
    def alphabet(self):
        return self.args[0]

    def _contains(self, word):
        if not isinstance(word, list):
            return False
        return all(word[t] in self.alphabet for t in range(len(word)))

    def __mul__(self, other):
        return FreeMonoid.tensor((self, other))

    def __pow__(self, n):
        return FreeMonoid.tensor((self,)*n)

    @staticmethod
    def tensor(fmnds):
        fmnds = tuple(fmnds)
        if any(not isinstance(fmnd, FreeMonoid) for fmnd in fmnds):
            return ProductSet(*fmnds)
        return FreeMonoid(ProductSet(*[fmnd.alphabet for fmnd in fmnds]))

class PathMonoid(Set):
    def __init__(self, base):
        if not isinstance(base, Set):
            raise TypeError
        return Set.__new__(cls, base)

    @property
    def base(self):
        return self.args[0]

    def _contains(self, pth):
        if not isinstance(pth, Path):
            return False
        if pth.function.expr in self.base:
            return True
        return None
        # return all(pth(t) in self.base for t in range(int(pth.length)+1))

    def __mul__(self, other):
        return PathMonoid.tensor((self, other))

    def __pow__(self, n):
        return PathMonoid.tensor((self,)*n)

    @staticmethod
    def tensor(pmnds):
        pmnds = tuple(pmnds)
        if any(not isinstance(pmnd, PathMonoid) for pmnd in pmnds):
            return ProductSet(pmnds)
        return PathMonoid(ProductSet(*[pmnd.base for pmnd in pmnds]))

class Path(Basic):
    def __new__(cls, func, flen):
        if (not isinstance(func, Lambda) or
            len(func.variables) > 1 or
            func.free_symbols != set()):
            raise TypeError
        if flen < 0:
            raise TypeError
        return Basic.__new__(cls, func, flen)

    @property
    def function(self):
        return self.args[0]

    @property
    def length(self):
        return self.args[1]

    def concat(self, other):
        if not isinstance(other, Path):
            raise ValueError
        t = self.function.variables[0]
        expr12 = Piecewise((self.function(t), t<=self.length),
                           (other.function(t), True))
        return Path(Lambda(t, expr12), self.length+other.length)

    def slice(self, start, stop):
        stop = stop if stop is not None else self.length
        start = start if start is not None else 0
        if (stop not in Interval(0, self.length) or
            start not in Interval(0, self.length) or
            stop < start):
            raise IndexError
        if start == 0:
            return Path(self.function, stop)
        else:
            t = self.function.variables[0]
            if is_Matrix(self.function.expr):
                expr = self.function(start+t)*self.function(start).inv()
            else:
                expr = self.function(start+t)/self.function(start)
            return Path(Lambda(t, expr), stop-start)

    def __call__(self, t):
        if t not in Interval(0, self.length):
            raise ValueError
        return self.function(t)

    def __len__(self):
        return self.length

    def __add__(self, other):
        return self.concat(other)

    def __getitem__(self, key):
        if not isinstance(key, slice):
            raise TypeError
        return self.slice(key.start, key.stop)

    def __mul__(self, other):
        return Path.tensor((self, other))

    def __pow__(self, n):
        return Path.tensor((self,)*n)

    @staticmethod
    def tensor(pths):
        return TensorPath(*pths)

class TensorPath(Path):
    def __new__(cls, *paths):
        if any(not isinstance(pth, Path) for pth in paths):
            raise TypeError
        if len(set(pth.length for pth in paths)) != 1:
            raise ValueError
        obj = Basic.__new__(cls, *paths)
        t = paths[0].function.variables[0]
        obj.function = Lambda(t, tuple(map(pth.function(t) for pth in paths)))
        obj.length = paths[0].length
        return obj

    def concat(self, other):
        if (not isinstance(other, TensorPath) or
            len(self.args) != len(self.args)):
            raise ValueError
        return TensorPath(*[pth1.concat(pth2)
                            for pth1, pth2 in zip(self.args, other.args)])

    def slice(self, start, stop):
        return TensorPath(*[pth.slice(start, stop) for pth in self.args])

