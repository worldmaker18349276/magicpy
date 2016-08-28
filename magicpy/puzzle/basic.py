"""
control method:
+-[apply]------------------------------------+
|+-[transform_by]---+                        |
||+-[interpret]----+|                        |
||| (deal with     ||                        |
|||  monoid-       ||                        |
|||  structured    ||                        |
|||  operation)    ||                        |
|||     ||         ||                        |
|||     \/         ||                        |
||| [_interpret]   ||                        |
||+---- || --------+|                        |
||      || <========== <_is_valid_operation> |
||+---- \/ -----------[_apply]-----------+   |
||| [_transform_by] |                    |   |
|||     || <========== <_is_valid_state> |   |
||+-----||-------------------------------+   |
|+------||----------+                        |
+-------\/-----------------------------------+
"""


class IllegalOperationError(Exception):
    pass

class IllegalStateError(Exception):
    pass



class Puzzle:
    """
    basic class of all puzzles.
    it define control method for puzzle,
    and only implement the procedure for dealing with monoid-structured operation.
    """
    def is_valid_state(self):
        """
        True if this puzzle is in the valid state.
        """
        return True

    def is_valid_operation(self, op):
        """
        True if op is in the valid operation for this puzzle.
        it should be true if op is appliable for this puzzle.
        but the inverse is not neccessary to be true; this is just a type test.
        this method implement the procedure for dealing with monoid-structured operation.
        """
        if isinstance(op, IdentityOperation):
            return True

        elif isinstance(op, ConcatenatedOperation):
            return all(self.is_valid_operation(op_i) for op_i in op.operations)

        elif isinstance(op, Operation):
            return self._is_valid_operation(self._interpret(op))

        else:
            return False

    def _is_valid_operation(self, op):
        """
        True if op is valid operation for this puzzle.
        this is for elementary operation.
        """
        return False

    def interpret(self, op):
        """
        interpret operation as exact operation, except for monoid-structured operations.
        interpretation may depand on state of puzzle.
        this method implement the procedure for dealing with monoid-structured operation.
        """
        if isinstance(op, (IdentityOperation, ConcatenatedOperation)):
            return op

        elif isinstance(op, Operation):
            return self._interpret(op)

        else:
            raise TypeError

    def _interpret(self, op):
        """
        interpret operation as exact operation.
        this is for elementary operation.
        """
        return op

    def transform_by(self, op):
        """
        transform this puzzle by operation op.
        op is not neccessary to be valid operation.
        this method implement the procedure for dealing with monoid-structured operation.
        """
        if isinstance(op, IdentityOperation):
            return self

        elif isinstance(op, ConcatenatedOperation):
            for op_i in op.operations:
                self = self.transform_by(op_i)
            return self

        elif isinstance(op, Operation):
            return self._transform_by(self._interpret(op))

        else:
            raise TypeError

    def _transform_by(self, op):
        """
        transform this puzzle by operation op.
        this is for elementary operation.
        """
        return NotImplemented

    def apply(self, op):
        """
        apply op to this puzzle.
        before applying, op should be valid operation;
        after applying, this puzzle should be in the valid state.
        this method implement the procedure for dealing with monoid-structured operation.
        """
        if isinstance(op, IdentityOperation):
            return self

        elif isinstance(op, ConcatenatedOperation):
            for op_i in op.operations:
                self = self.apply(op_i)
            return self

        elif isinstance(op, Operation):
            op = self._interpret(op)
            if not self._is_valid_operation(op):
                raise IllegalOperationError
            return self._apply(op)

        else:
            raise TypeError

    def _apply(self, op):
        """
        apply op to this puzzle.
        this is for elementary operation.
        """
        self = self._transform_by(op)

        if not self.is_valid_state():
            raise IllegalStateError

        return self

class Operation:
    """
    basic class of all operations.
    """
    def __mul__(self, other):
        return ConcatenatedOperation(self, other)

class IdentityOperation(Operation):
    """
    operation that do nothing.
    IdentityOperation is monoid-structured operation.
    """
    def __repr__(self):
        return "%s()"%type(self).__name__

    def __str__(self):
        return "Id"

