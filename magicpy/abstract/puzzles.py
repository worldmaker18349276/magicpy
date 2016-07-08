

class IllegalOperationError(Exception):
    pass

class IllegalStateError(Exception):
    pass



class Puzzle:
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
        """
        if isinstance(op, IdentityOperation):
            return True

        elif isinstance(op, ConcatenatedOperation):
            return all(self.is_valid_operation(op_i) for op_i in op.operations)

        elif isinstance(op, Operation):
            return self._is_valid_operation(op)

        else:
            return False

    def _is_valid_operation(self, op):
        """
        True if op is valid operation for this puzzle.
        this is for elementary operation.
        """
        return False

    def transform_by(self, op):
        """
        transform this puzzle by operation op.
        op is not neccessary to be valid operation.
        """
        if isinstance(op, IdentityOperation):
            return self

        elif isinstance(op, ConcatenatedOperation):
            for op_i in op.operations:
                self = self.transform_by(op_i)
            return self

        elif isinstance(op, Operation):
            return self._transform_by(op)

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
        """
        if not self.is_valid_operation(op):
            raise IllegalOperationError

        if isinstance(op, IdentityOperation):
            return self

        elif isinstance(op, ConcatenatedOperation):
            for op_i in op.operations:
                self = self.apply(op_i)
            return self

        elif isinstance(op, Operation):
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
    operation.
    """
    pass

class IdentityOperation(Operation):
    """
    operation which do nothing.
    """
    pass

class ConcatenatedOperation(Operation):
    """
    operation which apply specific operations sequentially.
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
            return ConcatenatedOperation(*self.operations[key])
        else:
            raise IndexError


class TensorPuzzle(Puzzle, tuple):
    """
    tensor of multiple puzzles.
    """
    def __new__(cls, pzls):
        if not all(isinstance(pzl_i, Puzzle) for pzl_i in pzls):
            raise TypeError
        return tuple.__new__(cls, pzls)

    def is_valid_state(self):
        return all(pzl_i.is_valid_state() for pzl_i in self)

    def _is_valid_operation(self, op):
        return (isinstance(op, TensorOperation) and len(self) == len(op) and
                all(pzl_i.is_valid_operation(op_i) for pzl_i, op_i in zip(self, op)))

    def _transform_by(self, op):
        return type(self)(pzl_i.transform_by(op_i) for pzl_i, op_i in zip(self, op))

class TensorOperation(Operation, tuple):
    """
    tensor of multiple operation for TensorPuzzle.
    """
    pass


class GeneralPuzzle(Puzzle):
    """
    implement some useful operation: ConditionalOperation, ContinuousOperation.
    """
    density = 10

    def _transform_by(self, op):
        if isinstance(op, ConditionalOperation):
            return self.transform_by(self.cond_op_to_op(op))

        else:
            return NotImplemented

    def cond_op_to_op(self, cond_op):
        """
        convert ConditionalOperation to Operation.
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
        if isinstance(op, ContinuousConditionalOperation):
            return self.cont_apply(self.cond_op_to_op(op))

        elif isinstance(op, ContinuousOperation):
            return self.cont_apply(op)

        else:
            return NotImplemented

    def cont_apply(self, op):
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
    key is condition, value is Operation.
    """
    pass

class ContinuousOperation(Operation):
    """
    operation which operate continuously.
    operation can be sliced to any distance.
    """
    @property
    def distance(self):
        """
        total distance of this operation.
        """
        raise NotImplementedError

    def to(self, dis):
        """
        slice this operation by dis.
        """
        return NotImplemented

class ContinuousIdentityOperation(ContinuousOperation, IdentityOperation):
    """
    identity operation with distance.
    this is for helping to compose ParallelOperation/ContinuousConditionalOperation in some case.
    """
    def __init__(self, dis):
        self.distance = dis

    def to(self, dis):
        if dis > self.distance:
            raise ValueError
        return ContinuousIdentityOperation(dis)

class ParallelOperation(ContinuousOperation, TensorOperation):
    """
    continuous tensor operation.
    """
    def __new__(cls, ops):
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

class ContinuousConditionalOperation(ContinuousOperation, ConditionalOperation):
    """
    continuous conditional operation.
    """
    def __new__(cls, ops):
        if not all(isinstance(op_i, ContinuousOperation) for op_i in ops.values()):
            raise TypeError
        if len(set(op_i.distance for op_i in ops.values())) != 1:
            raise ValueError
        return ConditionalOperation.__new__(cls, ops)

    @property
    def distance(self):
        return tuple(self.values())[0].distance

    def to(self, dis):
        if dis > self.distance:
            raise ValueError
        return type(self)(dict((cond, op_i.to(dis)) for cond, op_i in self.items()))


class CombinationalPuzzle(GeneralPuzzle, tuple):
    """
    puzzle composed by multiple elements.
    """
    def _transform_by(self, op):
        if isinstance(op, SelectiveOperation):
            return self._transform_by_comb(self.sel_op_to_comb_op(op))

        elif isinstance(op, CombinationalOperation):
            return self._transform_by_comb(op)

        else:
            return TypeError

    def _transform_by_comb(self, op):
        """
        transform this puzzle by combinational operation op.
        """
        return type(self)(self.elem_transform_by(elem, action) for elem, action in zip(self, op))

    def elem_transform_by(self, elem, action):
        """
        transform elements of this puzzle elem by action.
        """
        return NotImplemented

    def sel_op_to_comb_op(self, op):
        """
        convert SelectiveOperation to CombinationalOperation.
        """
        comb_op = []
        for elem in self:
            for select, action in op.items():
                if self.elem_filter(elem, select):
                    comb_op.append(action)
                    break
            else:
                raise IllegalOperationError
        return op.comb_type(comb_op)

    def elem_filter(self, elem, select):
        """
        True if elem is in the selection select.
        """
        return NotImplemented

    def _apply(self, op):
        if isinstance(op, ContinuousSelectiveOperation):
            return self.cont_apply(self.sel_op_to_comb_op(op))

        elif isinstance(op, ContinuousOperation):
            return self.cont_apply(op)

        else:
            return NotImplemented

class CombinationalOperation(Operation, tuple):
    """
    operation that operate elements of combinational puzzle seperatly.
    element of operation is action.
    """
    pass

class SelectiveOperation(Operation, dict):
    """
    operation that operate selected elements of combinational puzzle.
    key is selection, value is action.
    """
    comb_type = CombinationalOperation

class ContinuousCombinationalOperation(ContinuousOperation, CombinationalOperation):
    """
    continuous combinational operation.
    """
    pass

class ContinuousSelectiveOperation(ContinuousOperation, SelectiveOperation):
    """
    continuous selective operation.
    """
    comb_type = ContinuousCombinationalOperation

