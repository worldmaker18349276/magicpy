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
        self.extendedoperationset = FreeMonoid(ops)
        self.extendedapplication = lambda st, eop: reduce(ap, eop, st)
    def tensor(pzlsystems):
        pzlsystems = tuple(pzlsystems)
        if any(not isinstance(pzlsys, DiscretePuzzleSystem) for pzlsys in pzlsystems):
            raise TypeError
        stls = AbstractSet.tensor(pzlsys.stateset for pzlsys in pzlsystems)
        opls = AbstractSet.tensor(pzlsys.operationset for pzlsys in pzlsystems)
        apl = tuple(pzlsys.application for pzlsys in pzlsystems)
        lap = lambda stl, opl: tuple(map(lambda ap, st, op: ap(st, op), apl, stl, opl))
        return DiscretePuzzleSystem(stls, opls, lap)

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
        self.extendedoperationset = PathMonoid(bops)
        self.extendedapplication = lambda st, eop: bap(st, eop(len(eop)))
    def tensor(pzlsystems):
        pzlsystems = tuple(pzlsystems)
        if any(not isinstance(pzlsys, ContinuousPuzzleSystem) for pzlsys in pzlsystems):
            raise TypeError
        stls = AbstractSet.tensor(pzlsys.stateset for pzlsys in pzlsystems)
        bopls = ContinuousPuzzleSystem.tensor(pzlsys.basedoperationset for pzlsys in pzlsystems)
        bapl = tuple(pzlsys.basedapplication for pzlsys in pzlsystems)
        lbap = lambda stl, bopl: tuple(map(lambda bap, st, bop: bap(st, bop), bapl, stl, bopl))
        return ContinuousPuzzleSystem(stls, bopls, lbap)

