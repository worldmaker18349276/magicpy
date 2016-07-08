from magicpy.abstract.puzzles import *
from itertools import product, combinations


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

