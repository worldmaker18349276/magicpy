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
    def apply(self, st, eop):
        if st not in self.stateset or eop not in self.extendedoperationset:
            return None
        if any(eap(st, eop[:t+1]) not in rsts for t in range(len(eop))):
            return None
        return eap(st, eop)

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
                                                if isinstance(eop, Path) else False)
        self.extendedapplication = lambda st, eop: bap(st, eop(len(eop)))


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

