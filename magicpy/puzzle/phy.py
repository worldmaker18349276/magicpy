from itertools import product, combinations, groupby
from sympy.simplify import simplify
from symplus.strplus import mstr
from symplus.path import Path, IdentityPath
from symplus.affine import SE3_star, SO3_star, T3_star
from symplus.euclid import T_RR3
from magicpy.solid.marching import cube_engine
from magicpy.solid.sym import SymbolicSolidEngineVolumeAlgo
from magicpy.puzzle.basic import *


class PhysicalPuzzle(CombinationalPuzzle):
    def is_valid_state(self):
        return (all(map(self.is_valid_elem, self)) and
                self.engine.no_collision(self))

    def is_valid_operation(self, op):
        return (isinstance(op, PhysicalOperation) and
                len(self) == len(op) and
                all(map(self.is_valid_action, op)))

    def cross_common(self, cols):
        return self.new(self.engine.cross_common([self]+list(cols)))

    def partial_fuse(self, glues=None, remain=True, err=False):
        return self.new(self.engine.partial_fuse(self, glues=glues,
                                                       remain=remain,
                                                       err=err))

    def partition_by(self, *objs):
        return self.new(self.engine.partition_by(self, *objs))


class PhysicalOperation(ContinuousCombinationalOperation):
    def apply(self, pzl):
        if not pzl.is_valid_operation(self):
            raise IllegalOperationError

        ops = []
        elems = []
        inds = sorted(range(len(self)), key=lambda i: hash(self[i]))
        for op_i, inds_i in groupby(inds, self.__getitem__):
            ops.append(op_i)
            elems.append(pzl.engine.fuse(map(pzl.__getitem__, inds_i)))
        fused_op = self.new(ops)
        fused_pzl = pzl.new(elems)

        for t in range(int(fused_op.distance*fused_op.density)+1):
            moved = fused_op.to(t/fused_op.density).transform(fused_pzl)
            if not moved.is_valid_state():
                raise IllegalOperationError

        pzl = self.transform(pzl)
        if not pzl.is_valid_state():
            raise IllegalStateError

        return pzl

class PartitionalOperation(SelectiveOperation):
    interpreted_type = PhysicalOperation


sym_engine = SymbolicSolidEngineVolumeAlgo(cube_engine())

class SymbolicPhysicalPuzzle(PhysicalPuzzle):
    def __new__(cls, elems, states=T_RR3, actions=SE3_star):
        self = PhysicalPuzzle.__new__(cls, elems)
        self.states = states
        self.actions = actions
        return self

    def new(self, elems, states=None, actions=None):
        states = states if states is not None else self.states
        actions = actions if actions is not None else self.actions
        return type(self)(elems, states, actions)

    @property
    def engine(self):
        return sym_engine

    def is_valid_elem(self, elem):
        return simplify(self.states.is_regular_closed_set(elem)) == True

    def is_valid_action(self, action):
        return simplify(self.actions.contains(action)) == True

    def simplify(self):
        return self.new(self.engine.simplify(self))

    def __str__(self):
        elemstr = ',\n     '.join(map(mstr, self))
        return '%s(\n    [%s],\n    %s, %s)'%(type(self).__name__,
                                              elemstr,
                                              mstr(self.states),
                                              mstr(self.actions))

    def __repr__(self):
        return self.__str__()

class SymbolicPhysicalOperation(PhysicalOperation):
    @property
    def engine(self):
        return sym_engine

    def action_distance(self, act):
        return act.length

    def action_to(self, act, dis):
        return act[:dis]

    def elem_transform(self, elem, action):
        if isinstance(action, IdentityPath):
            return elem
        else:
            return self.engine.transform(elem, action.call())

class SymbolicPartitionalOperation(PartitionalOperation):
    interpreted_type = SymbolicPhysicalOperation

    @property
    def engine(self):
        return sym_engine

    def elem_filter(self, elem, region):
        return self.engine.side_of(elem, region, err=True) == 1

