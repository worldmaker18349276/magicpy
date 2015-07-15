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
    def __str__(self):
        return '('+str(self.states)+', '+str(self.transitions)+', '+str(self.applicationfunction)+')'
    def operation(self, *args, **kwargs):
        return Operation(self, *args, **kwargs)
    def puzzle(self, *args, **kwargs):
        return Puzzle(self, *args, **kwargs)

class Operation:
    def __init__(op, pzlsys, trs):
        op.system = pzlsys
        op.transitions = tuple(trs)
    @property
    def transitions(op):
        return op.__transitions
    @transitions.setter
    def transitions(op, trs):
        if all(tr not in op.system.transitions for tr in trs):
            raise IllegalOperationError
        op.__transitions = trs
    def append(op, tr):
        if tr in op.system.transitions:
            op.__transitions = op.__transitions + (tr)
        elif isinstance(tr, Operation) and tr.system == op.system:
            op.__transitions = op.__transitions + tr.__transitions
        else:
            raise IllegalOperationError
    def __mul__(op, tr):
        if tr in op.system.transitions:
            return op.system.operation(op.__transitions + (tr))
        elif isinstance(tr, Operation) and tr.system == op.system:
            return op.system.operation(op.__transitions + tr.__transitions)
        else:
            raise IllegalOperationError
    def __iter__(op):
        return iter(op.transitions)
    def __str__(op):
        return '*'.join(str(tr) for tr in op.transitions)

class Puzzle:
    def __init__(pzl, pzlsys, st):
        pzl.system = pzlsys
        pzl.state = st
    @property
    def state(pzl):
        return pzl.__state
    @state.setter
    def state(pzl, st):
        if st not in pzl.system.states:
            raise IllegalStateError
        pzl.__state = st
    def operate(pzl, tr):
        if tr in pzl.system.transitions:
            pzl.state = pzl.system.applicationfunction(pzl.state, tr)
        elif isinstance(tr, Operation) and tr.system == pzl.system:
            for _ in map(pzl.operate, tr):
                pass
        else:
            raise IllegalOperationError
    def __mul__(pzl, tr):
        if tr in pzl.system.transitions:
            return pzl.system.puzzle(pzl.system.applicationfunction(pzl.state, tr))
        elif isinstance(tr, Operation) and tr.system == pzl.system:
            pzl2 = pzl.system.puzzle(pzl.state)
            pzl2.operate(tr)
            return pzl2
        else:
            raise IllegalOperationError
    def __str__(pzl):
        return str(pzl.state)

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

AbstractSet.__mul__ = lambda self, other: AbstractTensorSet((self, other))

