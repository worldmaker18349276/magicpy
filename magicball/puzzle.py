from functools import reduce
from mathplus import *


class IllegalOperationError(Exception):
    pass

class IllegalStateError(Exception):
    pass


class PuzzleSystem:
    def __init__(self, sts, ops, ap):
        if not hasattr(sts, '__contains__'):
            raise TypeError
        if not hasattr(ops, '__contains__'):
            raise TypeError
        if not hasattr(ap, '__call__'):
            raise TypeError
        self.states = sts
        self.operations = ops
        self.application = ap
    def __str__(self):
        return '('+str(self.states)+', '+str(self.operations)+', '+str(self.application)+')'
    def apply(self, st, op):
        if st not in self.states or op not in self.operations:
            return None
        if any(self.application(st, op[:t+1]) not in self.states for t in range(len(op))):
            return None
        return self.application(st, op)

class DiscretePuzzleSystem(PuzzleSystem):
    def __init__(self, sts, pops, pap):
        if not hasattr(sts, '__contains__'):
            raise TypeError
        if not hasattr(pops, '__contains__'):
            raise TypeError
        if not hasattr(pap, '__call__'):
            raise TypeError
        self.states = sts
        self.primaryoperations = pops
        self.primaryapplication = pap
        self.operations = FreeMonoid(pops)
        self.application = lambda st, op: reduce(pap, op, st)
    def tensor(pzlsystems):
        pzlsystems = tuple(pzlsystems)
        if any(not isinstance(pzlsys, DiscretePuzzleSystem) for pzlsys in pzlsystems):
            raise TypeError
        stls = AbstractSet.tensor(pzlsys.states for pzlsys in pzlsystems)
        popls = AbstractSet.tensor(pzlsys.primaryoperations for pzlsys in pzlsystems)
        papl = tuple(pzlsys.primaryapplication for pzlsys in pzlsystems)
        lpap = lambda stl, popl: tuple(map(lambda pap, st, pop: pap(st, pop), papl, stl, popl))
        return DiscretePuzzleSystem(stls, popls, lpap)

class ContinuousPuzzleSystem(PuzzleSystem):
    def __init__(self, sts, bops, bap):
        if not hasattr(sts, '__contains__'):
            raise TypeError
        if not hasattr(bops, '__contains__'):
            raise TypeError
        if not hasattr(bap, '__call__'):
            raise TypeError
        self.states = sts
        self.basedoperations = bops
        self.basedapplication = bap
        self.operations = PathMonoid(bops)
        self.application = lambda st, op: bap(st, op(len(op)))
    def tensor(pzlsystems):
        pzlsystems = tuple(pzlsystems)
        if any(not isinstance(pzlsys, ContinuousPuzzleSystem) for pzlsys in pzlsystems):
            raise TypeError
        stls = AbstractSet.tensor(pzlsys.states for pzlsys in pzlsystems)
        bopls = AbstractSet.tensor(pzlsys.basedoperations for pzlsys in pzlsystems)
        bapl = tuple(pzlsys.basedapplication for pzlsys in pzlsystems)
        lbap = lambda stl, bopl: tuple(map(lambda bap, st, bop: bap(st, bop), bapl, stl, bopl))
        return ContinuousPuzzleSystem(stls, bopls, lbap)

