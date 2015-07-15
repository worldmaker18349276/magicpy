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
    @staticmethod
    def tensor(pzlsystems):
        stls = AbstractTensorSet(pzlsys.states for pzlsys in pzlsystems)
        trls = AbstractTensorSet(pzlsys.transitions for pzlsys in pzlsystems)
        apl = tuple(pzlsys.applicationfunction for pzlsys in pzlsystems)
        def lap(stl, trl):
            return tuple(map(lambda ap, st, tr: ap(st, tr), apl, stl, trl))
        return PuzzleSystem(stls, trls, lap)
    def __mul__(self, other):
        return self.tensor((self, other))


class AbstractSet:
    def __init__(self, cond):
        self.condition = cond
    def __contains__(self, member):
        return self.condition(member)
    def __mul__(self, other):
        return AbstractTensorSet((self, other))

class AbstractTensorSet(AbstractSet):
    def __init__(self, asets):
        if not all(hasattr(aset, '__contains__') for aset in asets):
            raise ValueError
        self.sets = asets
    def __contains__(self, members):
        if len(self.sets) != len(members):
            return False
        return all(map(operator.contains, self.sets, members))

