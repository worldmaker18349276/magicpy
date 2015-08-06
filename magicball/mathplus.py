import operator


class AbstractSet:
    def __init__(self, cond):
        self.condition = cond
    def __contains__(self, member):
        return self.condition(member)
    def __and__(self, other):
        if isinstance(other, AbstractAndSet):
            return AbstractAndSet((self) + other.sets)
        else:
            return AbstractAndSet((self, other))
    def __or__(self, other):
        if isinstance(other, AbstractOrSet):
            return AbstractOrSet((self) + other.sets)
        else:
            return AbstractOrSet((self, other))
    def __str__(self):
        return '{x|'+str(self.condition)+'(x)}'

class AbstractAndSet(AbstractSet):
    def __init__(self, asets):
        self.sets = tuple(asets)
    def __contains__(self, member):
        return all(member in aset for aset in self.sets)
    def __and__(self, other):
        if isinstance(other, AbstractAndSet):
            return AbstractAndSet(self.sets + other.sets)
        else:
            return AbstractAndSet(self.sets + (other))
    def __str__(self):
        return '('+'&'.join(str(aset) for aset in self.sets)+')'

class AbstractOrSet(AbstractSet):
    def __init__(self, asets):
        self.sets = tuple(asets)
    def __contains__(self, member):
        return all(member in aset for aset in self.sets)
    def __or__(self, other):
        if isinstance(other, AbstractOrSet):
            return AbstractOrSet(self.sets + other.sets)
        else:
            return AbstractOrSet(self.sets + (other))
    def __str__(self):
        return '('+'|'.join(str(aset) for aset in self.sets)+')'


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
    def __str__(self):
        return '('+'*'.join(str(aset) for aset in self.sets)+')'


class Path:
    def __init__( self, func, flen ):
        self.function = func
        self.length = flen
    def __len__( self ):
        return self.length
    def __add__( self, other ):
        if isinstance(other, Path):
            func1 = self.function
            func2 = other.function
            flen1 = self.length
            flen2 = other.length
            return Path(lambda t: func1(flen1)*func2(t-flen1) if t>flen1 else func1(t), flen1+flen2)
        else:
            raise ValueError
    def __getitem__( self, key ):
        if not isinstance(key, slice):
            raise ValueError
        stp = key.stop or self.length
        strt = key.start or 0
        if stp not in range(self.length) or strt not in range(self.length) or stp < strt:
            raise ValueError
        func = self.function
        return Path(lambda t: func(strt+t), stp-strt)
    def __call__( self, t ):
        if t in range(self.length):
            return self.function(t)
        else:
            raise ValueError

