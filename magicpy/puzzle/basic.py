"""
this module define control method for puzzle, and implement the procedure for
dealing with monoid-structured operation and continuous operation.
`is_valid_operation`, `is_valid_state` indicate the limitation rule of
puzzle; `transform` and `apply` indicate operation rule of puzzle.
"""
from magicpy.util import thiz, map


class IllegalOperationError(Exception):
    pass

class IllegalStateError(Exception):
    pass


class Puzzle(object):
    """
    basic class of all puzzles.
    """
    def is_valid_state(self):
        """
        True if this puzzle is in the valid state.
        """
        return True

    def is_valid_operation(self, op):
        """
        True if `op` is valid operation for this state, where `op` should be
        elementary operation.
        """
        return False

    def new(self, *args, **kwargs):
        """
        re-build puzzle from given parameters with this state as default.
        """
        return type(self)(*args, **kwargs)

class Operation(object):
    """
    basic class of all operations.
    """
    def apply(self, pzl):
        """
        apply this operation to puzzle `pzl`.
        """
        # this implementation is for elementary operation.
        if not pzl.is_valid_operation(self):
            raise IllegalOperationError

        pzl = self.transform(pzl)

        if not pzl.is_valid_state():
            raise IllegalStateError

        return pzl

    def transform(self, pzl):
        """
        transform puzzle `pzl` by this operation.
        """
        raise NotImplementedError

    def new(self, *args, **kwargs):
        """
        re-build operation from given parameters with this operation as
        default.
        """
        return type(self)(*args, **kwargs)

    def __mul__(self, other):
        return ConcatenatedOperation(self, other)

class WrappedOperation(Operation):
    def interpret_for(self, pzl):
        """
        interpret this operation as exact operation for puzzle `pzl`.
        """
        raise NotImplementedError

    def apply(self, pzl):
        return self.interpret_for(pzl).apply(pzl)

    def transform(self, pzl):
        return self.interpret_for(pzl).transform(pzl)

class IdentityOperation(Operation):
    """
    operation that do nothing.
    `IdentityOperation` is monoid-structured operation.
    """
    def apply(self, pzl):
        return pzl

    def transform(self, pzl):
        return pzl

    def __repr__(self):
        return "%s()"%type(self).__name__

    def __str__(self):
        return "Id"

class ConcatenatedOperation(Operation):
    """
    operation which apply operations sequentially.
    `ConcatenatedOperation` is monoid-structured operation.
    """
    def __new__(cls, *ops):
        if any(not isinstance(op, Operation) for op in ops):
            raise TypeError

        ops = ConcatenatedOperation.reduce(ops)

        if len(ops) == 0:
            return IdentityOperation()
        elif len(ops) == 1:
            return ops[0]
        else:
            op = Operation.__new__(cls)
            op.operations = ops
            return op

    @staticmethod
    def reduce(ops):
        ops = list(ops)
        i = 0
        while i < len(ops):
            if isinstance(ops[i], IdentityOperation):
                del ops[i]

            elif isinstance(ops[i], ConcatenatedOperation):
                ops[i:i+1] = ops[i].operations

            else:
                i = i + 1

        return tuple(ops)

    def apply(self, pzl):
        for op in self.operations:
            pzl = op.apply(pzl)
        return pzl

    def transform(self, pzl):
        for op in self.operations:
            pzl = op.transform(pzl)
        return pzl

    def __len__(self):
        return len(self.operations)

    def __getitem__(self, key):
        if isinstance(key, int):
            return self.operations[key]
        elif isinstance(key, slice):
            return self.new(*self.operations[key])
        else:
            raise IndexError

    def __repr__(self):
        return "%s%s"%(type(self).__name__, str(self.operations))

    def __str__(self):
        return "*".join(map(str, self.operations))

class ContinuousOperation(Operation):
    """
    operation which operate continuously.
    continuous operation can be cutted to any distance.
    """
    density = 10.0

    @property
    def distance(self):
        """
        total distance of this operation.
        """
        raise NotImplementedError

    def to(self, dis):
        """
        cut this operation to distance `dis`.
        """
        raise NotImplementedError

    def apply(self, pzl):
        if not pzl.is_valid_operation(self):
            raise IllegalOperationError

        for t in range(int(self.distance*self.density)+1):
            moved = self.to(t/self.density).transform(pzl)
            if not moved.is_valid_state():
                raise IllegalOperationError

        pzl = self.transform(pzl)
        if not pzl.is_valid_state():
            raise IllegalStateError

        return pzl


class TensorPuzzle(Puzzle, tuple):
    """
    tensor of puzzles.
    """
    def __new__(cls, pzls):
        pzls = tuple(pzls)
        if not all(isinstance(pzl_i, Puzzle) for pzl_i in pzls):
            raise TypeError
        return tuple.__new__(cls, pzls)

    def is_valid_state(self):
        return all(map(thiz.is_valid_state, self))

    def is_valid_operation(self, op):
        return (isinstance(op, TensorOperation) and
                len(self) == len(op) and
                all(map(thiz.is_valid_operation, self, op)))

    def __add__(self, other):
        if type(self) == type(other):
            return self.new(tuple(self)+tuple(other))

        else:
            raise TypeError

    def __getitem__(self, key):
        value = super(TensorPuzzle, self).__getitem__(key)
        if isinstance(key, int):
            return value
        elif isinstance(key, slice):
            return self.new(value)
        else:
            raise IndexError

    def __repr__(self):
        return "%s(%s)"%(type(self).__name__, str(tuple(self)))

    def __str__(self):
        return str(tuple(self))

    def __hash__(self):
        return hash((type(self), tuple(self)))

