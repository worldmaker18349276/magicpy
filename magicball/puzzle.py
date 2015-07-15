

class IllegalOperationError(Exception):
    pass

class IllegalStateError(Exception):
    pass


class PuzzleSystem:
    def __init__(self, st, tr, func):
        if not hasattr(st, '__contains__'):
            raise ValueError
        if not hasattr(tr, '__contains__'):
            raise ValueError
        if not hasattr(func, '__call__'):
            raise ValueError
        self.states = st
        self.transitions = tr
        self.applicationfunction = func
        class Puzzle:
            def __init__(pzl, st):
                pzl.state = st
            @property
            def state(pzl):
                return pzl.__state
            @state.setter
            def setState(pzl, st):
                if st not in self.states:
                    raise IllegalStateError
                pzl.__state = st
            def __mul__(pzl, trans):
                if trans not in self.transitions:
                    raise IllegalOperationError
                pzl.state = self.applicationfunction(pzl.state, trans)
        self.puzzle = Puzzle
    def tensor(pzlsystems):
        st = AbstractTensorSet(pzlsys.states for pzlsys in pzlsystems)
        tr = AbstractTensorSet(pzlsys.transitions for pzlsys in pzlsystems)
        aps = tuple(pzlsys.applicationfunction for pzlsys in pzlsystems)
        def ap(sts, trs):
            return tuple(map(lambda ap, st, tr: ap(st, tr), aps, sts, trs))
        return PuzzleSystem(st, tr, ap)
    def __mul__(self, other):
        return tensor((self, other))


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
        return all(members in aset for aset in self.sets)

