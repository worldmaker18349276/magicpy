import operator


class AbstractSet:
    def __init__(self, cond):
        self.condition = cond
    def __contains__(self, member):
        return self.condition(member)
    def __and__(self, other):
        if not hasattr(other, '__contains__'):
            raise ValueError
        cond1 = self.condition
        cond2 = other.condition
        return AbstractSet(lambda mem: cond1(mem) and cond2(mem))
    def __or__(self, other):
        if not hasattr(other, '__contains__'):
            raise ValueError
        cond1 = self.condition
        cond2 = other.condition
        return AbstractSet(lambda mem: cond1(mem) or cond2(mem))


class AbstractTensorSet(AbstractSet):
    def __init__(self, asets):
        self.sets = tuple(asets)
        if not all(hasattr(aset, '__contains__') for aset in self.sets):
            raise ValueError
    def __contains__(self, members):
        if not hasattr(members, '__len__'):
            return False
        if len(self.sets) != len(members):
            return False
        return all(map(operator.contains, self.sets, members))
    @property
    def condition(self):
        return self.__contains__


class Path:
    def __init__( self, func, flen ):
        self.function = func
        self.length = flen
    def __len__( self ):
        return self.length
    def __add__( self, other ):
        if not isinstance(other, Path):
            raise ValueError
        func1 = self.function
        func2 = other.function
        flen1 = self.length
        flen2 = other.length
        return Path(lambda t: func1(flen1)*func2(t-flen1) if t>flen1 else func1(t), flen1+flen2)
    def __getitem__( self, key ):
        if not isinstance(key, slice):
            raise ValueError
        stp = key.stop if key.stop is not None else self.length
        strt = key.start if key.start is not None else 0
        if stp not in range(self.length+1) or strt not in range(self.length) or stp < strt:
            raise ValueError
        func = self.function
        return Path(lambda t: func(strt+t), stp-strt)
    def __call__( self, t ):
        if t not in range(self.length):
            raise ValueError
        return self.function(t)