class TensorOperation(Operation, tuple):
    """
    tensor of operations.
    """
    def transform(self, pzl):
        return pzl.new(map(thiz.transform, self, pzl))

    def __add__(self, other):
        if type(self) == type(other):
            return self.new(tuple(self)+tuple(other))

        else:
            raise TypeError

    def __getitem__(self, key):
        value = super(TensorOperation, self).__getitem__(key)
        if isinstance(key, int):
            return value
        elif isinstance(key, slice):
            return self,new(value)
        else:
            raise IndexError

    def __repr__(self):
        return "%s(%s)"%(type(self).__name__, str(tuple(self)))

    def __str__(self):
        return str(tuple(self))

class ParallelOperation(ContinuousOperation, TensorOperation):
    """
    continuous tensor operation.
    operations are parallelly operate on the puzzle.
    """
    def __new__(cls, ops):
        ops = tuple(ops)
        if not all(isinstance(op_i, ContinuousOperation) for op_i in ops):
            raise TypeError
        if len(set(map(thiz.distance, ops))) != 1:
            raise ValueError
        return TensorOperation.__new__(cls, ops)

    @property
    def distance(self):
        return self[0].distance

    def to(self, dis):
        return self.new(op_i.to(dis) for op_i in self)


class CombinationalPuzzle(Puzzle, tuple):
    """
    puzzle composed by multiple elements.
    """
    ordered = True

    def is_valid_state(self):
        return all(map(self.is_valid_elem, self))

    def is_valid_operation(self, op):
        return len(self) == len(op) and all(map(self.is_valid_action, op))

    def is_valid_elem(self, elem):
        """
        True if `elem` is in the valid element.
        """
        raise NotImplementedError

    def is_valid_action(self, act):
        """
        True if `act` is valid action.
        """
        raise NotImplementedError

    def sort(self):
        """
        sort elements of this puzzle.
        """
        return self.new(sorted(self))

    def __add__(self, other):
        if type(self) == type(other):
            return self.new(tuple(self)+tuple(other))

        else:
            raise TypeError

    def __getitem__(self, key):
        value = super(CombinationalPuzzle, self).__getitem__(key)
        if isinstance(key, int):
            return value
        elif isinstance(key, slice):
            return self.new(value)
        else:
            raise IndexError

    def __repr__(self):
        return "%s(%s)"%(type(self).__name__, str(list(self)))

    def __str__(self):
        return str(list(self))

    def __hash__(self):
        return hash((type(self), tuple(self)))

class CombinationalOperation(Operation, tuple):
    """
    operation that operate elements of combinational puzzle seperatly.
    element of operation is action.
    """
    def transform(self, pzl):
        pzl = pzl.new(map(self.elem_transform, pzl, self))
        if not pzl.ordered:
            pzl = pzl.sort()
        return pzl

    def elem_transform(self, elem, act):
        """
        transform element `elem` by action `act`.
        """
        raise NotImplementedError

    def __add__(self, other):
        if type(self) == type(other):
            return self.new(tuple(self)+tuple(other))

        else:
            raise TypeError

    def __getitem__(self, key):
        value = super(CombinationalOperation, self).__getitem__(key)
        if isinstance(key, int):
            return value
        elif isinstance(key, slice):
            return self.new(value)
        else:
            raise IndexError

    def __repr__(self):
        return "%s(%s)"%(type(self).__name__, str(list(self)))

    def __str__(self):
        return str(list(self))

class ContinuousCombinationalOperation(ContinuousOperation,
        CombinationalOperation):
    """
    continuous combinational operation.
    """
    def __init__(self, acts):
        diss = set(map(self.action_distance, self))
        if len(diss) != 1:
            raise ValueError
        else:
            self._distance = diss.pop()

    @property
    def distance(self):
        return self._distance

    def to(self, dis):
        if dis > self.distance:
            raise ValueError
        return self.new(self.action_to(act_i, dis) for act_i in self)

    def action_distance(self, act):
        """
        total distance of action `act`.
        """
        raise NotImplementedError

    def action_to(self, act, dis):
        """
        cut action `act` to distance `dis`.
        """
        raise NotImplementedError

class SelectiveOperation(WrappedOperation, tuple):
    """
    operation that operate different elements of combinational puzzle
    seperatly by selecting.
    the data structure of `SelectiveOperation` is sorted items of dictionary,
    where key is selection, value is action.
    """
    interpreted_type = CombinationalOperation

    def __new__(cls, *args, **kwargs):
        return tuple.__new__(cls, sorted(dict(*args, **kwargs).iteritems()))

    def interpret_for(self, pzl):
        interpreted = []
        for elem in pzl:
            for sel, act in self:
                if self.elem_filter(elem, sel):
                    interpreted.append(act)
                    break
            else:
                raise IllegalOperationError
        return self.interpreted_type(interpreted)

    def elem_filter(self, elem, sel):
        """
        True if element `elem` is in the selection `sel`.
        """
        raise NotImplementedError

    def keys(self):
        return list(item[0] for item in self)

    def values(self):
        return list(item[1] for item in self)

    def __repr__(self):
        return "%s(%s)"%(type(self).__name__, str(list(self)))

    def __str__(self):
        return "(%s)"%"; ".join("%s: %s"%(sel, act) for sel, act in self)

