

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
    def __mul__(self, other): # tensor product
        return TensorPuzzleSystem(self, other)
    def puzzle(pzlsystem):
        class Puzzle:
            def __init__(self, st):
                self.state = st
            @property
            def system(self):
                return pzlsystem
            @property
            def state(self):
                return self.__state
            @state.setter
            def setState(self, st):
                if st not in pzlsystem.states:
                    raise IllegalStateError
                self.__state = st
            def __mul__(self, trans):
                if trans not in pzlsystem.transitions:
                    raise IllegalOperationError
                self.state = pzlsystem.applicationfunction(self.state, trans)
        return Puzzle

class TensorPuzzleSystem(PuzzleSystem):
    def __init__(self, *pzlsystems):
        self.systems = pzlsystems
    @property
    def states(self):
        AbstractTensorSet(*(pzlsys.states for pzlsys in self.systems))
    @property
    def transitions(self):
        AbstractTensorSet(*(pzlsys.transitions for pzlsys in self.systems))
    @property
    def applicationfunction(self):
        aps = tuple(pzlsys.applicationfunction for pzlsys in self.systems)
        def tensorapplicationfunction(sts, trs):
            return tuple(map(lambda ap, st, tr: ap(st, tr), aps, sts, trs))
        return tensorapplicationfunction


class AbstractSet:
    def __init__(self, cond):
        self.condition = cond
    def __contains__(self, member):
        return self.condition(member)
    def __mul__(self, other): # tensor product
        if hasattr(other, '__contains__'):
            return AbstractTensorSet(self, other)
        else:
            raise ValueError

class AbstractTensorSet(AbstractSet):
    def __init__(self, *asets):
        if not all(hasattr(aset, '__contains__') for aset in asets):
            raise ValueError
        self.sets = asets
    def __contains__(self, members):
        if len(self.sets) != len(members):
            return False
        return all(members in aset for aset in self.sets)
    def __mul__(self, other): # tensor product
        if hasattr(other, '__contains__'):
            return AbstractTensorSet(*self.sets, other)
        else:
            raise ValueError

