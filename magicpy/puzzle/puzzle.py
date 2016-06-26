


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
        raise NotImplementedError
        # # for ElementaryOperation
        # if not self.is_valid_operation(op):
        #     raise IllegalOperationError

        # self = self.transform_by(op)

        # if not self.is_valid_state():
        #     raise IllegalStateError

        # return self

class Operation:
    def _concat(self, other):
        return None

    def __add__(self, other):
        return ConcatenatedOperation(self, other)

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

