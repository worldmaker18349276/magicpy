from itertools import product, combinations, groupby
from sympy.simplify import simplify
from symplus.strplus import mstr
from symplus.path import IdentityPath
from symplus.affine import SE3_star, SO3_star, T3_star
from symplus.euclid import T_RR3
from magicpy.solid.marching import cube_engine
from magicpy.puzzle.basic import *


class PhysicalPuzzle(CombinationalPuzzle):
    def is_valid_state(self):
        return all(self.is_valid_elem(elem) for elem in self) and self.engine.no_collision(self)

    def _is_valid_operation(self, op):
        if isinstance(op, PhysicalOperation):
            return (len(self) == len(op)
                and all(self.is_valid_action(action) for action in op))
        elif isinstance(op, PartitionalOperation):
            return (all(self.is_valid_action(action) for action in op.values())
                and all(self.is_valid_region(region) for region in op.keys())
                and self.engine.no_collision(op.keys()))
        else:
            return False

    def is_valid_elem(self, elem):
        return NotImplemented

    def is_valid_region(self, region):
        return NotImplemented

    def is_valid_action(self, action):
        return NotImplemented

    def elem_filter(self, elem, region):
        return self.engine.side_of(elem, region, err=True) == 1

    def _apply_cont_op(self, op):
        if isinstance(op, PhysicalOperation):
            return self._apply_phy_op(op)

        else:
            return NotImplemented

    def _apply_phy_op(self, phy_op):
        ops = []
        elems = []
        inds = sorted(range(len(phy_op)), key=lambda i: hash(phy_op[i]))
        for op_i, inds_i in groupby(inds, phy_op.__getitem__):
            ops.append(op_i)
            elems.append(self.engine.fuse(map(self.__getitem__, inds_i)))
        fused_op = type(phy_op)(ops)
        fused = type(self)(elems)

        for t in range(int(fused_op.distance*self.density)):
            moved = fused._transform_by(fused_op.to(t/self.density))
            if not moved.is_valid_state():
                raise IllegalStateError

        moved = fused._transform_by(fused_op)
        if not moved.is_valid_state():
            raise IllegalStateError

        return self._transform_by(phy_op)

    def elem_transform_by(self, elem, action):
        if isinstance(action, IdentityPath):
            return elem
        else:
            return self.engine.transform(elem, action.call())

    def cross_common(self, cols):
        return self.engine.cross_common([self]+list(cols))

    def fuse(self, glues=None, remain=True, err=False):
        return self.engine.fuse(self, glues=glues, remain=remain, err=err)

    def partition_by(self, *objs):
        return self.engine.partition_by(self, *objs)

    def simplify(self):
        return self.engine.simplify(self)


class PhysicalOperation(ContinuousCombinationalOperation):
    pass

class PartitionalOperation(SelectiveOperation):
    comb_type = PhysicalOperation


class SymbolicPhysicalPuzzle(PhysicalPuzzle):
    def is_valid_elem(self, elem):
        return simplify(self.states.contains(elem)) == True

    def is_valid_region(self, region):
        return simplify(self.states.contains(region)) == True

    def is_valid_action(self, action):
        return simplify(self.actions.contains(action)) == True

    def __str__(self):
        elemstr = ',\n     '.join(map(mstr, self))
        return '%s(\n    [%s])'%(type(self).__name__, elemstr)

class SymbolicSE3PhysicalPuzzle(SymbolicPhysicalPuzzle):
    engine = cube_engine()
    actions = SE3_star
    states = T_RR3

class SymbolicSO3PhysicalPuzzle(SymbolicPhysicalPuzzle):
    engine = cube_engine()
    actions = SO3_star
    states = T_RR3

class SymbolicT3PhysicalPuzzle(SymbolicPhysicalPuzzle):
    engine = cube_engine()
    actions = T3_star
    states = T_RR3


class SymbolicPhysicalOperation(PhysicalOperation):
    def action_distance(self, act):
        return act.length

    def action_to(self, act, dis):
        return act[:dis]

class SymbolicPartitionalOperation(PartitionalOperation):
    comb_type = SymbolicPhysicalOperation

