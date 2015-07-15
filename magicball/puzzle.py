import operator


class IllegalOperationError(Exception):
    pass

class IllegalStateError(Exception):
    pass


class PuzzleSystem:
    def __init__(self, sts, trs, ap):
        if not hasattr(sts, '__contains__'):
            raise ValueError
        if not hasattr(trs, '__contains__'):
            raise ValueError
        if not hasattr(ap, '__call__'):
            raise ValueError
        self.states = sts
        self.transitions = trs
        self.applicationfunction = ap
        class Puzzle:
            def __init__(pzl, st):
                pzl.state = st
            @property
            def state(pzl):
                return pzl.__state
            @state.setter
            def state(pzl, st):
                if st not in self.states:
                    raise IllegalStateError
                pzl.__state = st
            def operate(pzl, tr):
                if tr not in self.transitions:
                    raise IllegalOperationError
                pzl.state = self.applicationfunction(pzl.state, tr)
            def __mul__(pzl, tr):
                if tr not in self.transitions:
                    raise IllegalOperationError
                return self.puzzle(self.applicationfunction(pzl.state, tr))
            def __str__(pzl):
                return str(pzl.state)
        self.puzzle = Puzzle
    def __str__(self):
        return '('+str(self.states)+', '+str(self.transitions)+', '+str(self.applicationfunction)+')'

class AbstractSet:
    def __init__(self, cond):
        self.condition = cond
    def __contains__(self, member):
        return self.condition(member)
    def __str__(self):
        return '{x|'+str(self.condition)+'(x)}'


def tensor(pzlsystems):
    if hasattr(pzlsystems, '__next__'):
        pzlsystems = tuple(pzlsystems)
    stls = AbstractTensorSet(pzlsys.states for pzlsys in pzlsystems)
    trls = AbstractTensorSet(pzlsys.transitions for pzlsys in pzlsystems)
    apl = tuple(pzlsys.applicationfunction for pzlsys in pzlsystems)
    def lap(stl, trl):
        return tuple(map(lambda ap, st, tr: ap(st, tr), apl, stl, trl))
    return PuzzleSystem(stls, trls, lap)

PuzzleSystem.__mul__ = lambda self, other: tensor((self, other))

class AbstractTensorSet(AbstractSet):
    def __init__(self, asets):
        self.sets = tuple(asets)
        if not all(hasattr(aset, '__contains__') for aset in self.sets):
            raise ValueError
    def __contains__(self, members):
        if len(self.sets) != len(members):
            return False
        return all(map(operator.contains, self.sets, members))
    @property
    def condition(self):
        return self.__contains__
    def __str__(self):
        return '('+'*'.join(str(aset) for aset in self.sets)+')'

AbstractSet.__mul__ = lambda self, other: AbstractTensorSet((self, other))

