from sympy.core import Basic, Lambda, Tuple, sympify
from sympy.functions import Piecewise
from sympy.sets import Set, FiniteSet, ProductSet, Interval
from magicball.symplus.util import *


class FreeMonoid(Set):
    """
    >>> from sympy import *
    >>> fmnd1 = FreeMonoid(FiniteSet('a', 'b', 'c')); fmnd1
    FreeMonoid({a, b, c})
    >>> Tuple(*'aabc') in fmnd1
    True
    >>> fmnd2 = FreeMonoid(FiniteSet('x', 'y', 'z'))
    >>> fmnd12 = fmnd1 * fmnd2; fmnd12
    FreeMonoid({a, b, c} x {x, y, z})
    >>> Tuple(('a', 'x'), ('c', 'x'), ('c', 'y')) in fmnd12
    True
    >>> Tuple(*zip('aac','zxy')) in fmnd12
    True
    """
    def __new__(cls, alphabet):
        if not isinstance(alphabet, Set):
            raise TypeError('alphabet is not a Set: %r' % alphabet)
        return Set.__new__(cls, alphabet)

    @property
    def alphabet(self):
        return self.args[0]

    def _contains(self, word):
        if not isinstance(word, Tuple):
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
    """
    >>> from sympy import *
    >>> t = Symbol('t', positive=True)
    >>> pmnd1 = PathMonoid(S.Reals); pmnd1
    PathMonoid((-oo, oo))
    >>> Path(t**2+1, 10) in pmnd1
    True
    >>> Path(t*I+1, 10) in pmnd1
    False
    >>> Path(exp(t), 4.3) in PathMonoid(Interval(0, 100))
    True
    >>> pmnd2 = pmnd1**2; pmnd2
    PathMonoid((-oo, oo) x (-oo, oo))
    >>> Path(t**2+1, 10)*Path(exp(t), 10) in pmnd2
    True
    """
    def __new__(cls, base):
        if not isinstance(base, Set):
            raise TypeError('base is not a Set: %r' % base)
        return Set.__new__(cls, base)

    @property
    def base(self):
        return self.args[0]

    def _contains(self, pth):
        if not isinstance(pth, Path):
            return False
        res = self.base.contains(pth.function.expr)
        if res in (True, False):
            return res
        return all(pth(t) in self.base for t in range(int(pth.length)+1))

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
    """
    >>> from sympy import *
    >>> t = Symbol('t', positive=True)
    >>> pth1 = Path(Lambda(t, t**2+1), 10); pth1
    Path(Lambda(t, t**2 + 1), 10)
    >>> pth2 = Path(exp(t), 10); pth2
    Path(Lambda(t, exp(t)), 10)
    >>> pth1(2)
    5
    >>> len(pth1)
    10
    >>> pth1+pth2
    Path(Lambda(t, Piecewise((t**2 + 1, t <= 10), (101*exp(t - 10), True))), 20)
    >>> pth2[2:5]
    Path(Lambda(t, exp(-2)*exp(t + 2)), 3)
    >>> pth12 = pth1 * pth2; pth12
    TensorPath(Path(Lambda(t, t**2 + 1), 10), Path(Lambda(t, exp(t)), 10))
    >>> pth12.function
    Lambda(t, (t**2 + 1, exp(t)))
    >>> pth12.length
    10
    >>> (pth12 + pth12).function.expr
    (Piecewise((t**2 + 1, t <= 10), (101*(t - 10)**2 + 101, True)), \
Piecewise((exp(t), t <= 10), (exp(10)*exp(t - 10), True)))
    >>> pth12[2:7]
    TensorPath(Path(Lambda(t, (t + 2)**2/5 + 1/5), 5), \
Path(Lambda(t, exp(-2)*exp(t + 2)), 5))
    """
    def __new__(cls, func, flen):
        if not isinstance(func, Lambda):
            if len(func.free_symbols) != 1:
                raise TypeError('func is not a one variable expression: %r' % func)
            t = tuple(func.free_symbols)[0]
            func = Lambda(t, func)
        else:
            if len(func.variables) > 1 or len(func.free_symbols) != 0:
                raise TypeError('func is not a one variable Lambda: %r' % func)
        if flen < 0:
            raise ValueError('flen must be positive: %s' % flen)
        return Basic.__new__(cls, func, flen)

    @property
    def function(self):
        return self.args[0]

    @property
    def length(self):
        return self.args[1]

    def concat(self, other):
        if not isinstance(other, Path):
            raise ValueError('other is not a Path: %s' % other)
        t = self.function.variables[0]
        l = self.length
        expr12 = Piecewise((self.function(t), t<=l),
                           (other.function(t-l)*self.function(l), True))
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
        return Basic.__new__(cls, *paths)

    @property
    def function(self):
        t = self.args[0].function.variables[0]
        return Lambda(t, tuple(pth.function(t) for pth in self.args))

    @property
    def length(self):
        return self.args[0].length

    def concat(self, other):
        if (not isinstance(other, TensorPath) or
            len(self.args) != len(self.args)):
            raise ValueError
        return TensorPath(*[pth1.concat(pth2)
                            for pth1, pth2 in zip(self.args, other.args)])

    def slice(self, start, stop):
        return TensorPath(*[pth.slice(start, stop) for pth in self.args])

