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
        self.sets = asets
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
        self.sets = asets
    def __contains__(self, member):
        return all(member in aset for aset in self.sets)
    def __and__(self, other):
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

