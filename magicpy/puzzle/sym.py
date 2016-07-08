from sympy.simplify import simplify
from symplus.strplus import mstr
from magicpy.engine.marching import cube_engine
from magicpy.model.affine import SE3_star, SO3_star, T3_star
from magicpy.model.euclid import T_RR3
from magicpy.abstract.phy import *


class SymbolicPhysicalPuzzle(PhysicalPuzzle):
    def simp(self):
        simplified = []
        for elem in self:
            elem = self.elem_simp(elem)
            if elem is not None:
                simplified.append(elem)
        return type(self)(simplified)


    def is_valid_elem(self, elem):
        return simplify(self.states.contains(elem)) == True

    def is_valid_region(self, region):
        return simplify(self.states.contains(region)) == True

    def is_valid_action(self, action):
        return simplify(self.actions.contains(action)) == True

    def elem_transform_by(self, elem, action):
        return self.engine.transform_by(elem, action)

    def elem_is_subset(self, elem1, elem2):
        return self.engine.is_subset(elem1, elem2)

    def elem_is_disjoint(self, elem1, elem2):
        return self.engine.is_disjoint(elem1, elem2)

    def elem_intersection(self, *elems):
        return self.engine.intersection(*elems)

    def elem_union(self, *elems):
        return self.engine.union(*elems)

    def elem_simp(self, elem):
        return self.engine.simp(elem)

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
    def __init__(self, actions):
        if len(set(len(action) for action in actions)) > 1:
            raise ValueError

    @property
    def distance(self):
        return len(self[0])

    def to(self, index):
        if index > self.distance:
            raise ValueError
        return type(self)(action[:index] for action in self)

class SymbolicPartitionalOperation(PartitionalOperation):
    comb_type = SymbolicPhysicalOperation

