import operator
from sympy import MatrixBase


class AbstractSet:
    def __init__(self, cond):
        if not hasattr(cond, '__call__'):
            raise TypeError
        self.condition = cond
    def __contains__(self, mem):
        return self.condition(mem)
    def __and__(self, other):
        if not hasattr(other, '__contains__'):
            raise TypeError
        return AbstractSet(lambda mem: mem in self and mem in other)
    def __or__(self, other):
        if not hasattr(other, '__contains__'):
            raise TypeError
        return AbstractSet(lambda mem: mem in self or mem in other)
    def __invert__(self):
        return AbstractSet(lambda mem: not mem in self)
    def __mul__(self, other):
        return AbstractSet.tensor((self, other))
    def __pow__(self, n):
        return AbstractSet.tensor((self,)*n)
    @staticmethod
    def tensor(asets):
        asets = tuple(asets)
        if any(not hasattr(aset, '__contains__') for aset in asets):
            raise TypeError
        def tensor_contains(mem):
            if not isinstance(mem, tuple):
                return False
            if len(asets) != len(mem):
                return False
            return all(map(operator.contains, asets, mem))
        return AbstractSet(tensor_contains)


class FreeMonoid(AbstractSet):
    def __init__(self, ab):
        if not hasattr(ab, '__contains__'):
            raise TypeError
        self.alphabet = ab
    def __contains__(self, mem):
        if not isinstance(mem, list):
            return False
        return all(mem[t] in self.alphabet for t in range(len(mem)))
    def __mul__(self, other):
        return FreeMonoid.tensor((self, other))
    def __pow__(self, n):
        return FreeMonoid.tensor((self,)*n)
    @staticmethod
    def tensor(fmnds):
        fmnds = tuple(fmnds)
        if any(not isinstance(fmnd, FreeMonoid) for fmnd in fmnds):
            raise TypeError
        return FreeMonoid(AbstractSet.tensor(fmnd.alphabet for fmnd in fmnds))

class PathMonoid(AbstractSet):
    def __init__(self, bs):
        if not hasattr(bs, '__contains__'):
            raise TypeError
        self.base = bs
    def __contains__(self, mem):
        if not isinstance(mem, Path):
            return False
        return all(mem(t) in self.base for t in range(len(mem)+1))
    def __mul__(self, other):
        return PathMonoid.tensor((self, other))
    def __pow__(self, n):
        return PathMonoid.tensor((self,)*n)
    @staticmethod
    def tensor(pmnds):
        pmnds = tuple(pmnds)
        if any(not isinstance(pmnd, PathMonoid) for pmnd in pmnds):
            raise TypeError
        return PathMonoid(AbstractSet.tensor(pmnd.base for pmnd in pmnds))

class Path:
    def __init__(self, func, flen):
        if not hasattr(func, '__call__'):
            raise TypeError
        if not isinstance(flen, int):
            raise TypeError
        self.function = func
        self.length = flen
    def __len__(self):
        return self.length
    def __add__(self, other):
        if not isinstance(other, Path):
            raise ValueError
        func1 = self.function
        func2 = other.function
        flen1 = self.length
        flen2 = other.length
        return Path(lambda t: func2(t-flen1)*func1(flen1) if t>flen1 else func1(t), flen1+flen2)
    def __getitem__(self, key):
        if not isinstance(key, slice):
            raise TypeError
        func = self.function
        stp = key.stop if key.stop is not None else self.length
        strt = key.start if key.start is not None else 0
        if stp not in range(self.length+1) or strt not in range(self.length+1) or stp < strt:
            raise IndexError
        if strt == 0:
            return Path(func, stp)
        else:
            return Path(lambda t: func(strt+t)/func(strt), stp-strt)
    def __call__(self, t):
        if t not in range(self.length+1):
            raise IndexError
        return self.function(t)
    def __mul__(self, other):
        return Path.tensor((self, other))
    def __pow__(self, n):
        return Path.tensor((self,)*n)
    @staticmethod
    def tensor(pths):
        pths = tuple(pths)
        if any(not isinstance(pth, Path) for pth in pths):
            raise TypeError
        if max(len(pth) for pth in pths) != min(len(pth) for pth in pths):
            raise ValueError
        return Path(lambda t: tuple(map(pth.function(t) for pth in pths)), len(pths[0]))