class ConcatenatedOperation(Operation):
    """
    operation which apply operations sequentially.
    ConcatenatedOperation is monoid-structured operation.
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

    def reduce(ops):
        i = 0
        while i < len(ops):
            if isinstance(ops[i], IdentityOperation):
                ops = ops[:i] + ops[i+1:]

            elif isinstance(ops[i], ConcatenatedOperation):
                ops = ops[:i] + ops[i].operations + ops[i+1:]

            elif i > 0 and hasattr(ops[i-1], '_concat'):
                op_i = ops[i-1]._concat(ops[i])
                if op_i is not None:
                    ops = ops[:i-1] + [op_i] + ops[i+1:]
                else:
                    i = i + 1

            else:
                i = i + 1

        return ops

    def __len__(self):
        return len(self.operations)

    def __getitem__(self, key):
        if isinstance(key, int):
            return self.operations[key]
        elif isinstance(key, slice):
            return type(self)(*self.operations[key])
        else:
            raise IndexError

    def __repr__(self):
        return "%s%s"%(type(self).__name__, str(self.operations))

    def __str__(self):
        return "*".join(map(str, self.operations))


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
        return all(pzl_i.is_valid_state() for pzl_i in self)

    def _is_valid_operation(self, op):
        if isinstance(op, TensorOperation):
            return (len(self) == len(op) and
                all(pzl_i.is_valid_operation(op_i) for pzl_i, op_i in zip(self, op)))

        else:
            return NotImplemented

    def _interpret(self, op):
        if isinstance(op, TensorOperation):
            return TensorOperation(pzl_i.interpret(op_i) for pzl_i, op_i in zip(self, op))

        else:
            return NotImplemented

    def _transform_by(self, op):
        if isinstance(op, TensorOperation):
            return type(self)(pzl_i.transform_by(op_i) for pzl_i, op_i in zip(self, op))

        else:
            return NotImplemented

    def __add__(self, other):
        if type(self) == type(other):
            return type(self)(tuple(self)+tuple(other))

        else:
            raise TypeError

    def __getitem__(self, key):
        if isinstance(key, int):
            return super(TensorPuzzle, self).__getitem__[key]
        elif isinstance(key, slice):
            return type(self)(super(TensorPuzzle, self).__getitem__[key])
        else:
            raise IndexError

    def __repr__(self):
        return "%s(%s)"%(type(self).__name__, str(self))

    def __str__(self):
        return super(tuple, self).__str__()

    def __hash__(self):
        return hash((type(self), super(tuple, self).__hash__()))

class TensorOperation(Operation, tuple):
    """
    tensor of operations for TensorPuzzle.
    """
    def __add__(self, other):
        if type(self) == type(other):
            return type(self)(tuple(self)+tuple(other))

        else:
            raise TypeError

    def __getitem__(self, key):
        if isinstance(key, int):
            return super(TensorOperation, self).__getitem__[key]
        elif isinstance(key, slice):
            return type(self)(super(TensorOperation, self).__getitem__[key])
        else:
            raise IndexError

    def __repr__(self):
        return "%s(%s)"%(type(self).__name__, str(self))

    def __str__(self):
        return super(tuple, self).__str__()


class GeneralPuzzle(Puzzle):
    """
    define some useful operation: ConditionalOperation, ContinuousOperation.
    """
    density = 10

    def _interpret(self, op):
        if isinstance(op, ConditionalOperation):
            return _interpret_cond_op(self, op)

        else:
            return NotImplemented

    def _interpret_cond_op(self, cond_op):
        """
        interpret ConditionalOperation to Operation.
        """
        for cond, op_i in cond_op.items():
            if self._filter(cond):
                return op_i
        else:
            raise IllegalOperationError

    def _filter(self, cond):
        """
        True if this puzzle is in the condition cond.
        """
        return NotImplemented

    def _apply(self, op):
        if isinstance(op, ContinuousOperation):
            return self._apply_cont_op(op)

        else:
            return NotImplemented

    def _apply_cont_op(self, op):
        """
        continuously apply op to this puzzle.
        """
        for t in range(int(op.distance*self.density)):
            moved = self._transform_by(op.to(t/self.density))
            if not moved.is_valid_state():
                raise IllegalStateError

        self = self._transform_by(op)
        if not self.is_valid_state():
            raise IllegalStateError

        return self

class ConditionalOperation(Operation, dict):
    """
    operation which operate case by case.
    key is condition, value is elementary operation.
    """
    def __repr__(self):
        return "%s(%s)"%(type(self).__name__, dict.__str__(self))

    def __str__(self):
        return "(%s)"%"; ".join("%s: %s"%(cond, op_i) for cond, op_i in self.items())

class ContinuousOperation(Operation):
    """
    operation which operate continuously.
    operation can be cutted to any distance.
    """
    @property
    def distance(self):
        """
        total distance of this operation.
        """
        raise NotImplementedError

    def to(self, dis):
        """
        cut this operation to distance dis.
        """
        return NotImplemented

class ParallelOperation(ContinuousOperation, TensorOperation):
    """
    continuous tensor operation.
    operations are parallelly operate on the puzzle.
    """
    def __new__(cls, ops):
        ops = tuple(ops)
        if not all(isinstance(op_i, ContinuousOperation) for op_i in ops):
            raise TypeError
        if len(set(op_i.distance for op_i in ops)) != 1:
            raise ValueError
        return TensorOperation.__new__(cls, ops)

    @property
    def distance(self):
        return self[0].distance

    def to(self, dis):
        if dis > self.distance:
            raise ValueError
        return type(self)(op_i.to(dis) for op_i in self)


class CombinationalPuzzle(GeneralPuzzle, tuple):
    """
    puzzle composed by multiple elements.
    """
    ordered = True

    def transform_by(self, op):
        if not self.ordered:
            return super(CombinationalPuzzle, self).transform_by(self, op).sort()
        else:
            return super(CombinationalPuzzle, self).transform_by(self, op)

    def apply(self, op):
        if not self.ordered:
            return super(CombinationalPuzzle, self).apply(op).sort()
        else:
            return super(CombinationalPuzzle, self).apply(op)

    def sort(self):
        return type(self)(sorted(self))

    def _interpret(self, op):
        if isinstance(op, SelectiveOperation):
            return self._interpret_sel_op(op)

        else:
            return NotImplemented

    def _interpret_sel_op(self, sel_op):
        """
        interpret SelectiveOperation to CombinationalOperation.
        """
        comb_op = []
        for elem in self:
            for sel, act in sel_op.items():
                if self.elem_filter(elem, sel):
                    comb_op.append(act)
                    break
            else:
                raise IllegalOperationError
        return sel_op.comb_type(comb_op)

    def elem_filter(self, elem, sel):
        """
        True if elem is in the selection sel.
        """
        return NotImplemented

    def _transform_by(self, op):
        if isinstance(op, CombinationalOperation):
            return self._transform_by_comb_op(op)

        else:
            return NotImplemented

    def _transform_by_comb_op(self, comb_op):
        """
        transform this puzzle by combinational operation comb_op.
        """
        return type(self)(self.elem_transform_by(elem, act) for elem, act in zip(self, comb_op))

    def elem_transform_by(self, elem, act):
        """
        transform elements of this puzzle elem by action act.
        """
        return NotImplemented

    def __add__(self, other):
        if type(self) == type(other):
            return type(self)(tuple(self)+tuple(other))

        else:
            raise TypeError

    def __getitem__(self, key):
        if isinstance(key, int):
            return super(CombinationalPuzzle, self).__getitem__(key)
        elif isinstance(key, slice):
            return type(self)(super(CombinationalPuzzle, self).__getitem__(key))
        else:
            raise IndexError

    def __repr__(self):
        return "%s(%s)"%(type(self).__name__, str(list(self)))

    def __str__(self):
        return str(list(self))

    def __hash__(self):
        return hash((type(self), super(tuple, self).__hash__()))

class CombinationalOperation(Operation, tuple):
    """
    operation that operate elements of combinational puzzle seperatly.
    element of operation is action.
    """
    def __add__(self, other):
        if type(self) == type(other):
            return type(self)(tuple(self)+tuple(other))

        else:
            raise TypeError

    def __getitem__(self, key):
        if isinstance(key, int):
            return super(CombinationalOperation, self).__getitem__(key)
        elif isinstance(key, slice):
            return type(self)(super(CombinationalOperation, self).__getitem__(key))
        else:
            raise IndexError

    def __repr__(self):
        return "%s(%s)"%(type(self).__name__, str(list(self)))

    def __str__(self):
        return str(list(self))


class ContinuousCombinationalOperation(ContinuousOperation, CombinationalOperation):
    """
    continuous combinational operation.
    """
    def __init__(self, acts):
        diss = set(self.action_distance(act_i) for act_i in self)
        if len(diss) != 1:
            raise ValueError
        else:
            self._distance = tuple(diss)[0]

    @property
    def distance(self):
        return self._distance

    def action_distance(self, act):
        return NotImplemented

    def to(self, dis):
        if dis > self.distance:
            raise ValueError
        return type(self)(self.action_to(act_i, dis) for act_i in self)

    def action_to(self, act, dis):
        return NotImplemented

class SelectiveOperation(Operation, dict):
    """
    operation that operate different elements of combinational puzzle seperatly by selecting.
    key is selection, value is action.
    """
    comb_type = CombinationalOperation

    def __repr__(self):
        return "%s(%s)"%(type(self).__name__, dict.__str__(self))

    def __str__(self):
        return "(%s)"%"; ".join("%s: %s"%(sel, act) for sel, act in self.items())

