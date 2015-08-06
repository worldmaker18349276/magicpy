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
    def restrict(self, cond):
        rsts = AbstractSet(cond) & self.stateset
        eap = self.extendedapplication
        erap = lambda rst, eop: eap(rst, eop[:len(eop)])
               if all(eap(rst, eop[:t]) in rsts for t in range(len(eop)))
               else None
        return PuzzleSystem(rsts, self.extendedoperationset, erap)

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


class DiscretePuzzleSystem(PuzzleSystem):
    def __init__(self, sts, ops, ap):
        if not hasattr(sts, '__contains__'):
            raise ValueError
        if not hasattr(ops, '__contains__'):
            raise ValueError
        if not hasattr(ap, '__call__'):
            raise ValueError
        self.stateset = sts
        self.operationset = ops
        self.application = ap
        self.extendedoperationset = AbstractSet(lambda eop: all(op in ops for op in eop)
                                                if hasattr(eop, '__len__') else False)
        self.extendedapplication = lambda st, eop: reduce(ap, eop, st)

class ContinuousPuzzleSystem(PuzzleSystem):
    def __init__(self, sts, bops, bap):
        if not hasattr(sts, '__contains__'):
            raise ValueError
        if not hasattr(bops, '__contains__'):
            raise ValueError
        if not hasattr(bap, '__call__'):
            raise ValueError
        self.stateset = sts
        self.basedoperationset = bops
        self.basedapplication = bap
        self.extendedoperationset = AbstractSet(lambda eop: all(eop(t) in bops for t in range(len(eop)))
                                                if hasattr(eop, '__len__') and hasattr(eop, '__call__')
                                                else False)
        self.extendedapplication = lambda st, eop: bap(st, eop(len(eop)))
                                   if all(bap(st, eop(t)) is not None for t in range(len(eop)))
                                   else None


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

