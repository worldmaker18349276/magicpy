

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
        return False

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
        return NotImplemented

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
    pass


class GeneralPuzzle(Puzzle):
    density = 10

    def _transform_by(self, op):
        if isinstance(op, ConditionalOperation):
            return self.transform_by(self.cond_op_to_op(op))

        else:
            return NotImplemented

    def cond_op_to_op(self, cond_op):
        for cond, op_i in cond_op.items():
            if self._filter(cond):
                return op_i
        else:
            raise IllegalOperationError

    def _filter(self, cond):
        return NotImplemented

    def _apply(self, op):
        if isinstance(op, ContinuousConditionalOperation):
            return self.cont_apply(self.cond_op_to_op(op))

        elif isinstance(op, ContinuousOperation):
            return self.cont_apply(op)

        else:
            return NotImplemented

    def cont_apply(self, op):
        for t in range(int(op.distance*self.density)):
            moved = self._transform_by(op.to(t/self.density))
            if not moved.is_valid_state():
                raise IllegalStateError

        self = self._transform_by(op)
        if not self.is_valid_state():
            raise IllegalStateError

        return self

class ConditionalOperation(Operation, dict):
    pass

class ContinuousOperation(Operation):
    def distance(self):
        return NotImplemented

    def to(self, index):
        return NotImplemented

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

class ContinuousConditionalOperation(ContinuousOperation, ConditionalOperation):
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
    def _transform_by(self, op):
        if isinstance(op, SelectiveOperation):
            return self._transform_by_comb(self.sel_op_to_comb_op(op))

        elif isinstance(op, CombinationalOperation):
            return self._transform_by_comb(op)

        else:
            return TypeError

    def _transform_by_comb(self, op):
        return type(self)(self.elem_transform_by(elem, action) for elem, action in zip(self, op))

    def elem_transform_by(self, elem, action):
        return NotImplemented

    def sel_op_to_comb_op(self, op):
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
        return NotImplemented

    def _apply(self, op):
        if isinstance(op, ContinuousCombinationalOperation):
            return self.cont_apply(self.sel_op_to_comb_op(op))

        elif isinstance(op, ContinuousOperation):
            return self.cont_apply(op)

        else:
            return NotImplemented

class CombinationalOperation(Operation, tuple):
    pass

class SelectiveOperation(Operation, dict):
    comb_type = CombinationalOperation

class ContinuousCombinationalOperation(ContinuousOperation, CombinationalOperation):
    pass

class ContinuousSelectiveOperation(ContinuousOperation, SelectiveOperation):
    comb_type = ContinuousCombinationalOperation


class PhysicalPuzzle(CombinationalPuzzle):
    def is_valid_state(self):
        return all(self.is_valid_elem(elem) for elem in self) and self.no_collision()

    def _is_valid_operation(self, op):
        if isinstance(op, PhysicalOperation):
            return (len(self) == len(op)
                and all(self.is_valid_action(action) for action in op))
        elif isinstance(op, PartitionalOperation):
            return (all(self.is_valid_action(action) for action in op.values())
                and all(self.is_valid_region(region) for region in op.keys())
                and type(self)(op.keys()).no_collision())
        else:
            return False

    def is_valid_elem(self, elem):
        return NotImplemented

    def is_valid_region(self, region):
        return NotImplemented

    def is_valid_action(self, action):
        return NotImplemented

    def elem_filter(self, elem, region):
        return self.elem_is_subset(elem, region)

    def no_collision(self):
        for elem1, elem2 in combinations(self, 2):
            if not self.elem_is_disjoint(elem1, elem2):
                return False
        return True

    def no_collision_with(self, other):
        for elem1, elem2 in product(self, other):
            if not self.elem_is_disjoint(elem1, elem2):
                return False
        return True

    def cut_by(self, *knives):
        cutted = []
        for sub in product(self, *knives):
            cutted.append(self.elem_intersection(*sub))
        return type(self)(cutted)

    def fuse(self, *ind, region=None):
        if len(ind) == 0:
            ind = [i for i in range(len(self)) if self.elem_filter(self[i], region)]
        selected = [self[i] for i in ind]
        others = [self[i] for i in range(len(self)) if i not in ind]
        return type(self)(others+[self.elem_union(*selected)])

    def elem_transform_by(self, elem, action):
        return NotImplemented

    def elem_is_subset(self, elem1, elem2):
        return NotImplemented

    def elem_is_disjoint(self, elem1, elem2):
        return NotImplemented

    def elem_intersection(self, *elems):
        return NotImplemented

    def elem_union(self, *elems):
        return NotImplemented

class PhysicalOperation(ContinuousCombinationalOperation):
    pass

class PartitionalOperation(ContinuousSelectiveOperation):
    comb_type = PhysicalOperation

