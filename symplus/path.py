from sympy.core import S, Basic, Lambda, Tuple, sympify, Symbol
from sympy.core.compatibility import with_metaclass
from sympy.core.singleton import Singleton
from sympy.core.evaluate import global_evaluate
from sympy.functions import Piecewise
from sympy.sets import Set, FiniteSet, ProductSet, Interval
from symplus.typlus import is_Matrix
from symplus.symbplus import free_symbols, rename_variables_in
from symplus.funcplus import FunctionObject, compose, inverse, nres, narg


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


class Path(Basic):
    def __len__(self):
        return self.length

    def __getitem__(self, key):
        if not isinstance(key, slice):
            raise TypeError
        return SlicedPath(self, key.start, key.stop)

    def __add__(self, other):
        return ConcatenatedPath(self, other)

    def __mul__(self, other):
        return TensorPath(self, other)

    def forget(self, t=None):
        t = t if t is not None else self.length
        if free_symbols(t) == set() and t not in Interval(0, self.length):
            raise ValueError
        return self.slice_lambda()(t)

class IdentityPath(with_metaclass(Singleton, Path)):
    length = S.Zero

    def _sympystr(self, printer):
        return "Id"

    def _mathstr(self, printer):
        return "1^0"

    def slice_lambda(self):
        t = Symbol('t')
        return Lambda(t, t)

class SlicedPath(Path):
    def __new__(cls, path, start, stop, **kwargs):
        evaluate = kwargs.pop('evaluate', global_evaluate[0])

        if not isinstance(path, Path):
            raise TypeError
        stop = sympify(stop) if stop is not None else path.length
        start = sympify(start) if start is not None else S.Zero
        if (stop not in Interval(0, path.length) or
            start not in Interval(0, path.length) or
            stop < start):
            raise IndexError

        if evaluate:
            if start == 0 and stop == path.length:
                sliced_path = path
            elif start == stop:
                sliced_path = IdentityPath()
            else:
                sliced_path = path._slice(start, stop)

        if sliced_path is not None:
            return sliced_path
        else:
            return Basic.__new__(cls, path, start, stop)

    @property
    def path(self):
        return self.args[0]

    @property
    def start(self):
        return self.args[1]

    @property
    def stop(self):
        return self.args[2]

    @property
    def length(self):
        return self.stop - self.start

    def _concat(self, other):
        if (isinstance(other, SlicedPath) and
            self.path == other.path and
            self.stop == other.start):
            return SlicedPath(self.path, self.start, other.stop)

    def _slice(self, start, stop):
        return SlicedPath(self.path, self.start+start, self.start+stop)

    def _sympystr(self, printer):
        return "{0}[{1}:{2}]".format(
            printer._print(self.path),
            printer._print(self.start),
            printer._print(self.stop))

    def _mathstr(self, printer):
        return self._sympystr(printer)

class ConcatenatedPath(Path):
    def __new__(cls, *paths, **kwargs):
        evaluate = kwargs.pop('evaluate', global_evaluate[0])

        if any(not isinstance(pth, Path) for pth in paths):
            raise TypeError

        if evaluate:
            paths = cls.reduce(paths)

        if len(paths) == 0:
            return IdentityPath()
        elif len(paths) == 1:
            return paths[0]
        else:
            return Basic.__new__(cls, *paths)

    @staticmethod
    def reduce(paths):
        i = 0
        while i < len(paths):
            if isinstance(paths[i], IdentityPath):
                paths = paths[:i] + paths[i+1:]
            elif isinstance(paths[i], ConcatenatedPath):
                paths = paths[:i] + paths[i].paths + paths[i+1:]
            elif i-1 >= 0 and hasattr(paths[i-1], '_concat'):
                concat_path = paths[i-1]._concat(paths[i])
                if concat_path is not None:
                    paths = paths[:i-1] + (concat_path,) + paths[i+1:]
                    i = i - 1
            i = i + 1
        return paths

    @property
    def paths(self):
        return self.args

    @property
    def length(self):
        return sum(pth.length for pth in self.paths)

    def _slice(self, start, stop):
        paths = []
        for pth in self.paths:
            if start < 0:
                start_ = 0
            elif start > pth.length:
                start_ = pth.length
            else:
                start_ = start
            if stop < 0:
                stop_ = 0
            elif stop > pth.length:
                stop_ = pth.length
            else:
                stop_ = stop

            paths.append(SlicedPath(pth, start_, stop_))
            start = start - pth.length
            stop = stop - pth.length
        return ConcatenatedPath(*paths)

    def _sympystr(self, printer):
        return " + ".join(map(printer._print, self.paths))

    def _mathstr(self, printer):
        return self._sympystr(printer)

