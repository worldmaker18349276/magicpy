from sympy.core import Basic, Lambda, Tuple, sympify, Dummy
from sympy.functions import Piecewise
from sympy.sets import Set, FiniteSet, ProductSet, Interval
from symplus.util import *
from symplus.funcplus import Functor, compose, inverse


class Word(Tuple):
    def __getitem__(self, i):
        if isinstance(i, slice):
            indices = i.indices(len(self))
            return self.func(*[self.args[j] for j in range(*indices)])
        return self.args[i]

    def __add__(self, other):
        if isinstance(other, Tuple):
            return self.func(*(self.args + other.args))
        elif isinstance(other, tuple):
            return self.func(*(self.args + other))
        else:
            return NotImplemented

    def __radd__(self, other):
        if isinstance(other, Tuple):
            return self.func(*(other.args + self.args))
        elif isinstance(other, tuple):
            return self.func(*(other + self.args))
        else:
            return NotImplemented

    def __mul__(self, other):
        if isinstance(other, Tuple):
            return self.func(*zip(self.args, other.args))
        elif isinstance(other, tuple):
            return self.func(*zip(self.args, other))
        else:
            return NotImplemented

    def __rmul__(self, other):
        if isinstance(other, Tuple):
            return self.func(*zip(other.args, self.args))
        elif isinstance(other, tuple):
            return self.func(*zip(other, self.args))
        else:
            return NotImplemented

class FreeMonoid(Set):
    """
    >>> from sympy import *
    >>> fmnd1 = FreeMonoid({'a', 'b', 'c'}); fmnd1
    FreeMonoid({a, b, c})
    >>> Word(*'aabc') in fmnd1
    True
    >>> fmnd2 = FreeMonoid({'x', 'y', 'z'})
    >>> fmnd12 = fmnd1 * fmnd2; fmnd12
    FreeMonoid({a, b, c} x {x, y, z})
    >>> Word(('a', 'x'), ('c', 'x'), ('c', 'y')) in fmnd12
    True
    >>> Word(*'aac') * Word(*'zxy') in fmnd12
    True
    """
    def __new__(cls, alphabet):
        if isinstance(alphabet, set):
            alphabet = FiniteSet(*alphabet)
        if not isinstance(alphabet, Set):
            raise TypeError('alphabet is not a Set: %r' % alphabet)
        return Set.__new__(cls, alphabet)

    @property
    def alphabet(self):
        return self.args[0]

    def _contains(self, word):
        if not isinstance(word, Word):
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


class Path(Functor):
    def __new__(cls, flen, *args):
        if flen < 0:
            raise ValueError('flen must be positive: %s' % flen)
        return Functor.__new__(cls, flen, *args)

    narg = 1
    nres = 1

    @property
    def length(self):
        return self.args[0]

    @staticmethod
    def tensor(pths):
        return TensorPath(*pths)

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

class TensorPath(Path):
    def __new__(cls, *paths):
        if any(not isinstance(pth, Path) for pth in paths):
            raise TypeError
        if len(set(pth.length for pth in paths)) != 1:
            raise ValueError
        return Functor.__new__(cls, *paths)

    @property
    def nres(self):
        return len(self.paths)

    @property
    def paths(self):
        return self.args

    @property
    def length(self):
        return self.args[0].length

    def as_lambda(self):
        t = Dummy('t')
        return Lambda(t, tuple(pth(t) for pth in self.paths))

    def concat(self, other):
        if not isinstance(other, TensorPath) or len(self.paths) != len(self.paths):
            raise ValueError
        return TensorPath(*[pth1.concat(pth2)
                            for pth1, pth2 in zip(self.paths, other.paths)])

    def slice(self, start, stop):
        return TensorPath(*[pth.slice(start, stop) for pth in self.paths])

