from functools import reduce
from mathplus import *


class IllegalOperationError(Exception):
    pass

class IllegalStateError(Exception):
    pass


class PuzzleSystem:
    def __init__(self, sts, eops, eap):
        if not hasattr(sts, '__contains__'):
            raise ValueError
        if not hasattr(eops, '__contains__'):
            raise ValueError
        if not hasattr(eap, '__call__'):
            raise ValueError
        self.stateset = sts
        self.extendedoperationset = eops
        self.extendedapplication = eap
    def __str__(self):
        return '('+str(self.stateset)+', '+str(self.extendedoperationset)+', '+str(self.extendedapplication)+')'
    def puzzle(self, *args, **kwargs):
        return Puzzle(self, *args, **kwargs)

class Puzzle:
    def __init__(self, pzlsys, st):
        self.system = pzlsys
        self.state = st
    @property
    def state(self):
        return self.__state
    @state.setter
    def state(self, st):
        if st not in self.system.stateset:
            raise IllegalStateError
        self.__state = st
    def __imul__(self, op):
        if op not in self.system.extendedoperationset:
            raise IllegalOperationError
        self.state = self.system.extendedapplication(self.state, op)
    def __mul__(self, op):
        if op not in self.system.extendedoperationset:
            raise IllegalOperationError
        return self.system.puzzle(self.system.extendedapplication(self.state, op))
    def __str__(self):
        return str(self.state)


def restrict(pzlsys, cond):
    if isinstance(pzlsys, ContinuousPuzzleSystem):
        restrictedstateset = pzlsys.stateset & AbstractSet(cond)
        def extendedrestrictedapplication(st, eop):
            def rap(st, eop):
                if st is None:
                    return None
                st2 = pzlsys.extendedapplication(st, eop)
                if st2 in restrictedstateset:
                    return st2
                else:
                    return None
            n = 1000
            return reduce(rap, eop[::1/n], st)
        return ContinuousPuzzleSystem(restrictedstateset, pzlsys.extendedoperationset, extendedrestrictedapplication)
    elif isinstance(pzlsys, PuzzleSystem):
        restrictedstateset = pzlsys.stateset & AbstractSet(cond)
        def restrictedapplication(st, op):
            if st is None:
                return None
            st2 = pzlsys.application(st, op)
            if st2 in restrictedstateset:
                return st2
            else:
                return None
        return PuzzleSystem(restrictedstateset, pzlsys.operationset, restrictedapplication)
    else:
        raise ValueError


def tensor(pzlsystems):
    if all(isinstance(pzlsys, ContinuousPuzzleSystem) for pzlsys in pzlsystems):
        pzlsystems = tuple(pzlsystems)
        stls = AbstractTensorSet(pzlsys.stateset for pzlsys in pzlsystems)
        samelen = lambda opl: max(len(op) for op in opl) == min(len(op) for op in opl)
        opls = AbstractTensorSet(pzlsys.extendedoperationset for pzlsys in pzlsystems) & AbstractSet(samelen)
        apl = tuple(pzlsys.extendedapplication for pzlsys in pzlsystems)
        def lap(stl, opl):
            stl2 = tuple(map(lambda ap, st, op: ap(st, op), apl, stl, opl))
            if any(st2 is None for st2 in stl2):
                return None
            else:
                return stl2
        return PuzzleSystem(stls, opls, lap)
    elif all(isinstance(pzlsys, PuzzleSystem) and not isinstance(pzlsys, ContinuousPuzzleSystem) for pzlsys in pzlsystems):
        pzlsystems = tuple(pzlsystems)
        stls = AbstractTensorSet(pzlsys.stateset for pzlsys in pzlsystems)
        opls = AbstractTensorSet(pzlsys.operationset for pzlsys in pzlsystems)
        apl = tuple(pzlsys.application for pzlsys in pzlsystems)
        def lap(stl, opl):
            stl2 = tuple(map(lambda ap, st, op: ap(st, op), apl, stl, opl))
            if any(st2 is None for st2 in stl2):
                return None
            else:
                return stl2
        return PuzzleSystem(stls, opls, lap)
    else:
        raise ValueError