class TensorPath(Path):
    def __new__(cls, *paths, **kwargs):
        evaluate = kwargs.pop('evaluate', global_evaluate[0])

        if any(not isinstance(pth, Path) for pth in paths):
            raise TypeError
        if len(paths) != 0 and len(set(pth.length for pth in paths)) != 1:
            raise ValueError

        if evaluate:
            paths = cls.reduce(paths)

        if len(paths) == 0:
            return IdentityPath()
        elif len(paths) == 1:
            return paths[0]
        else:
            return Basic.__new__(cls, *paths)

    @staticmethod
    def reduce(paths):
        i = 0
        while i < len(paths):
            if isinstance(paths[i], TensorPath):
                paths = paths[:i] + paths[i].paths + paths[i+1:]
            i = i + 1
        return paths

    @property
    def paths(self):
        return self.args

    @property
    def length(self):
        return self.paths[0].length

    def _concat(self, other):
        if isinstance(other, TensorPath):
            paths1 = self.reduce(self.paths)
            paths2 = other.reduce(other.paths)
            return TensorPath(*[ConcatenatedPath(pth1, pth2)
                                for pth1, pth2 in zip(paths1, paths2)])

    def _slice(self, start, stop):
        return TensorPath(*[SlicedPath(pth, start, stop) for pth in self.paths])

    def slice_lambda(self):
        lambdas = tuple(pth.slice_lambda() for pth in self.paths)
        t = lambdas[0].variables
        t = rename_variables_in(t, free_symbols(lambdas))
        return Lambda(t, tuple(f(*t) for f in lambdas))

    def _sympystr(self, printer):
        return " * ".join(map(printer._print, self.paths))

    def _mathstr(self, printer):
        return self._sympystr(printer)

class LambdaPath(Path):
    def __new__(cls, flen, variable, expr):
        flen = sympify(flen)
        if flen < 0:
            raise ValueError('flen must be positive: %s' % flen)
        if not isinstance(variable, Symbol):
            raise TypeError('variable is not a Symbol: %r' % variable)
        return Basic.__new__(cls, flen, variable, expr)

    @property
    def length(self):
        return self.args[0]

    @property
    def variable(self):
        return self.args[1]

    @property
    def expr(self):
        return self.args[2]

    def slice_lambda(self):
        return Lambda(self.variable, self.expr)

    def _concat(self, other):
        if not isinstance(other, type(self)):
            raise ValueError('other is not a %s: %s' % (type(self), other))
        t = self.variable
        l = self.length
        expr12 = Piecewise((self.forget(t), t<=l),
                           (self.base_compose(other.forget(t-l), self.forget(l)), True))
        return self.func(self.length+other.length, t, expr12)

    def _slice(self, start=None, stop=None):
        stop = stop if stop is not None else self.length
        start = start if start is not None else 0
        if (stop not in Interval(0, self.length) or
            start not in Interval(0, self.length) or
            stop < start):
            raise IndexError
        if start == 0:
            return self.func(stop, self.variable, self.expr)
        else:
            t = self.variable
            expr = self.base_decompose(self.forget(start+t), self.forget(start))
            return self.func(stop-start, t, expr)

    def _mathstr(self, printer):
        return "[{0} ~ {1} |-> {2}]".format(
            printer._print(self.variable),
            printer._print(self.length),
            printer._print(self.expr))

class MultiplicativePath(LambdaPath):
    """
    >>> from sympy import *
    >>> from symplus.strplus import init_mprinting
    >>> init_mprinting()
    >>> t = Symbol('t', positive=True)
    >>> pth1 = MultiplicativePath(10, t, t**2+1); pth1
    [t ~ 10 |-> t**2 + 1]
    >>> pth2 = MultiplicativePath(10, t, exp(t)); pth2
    [t ~ 10 |-> exp(t)]
    >>> pth1.forget(2)
    5
    >>> len(pth1)
    10
    >>> pth1+pth2
    [t ~ 20 |-> (t**2 + 1 if t =< 10; 101*exp(t - 10) if True)]
    >>> pth2[2:5]
    [t ~ 3 |-> exp(-2)*exp(t + 2)]
    >>> pth12 = pth1 * pth2; pth12
    [t ~ 10 |-> t**2 + 1] * [t ~ 10 |-> exp(t)]
    >>> pth12.slice_lambda()
    (t |-> (t**2 + 1, exp(t)))
    >>> pth12.length
    10
    >>> (pth12 + pth12).slice_lambda().expr
    ((t**2 + 1 if t =< 10; 101*(t - 10)**2 + 101 if True), (exp(t) if t =< 10; exp(10)*exp(t - 10) if True))
    >>> pth12[2:7]
    [t ~ 5 |-> (t + 2)**2/5 + 1/5] * [t ~ 5 |-> exp(-2)*exp(t + 2)]
    """
    @staticmethod
    def base_compose(action1, action2):
        return action1 * action2

    @staticmethod
    def base_decompose(action1, action2):
        if is_Matrix(action2):
            return action1 * action2.inv()
        else:
            return action1 / action2

