from functools import reduce
import operator


class IllegalOperationError(Exception):
    pass

class IllegalStateError(Exception):
    pass


class PuzzleSystem:
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
    def __str__(self):
        return '('+str(self.stateset)+', '+str(self.operationset)+', '+str(self.application)+')'
    def operation(self, *args, **kwargs):
        return Operation(self, *args, **kwargs)
    def puzzle(self, *args, **kwargs):
        return Puzzle(self, *args, **kwargs)

class ContinuousPuzzleSystem(PuzzleSystem):
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
    @property
    def operationset(self):
        return self.extendedoperationset
    def application(self, st, eop):
        return self.extendedapplication(st, eop)
    def __str__(self):
        return '('+str(self.stateset)+', '+str(self.extendedoperationset)+', '+str(self.extendedapplication)+')'
    def operation(self, *args, **kwargs):
        return Operation(self, *args, **kwargs)
    def puzzle(self, *args, **kwargs):
        return Puzzle(self, *args, **kwargs)

class Operation:
    def __init__(self, pzlsys, ops):
        self.system = pzlsys
        self.operations = tuple(ops)
    @property
    def operations(self):
        return self.__operations
    @operations.setter
    def operations(self, ops):
        if all(op not in self.system.operationset for op in ops):
            raise IllegalOperationError
        self.__operations = ops
    def append(self, op):
        if op in self.system.operationset:
            self.__operations = self.__operations + (op)
        elif isinstance(op, Operation) and op.system == self.system:
            self.__operations = self.__operations + op.__operations
        else:
            raise IllegalOperationError
    def __mul__(self, op):
        if op in self.system.operationset:
            return self.system.operation(self.__operations + (op))
        elif isinstance(op, Operation) and op.system == self.system:
            return self.system.operation(self.__operations + op.__operations)
        else:
            raise IllegalOperationError
    def __iter__(self):
        return iter(self.operations)
    def __str__(self):
        return '*'.join(str(op) for op in self.operations)

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
    def operate(self, op):
        if op in self.system.operationset:
            self.state = self.system.application(self.state, op)
        elif isinstance(op, Operation) and op.system == self.system:
            for _ in map(self.operate, op):
                pass
        else:
            raise IllegalOperationError
    def __mul__(self, op):
        if op in self.system.operationset:
            return self.system.puzzle(self.system.application(self.state, op))
        elif isinstance(op, Operation) and op.system == self.system:
            pzl2 = self.system.puzzle(self.state)
            pzl2.operate(op)
            return pzl2
        else:
            raise IllegalOperationError
    def __str__(self):
        return str(self.state)

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
    stls = AbstractTensorSet(pzlsys.stateset for pzlsys in pzlsystems)
    opls = AbstractTensorSet(pzlsys.operationset for pzlsys in pzlsystems)
    apl = tuple(pzlsys.application for pzlsys in pzlsystems)
    def lap(stl, opl):
        return tuple(map(lambda ap, st, op: ap(st, op), apl, stl, opl))
    return PuzzleSystem(stls, opls, lap)

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