class LambdaPath(Path):
    def __new__(cls, flen, variable, expr):
        if flen < 0:
            raise ValueError('flen must be positive: %s' % flen)
        if not is_Symbol(variable):
            raise TypeError('variable is not a Symbol or MatrixSymbol: %r' % variable)
        return Path.__new__(cls, flen, variable, expr)

    @property
    def variable(self):
        return self.args[1]

    @property
    def expr(self):
        return self.args[2]

    def as_lambda(self):
        return Lambda(self.variable, self.expr)

    def call(self, t=None):
        t = t if t is not None else self.length
        if free_symbols(t) == set() and t not in Interval(0, self.length):
            raise ValueError
        return self.as_lambda()(t)

    def concat(self, other):
        if not isinstance(other, type(self)):
            raise ValueError('other is not a %s: %s' % (type(self), other))
        t = self.variable
        l = self.length
        expr12 = Piecewise((self(t), t<=l),
                           (self.base_compose(other(t-l), self(l)), True))
        return self.func(self.length+other.length, t, expr12)

    def slice(self, start, stop):
        stop = stop if stop is not None else self.length
        start = start if start is not None else 0
        if (stop not in Interval(0, self.length) or
            start not in Interval(0, self.length) or
            stop < start):
            raise IndexError
        if start == 0:
            return self.func(self.variable, self.expr, stop)
        else:
            t = self.variable
            expr = self.base_decompose(self(start+t), self(start))
            return self.func(stop-start, t, expr)

class MultiplicativePath(LambdaPath):
    """
    >>> from sympy import *
    >>> t = Symbol('t', positive=True)
    >>> pth1 = MultiplicativePath(10, t, t**2+1); pth1
    MultiplicativePath(10, t, t**2 + 1)
    >>> pth2 = MultiplicativePath(10, t, exp(t)); pth2
    MultiplicativePath(10, t, exp(t))
    >>> pth1(2)
    5
    >>> len(pth1)
    10
    >>> pth1+pth2
    MultiplicativePath(20, t, Piecewise((t**2 + 1, t <= 10), (101*exp(t - 10), True)))
    >>> pth2[2:5]
    MultiplicativePath(3, t, exp(-2)*exp(t + 2))
    >>> pth12 = pth1 * pth2; pth12
    TensorPath(MultiplicativePath(10, t, t**2 + 1), MultiplicativePath(10, t, exp(t)))
    >>> pth12.as_lambda()
    Lambda(_t, (_t**2 + 1, exp(_t)))
    >>> pth12.length
    10
    >>> (pth12 + pth12).as_lambda().expr
    (Piecewise((_t**2 + 1, _t <= 10), (101*(_t - 10)**2 + 101, True)), Piecewise((exp(_t), _t <= 10), (exp(10)*exp(_t - 10), True)))
    >>> pth12[2:7]
    TensorPath(MultiplicativePath(5, t, (t + 2)**2/5 + 1/5), MultiplicativePath(5, t, exp(-2)*exp(t + 2)))
    """
    @staticmethod
    def base_compose(self, other):
        return self * other

    @staticmethod
    def base_decompose(self, other):
        if is_Matrix(other):
            return self * other.inv()
        else:
            return self / other

class AdditivePath(LambdaPath):
    """
    >>> from sympy import *
    >>> t = Symbol('t', positive=True)
    >>> pth1 = AdditivePath(10, t, t**2+1); pth1
    AdditivePath(10, t, t**2 + 1)
    >>> pth2 = AdditivePath(10, t, exp(t)); pth2
    AdditivePath(10, t, exp(t))
    >>> pth1(2)
    5
    >>> len(pth1)
    10
    >>> pth1+pth2
    AdditivePath(20, t, Piecewise((t**2 + 1, t <= 10), (exp(t - 10) + 101, True)))
    >>> pth2[2:5]
    AdditivePath(3, t, exp(t + 2) - exp(2))
    >>> pth12 = pth1 * pth2; pth12
    TensorPath(AdditivePath(10, t, t**2 + 1), AdditivePath(10, t, exp(t)))
    >>> pth12.as_lambda()
    Lambda(_t, (_t**2 + 1, exp(_t)))
    >>> pth12.length
    10
    >>> (pth12 + pth12).as_lambda().expr
    (Piecewise((_t**2 + 1, _t <= 10), ((_t - 10)**2 + 102, True)), Piecewise((exp(_t), _t <= 10), (exp(_t - 10) + exp(10), True)))
    >>> pth12[2:7]
    TensorPath(AdditivePath(5, t, (t + 2)**2 - 4), AdditivePath(5, t, exp(t + 2) - exp(2)))
    """
    @staticmethod
    def base_compose(self, other):
        return self + other

    @staticmethod
    def base_decompose(self, other):
        return self - other

