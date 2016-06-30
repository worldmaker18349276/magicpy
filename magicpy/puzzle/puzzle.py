


class IllegalOperationError(Exception):
    pass

class IllegalStateError(Exception):
    pass



class Puzzle:
    def is_valid_state(self):
        return True

    def is_valid_operation(self, op):
        if isinstance(op, IdentityOperation):
            return True

        elif isinstance(op, ConcatenatedOperation):
            return all(self.is_valid_operation(op_i) for op_i in op.operations)

        elif isinstance(op, Operation):
            return self._is_valid_operation(op)

        else:
            return False

    def _is_valid_operation(self, op):
        return True

    def transform_by(self, op):
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
        raise NotImplementedError

    def apply(self, op):
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
        self = self._transform_by(op)

        if not self.is_valid_state():
            raise IllegalStateError

        return self


class TensorPuzzle(Puzzle, tuple):
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


class ContinuousPuzzle(Puzzle):
    density = 10

    def _apply(self, op):
        if isinstance(op, ContinuousOperation):
            return self._apply_cont(op)

        else:
            return Puzzle._apply(self, op)

    def _apply_cont(self, op):
        for t in range(int(op.distance*density)):
            moved = self._transform_by(op.to(t/density))
            if not moved.is_valid_state():
                raise IllegalStateError

        self = self._transform_by(op.to(op.distance))
        if not self.is_valid_state():
            raise IllegalStateError

        return self


class ContinuousTensorPuzzle(ContinuousPuzzle, TensorPuzzle):
    def __new__(cls, pzls):
        if not all(isinstance(pzl_i, ContinuousPuzzle) for pzl_i in pzls):
            raise TypeError
        return TensorPuzzle.__new__(cls, pzls)


class CombinationalPuzzle(Puzzle, tuple):
    def _is_valid_operation(self, op):
        if isinstance(op, CombinationalOperation):
            return (len(self) == len(op) and
                all(self._is_valid_operation_elem(elem, action) for elem, action in zip(self, op)))
        elif isinstance(op, PartitionalOperation):
            return True
        else:
            return False

    def _is_valid_operation_elem(self, elem, action):
        raise NotImplementedError

    def _transform_by(self, op):
        if isinstance(op, CombinationalOperation):
            return self._transform_by_comb(op)

        elif isinstance(op, PartitionalOperation):
            return self._transform_by_comb(self._to_comb_op(op))

        else:
            raise NotImplementedError

    def _transform_by_comb(self, op):
        return type(self)(self._transform_by_elem(elem, action) for elem, action in zip(self, op))

    def _transform_by_elem(self, elem, action):
        raise NotImplementedError

    def _to_comb_op(self, op):
        comb_op = []
        for elem in self:
            for part, action in op.items():
                if self._filter_elem(elem, part):
                    comb_op.append(action)
                    break
            else:
                raise IllegalOperationError
        return op.comb_type(comb_op)

    def _filter_elem(self, elem, part):
        raise NotImplementedError


class UnorderedCombinationalPuzzle(CombinationalPuzzle):
    def transform_by(self, op):
        self = CombinationalPuzzle.transform_by(self, op)
        return self._sort()

    def apply(self, op):
        self = CombinationalPuzzle.apply(self, op)
        return self._sort()

    def _sort(self):
        return type(self)(sorted(self, key=hash))


class ContinuousCombinationalPuzzle(ContinuousPuzzle, CombinationalPuzzle):
    def _apply(self, op):
        if isinstance(op, ContinuousCombinationalOperation):
            return self._apply_cont(self._to_comb_op(op))

        elif isinstance(op, ContinuousOperation):
            return self._apply_cont(op)

        else:
            return CombinationalPuzzle._apply(self, op)


class ContinuousUnorderedCombinationalPuzzle(ContinuousCombinationalPuzzle, UnorderedCombinationalPuzzle):
    pass



class Operation:
    pass

class IdentityOperation(Operation):
    pass

class ConcatenatedOperation(Operation):
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

class TensorOperation(Operation, tuple):
    pass

class ContinuousOperation(Operation):
    @property
    def distance(self):
        raise NotImplementedError

    def to(self, index):
        raise NotImplementedError

class ContinuousIdentityOperation(ContinuousOperation, IdentityOperation):
    def __init__(self, dis):
        self.distance = dis

    def to(self, index):
        if index > self.distance:
            raise ValueError
        return ContinuousIdentityOperation(index)

class ParallelOperation(ContinuousOperation, TensorOperation):
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

class CombinationalOperation(Operation, tuple):
    pass

class PartitionalOperation(Operation, dict):
    comb_type = CombinationalOperation

class ContinuousCombinationalOperation(ContinuousOperation, CombinationalOperation):
    pass

class ContinuousPartitionalOperation(ContinuousOperation, PartitionalOperation):
    comb_type = ContinuousCombinationalOperation