class AdditivePath(LambdaPath):
    """
    >>> from sympy import *
    >>> from symplus.strplus import init_mprinting
    >>> init_mprinting()
    >>> t = Symbol('t', positive=True)
    >>> pth1 = AdditivePath(10, t, t**2+1); pth1
    [t ~ 10 |-> t**2 + 1]
    >>> pth2 = AdditivePath(10, t, exp(t)); pth2
    [t ~ 10 |-> exp(t)]
    >>> pth1.forget(2)
    5
    >>> len(pth1)
    10
    >>> pth1+pth2
    [t ~ 20 |-> (t**2 + 1 if t =< 10; exp(t - 10) + 101 if True)]
    >>> pth2[2:5]
    [t ~ 3 |-> exp(t + 2) - exp(2)]
    >>> pth12 = pth1 * pth2; pth12
    [t ~ 10 |-> t**2 + 1] * [t ~ 10 |-> exp(t)]
    >>> pth12.slice_lambda()
    (t |-> (t**2 + 1, exp(t)))
    >>> pth12.length
    10
    >>> (pth12 + pth12).slice_lambda().expr
    ((t**2 + 1 if t =< 10; (t - 10)**2 + 102 if True), (exp(t) if t =< 10; exp(t - 10) + exp(10) if True))
    >>> pth12[2:7]
    [t ~ 5 |-> (t + 2)**2 - 4] * [t ~ 5 |-> exp(t + 2) - exp(2)]
    """
    @staticmethod
    def base_compose(action1, action2):
        return action1 + action2

    @staticmethod
    def base_decompose(action1, action2):
        return action1 - action2

class TransformationPath(LambdaPath, FunctionObject):
    """
    >>> from sympy import *
    >>> from symplus.strplus import init_mprinting
    >>> init_mprinting()
    >>> t = Symbol('t', positive=True)
    >>> x = Symbol('x')
    >>> pth1 = TransformationPath(10, t, Lambda(x, t*x)); pth1
    [t ~ 10 |-> (x |-> t*x)]
    >>> pth2 = TransformationPath(10, t, Lambda(x, t+x)); pth2
    [t ~ 10 |-> (x |-> t + x)]
    >>> pth1.forget(2)
    (x |-> 2*x)
    >>> len(pth1)
    10
    >>> pth1+pth2
    [t ~ 20 |-> ((x |-> t*x) if t =< 10; (x |-> t + 10*x - 10) if True)]
    >>> pth2[2:5]
    [t ~ 3 |-> (a0 |-> a0 + t)]
    >>> pth12 = pth1 * pth2; pth12
    [t ~ 10 |-> (x |-> t*x)] * [t ~ 10 |-> (x |-> t + x)]
    >>> pth12.slice_lambda()
    (t |-> (Lambda(x, t*x), Lambda(x, t + x)))
    >>> pth12.length
    10
    >>> (pth12 + pth12).slice_lambda().expr
    (((x |-> t*x) if t =< 10; (x |-> 10*x*(t - 10)) if True), (x |-> t + x))
    >>> pth12[2:7]
    [t ~ 5 |-> (a0 |-> a0*(t + 2)/2)] * [t ~ 5 |-> (a0 |-> a0 + t)]
    """
    @staticmethod
    def base_compose(action1, action2):
        return compose(action1, action2)

    @staticmethod
    def base_decompose(action1, action2):
        return compose(action1, inverse(action2))

    @property
    def nres(self):
        return nres(self.forget())

    @property
    def narg(self):
        return narg(self.forget())

    def call(self, *args, **kwargs):
        return self.forget()(*args, **kwargs)

class PathMonoid(Set):
    """
    >>> from sympy import *
    >>> t = Symbol('t', positive=True)
    >>> pmnd1 = PathMonoid(S.Reals); pmnd1
    PathMonoid((-oo, oo))
    >>> AdditivePath(10, t, t**2+1) in pmnd1
    True
    >>> AdditivePath(10, t, t*I+1) in pmnd1
    False
    >>> pmnd2 = pmnd1**2; pmnd2
    PathMonoid((-oo, oo) x (-oo, oo))
    >>> AdditivePath(10, t, t**2+1)*AdditivePath(10, t, exp(t)) in pmnd2
    True
    """
    def __new__(cls, base):
        if not isinstance(base, Set): # it should be a Group
            raise TypeError('base is not a Set: %r' % base)
        return Set.__new__(cls, base)

    @property
    def base(self):
        return self.args[0]

    def _contains(self, pth):
        if not isinstance(pth, Path):
            return False

        elif isinstance(pth, LambdaPath):
            res = self.base._contains(pth.expr)
            if res in (True, False):
                return res
            # return all(pth(t) in self.base for t in range(int(pth.length)+1))

        elif isinstance(pth, TensorPath) and all(isinstance(p, LambdaPath) for p in pth.paths):
            res = self.base._contains(tuple(p.expr for p in pth.paths))
            if res in (True, False):
                return res

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

    def _mathstr(self, printer):
        from sympy.printing.precedence import PRECEDENCE
        return "%s^*" % printer.parenthesize(self.base, PRECEDENCE["Pow"])