class TransformationPath(LambdaPath):
    """
    >>> from sympy import *
    >>> t = Symbol('t', positive=True)
    >>> x = Symbol('x')
    >>> pth1 = TransformationPath(10, t, Lambda(x, t*x)); pth1
    TransformationPath(10, t, Lambda(x, t*x))
    >>> pth2 = TransformationPath(10, t, Lambda(x, t+x)); pth2
    TransformationPath(10, t, Lambda(x, t + x))
    >>> pth1(2)
    Lambda(x, 2*x)
    >>> len(pth1)
    10
    >>> pth1+pth2
    TransformationPath(20, t, Piecewise((Lambda(x, t*x), t <= 10), (Lambda(x, t + 10*x - 10), True)))
    >>> pth2[2:5]
    TransformationPath(3, t, FunctionCompose(Lambda(x, t + x + 2), FunctionInverse(Lambda(x, x + 2))))
    >>> pth12 = pth1 * pth2; pth12
    TensorPath(TransformationPath(10, t, Lambda(x, t*x)), TransformationPath(10, t, Lambda(x, t + x)))
    >>> pth12.as_lambda()
    Lambda(_t, (Lambda(x, _t*x), Lambda(x, _t + x)))
    >>> pth12.length
    10
    >>> (pth12 + pth12).as_lambda().expr
    (Piecewise((Lambda(x, _t*x), _t <= 10), (Lambda(x, 10*x*(_t - 10)), True)), Lambda(x, _t + x))
    >>> pth12[2:7]
    TensorPath(TransformationPath(5, t, FunctionCompose(Lambda(x, x*(t + 2)), FunctionInverse(Lambda(x, 2*x)))), TransformationPath(5, t, FunctionCompose(Lambda(x, t + x + 2), FunctionInverse(Lambda(x, x + 2)))))
    """
    @staticmethod
    def base_compose(self, other):
        return compose(self, other)

    @staticmethod
    def base_decompose(self, other):
        return compose(self, inverse(other))

# class PathMonoid(Set):
#     """
#     >>> from sympy import *
#     >>> t = Symbol('t', positive=True)
#     >>> pmnd1 = PathMonoid(S.Reals); pmnd1
#     PathMonoid((-oo, oo))
#     >>> Path(t**2+1, 10) in pmnd1
#     True
#     >>> Path(t*I+1, 10) in pmnd1
#     False
#     >>> Path(exp(t), 4.3) in PathMonoid(Interval(0, 100))
#     True
#     >>> pmnd2 = pmnd1**2; pmnd2
#     PathMonoid((-oo, oo) x (-oo, oo))
#     >>> Path(t**2+1, 10)*Path(exp(t), 10) in pmnd2
#     True
#     """
#     def __new__(cls, base):
#         if not isinstance(base, Set):
#             raise TypeError('base is not a Set: %r' % base)
#         return Set.__new__(cls, base)

#     @property
#     def base(self):
#         return self.args[0]

#     def _contains(self, pth):
#         if not isinstance(pth, Path):
#             return False
#         res = self.base.contains(pth.function.expr)
#         if res in (True, False):
#             return res
#         return all(pth(t) in self.base for t in range(int(pth.length)+1))

#     def __mul__(self, other):
#         return PathMonoid.tensor((self, other))

#     def __pow__(self, n):
#         return PathMonoid.tensor((self,)*n)

#     @staticmethod
#     def tensor(pmnds):
#         pmnds = tuple(pmnds)
#         if any(not isinstance(pmnd, PathMonoid) for pmnd in pmnds):
#             return ProductSet(pmnds)
#         return PathMonoid(ProductSet(*[pmnd.base for pmnd in pmnds]))

