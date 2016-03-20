from itertools import combinations, product
from sympy.core import S, Lambda
from sympy.sets import Set
from sympy.simplify import simplify
from sympy.matrices import MatrixBase
from symplus.setplus import AbstractSet
from symplus.topoplus import NaturalTopology
from symplus.strplus import mstr
from symplus.pathplus import PathMonoid, Path
from magicpy.engine.marching import cube_engine
from magicpy.model.affine import SE3, SO3, T3, transform
from magicpy.model.euclid import EuclideanTopology


class TotalOperation:
    def __init__(self, action):
        self.action = action

class TargetedOperation:
    def __init__(self, target, action):
        self.target = target
        self.action = action

class RegionalOperation:
    def __init__(self, region, action):
        self.region = region
        self.action = action


class IllegalOperationError(Exception):
    pass

class IllegalStateError(Exception):
    pass


class PhysicalPuzzle(frozenset):
    def __new__(cls, elements):
        return frozenset.__new__(cls, elements)

    def is_valid_state(self):
        if any(elem not in self.states for elem in self):
            return False
        if not self.no_collision():
            return False
        return True

    def is_valid_operation(self, operation):
        if isinstance(operation, TotalOperation):
            return operation.action in self.actions
        elif isinstance(operation, TargetedOperation):
            return operation.action in self.actions and operation.target <= self
        elif isinstance(operation, RegionalOperation):
            return operation.action in self.actions and operation.region in self.states
        else:
            return False

    def cut_by(self, *knives):
        """
        >>> from symplus.matplus import *
        >>> from magicpy.model.euclid import *
        >>> cube2x2x2 = RotationalPhysicalPuzzle({Sphere()})
        >>> cube2x2x2 = cube2x2x2.cut_by(
        ...     (Halfspace(-i), Halfspace(i)),
        ...     (Halfspace(-j), Halfspace(j)),
        ...     (Halfspace(-k), Halfspace(k)))
        >>> print(str(cube2x2x2))
        RotationalPhysicalPuzzle(
            {(Halfspace([-1, 0, 0]', 0, False)) n (Halfspace([0, -1, 0]', 0, False)) n (Halfspace([0, 0, -1]', 0, False)) n (Sphere(1, [0, 0, 0]', False)),
             (Halfspace([-1, 0, 0]', 0, False)) n (Halfspace([0, -1, 0]', 0, False)) n (Halfspace([0, 0, 1]', 0, False)) n (Sphere(1, [0, 0, 0]', False)),
             (Halfspace([-1, 0, 0]', 0, False)) n (Halfspace([0, 0, -1]', 0, False)) n (Halfspace([0, 1, 0]', 0, False)) n (Sphere(1, [0, 0, 0]', False)),
             (Halfspace([-1, 0, 0]', 0, False)) n (Halfspace([0, 0, 1]', 0, False)) n (Halfspace([0, 1, 0]', 0, False)) n (Sphere(1, [0, 0, 0]', False)),
             (Halfspace([0, -1, 0]', 0, False)) n (Halfspace([0, 0, -1]', 0, False)) n (Halfspace([1, 0, 0]', 0, False)) n (Sphere(1, [0, 0, 0]', False)),
             (Halfspace([0, -1, 0]', 0, False)) n (Halfspace([0, 0, 1]', 0, False)) n (Halfspace([1, 0, 0]', 0, False)) n (Sphere(1, [0, 0, 0]', False)),
             (Halfspace([0, 0, -1]', 0, False)) n (Halfspace([0, 1, 0]', 0, False)) n (Halfspace([1, 0, 0]', 0, False)) n (Sphere(1, [0, 0, 0]', False)),
             (Halfspace([0, 0, 1]', 0, False)) n (Halfspace([0, 1, 0]', 0, False)) n (Halfspace([1, 0, 0]', 0, False)) n (Sphere(1, [0, 0, 0]', False))})
        """
        cutted = set()
        for sub in product(self, *knives):
            cutted.add(self.engine.intersection(*sub))
        return type(self)(cutted)

    def fuse(self, region=None):
        if region is None:
            return type(self)({self.engine.union(*self)})
        else:
            selected, others = self.select_by(region)
            return type(self)(others | selected.fuse())

    def simp(self):
        """
        >>> from sympy import *
        >>> from symplus.matplus import *
        >>> from magicpy.model.euclid import *
        >>> from magicpy.engine.marching import *
        >>> knives = Halfspace(i, 1), Halfspace(j, 1), Halfspace(-i, 1), Halfspace(-j, 1)
        >>> floppy3x3x1 = RotationalPhysicalPuzzle({Sphere(3)})
        >>> floppy3x3x1 = floppy3x3x1.cut_by(*map(with_exterior, knives))
        >>> print(str(floppy3x3x1))
        RotationalPhysicalPuzzle(
            {(Halfspace([-1, 0, 0]', -1, True)) n (Halfspace([-1, 0, 0]', 1, False)) n (Halfspace([0, -1, 0]', -1, True)) n (Halfspace([0, -1, 0]', 1, False)) n (Sphere(3, [0, 0, 0]', False)),
             (Halfspace([-1, 0, 0]', -1, True)) n (Halfspace([-1, 0, 0]', 1, False)) n (Halfspace([0, -1, 0]', -1, True)) n (Halfspace([0, 1, 0]', -1, True)) n (Sphere(3, [0, 0, 0]', False)),
             (Halfspace([-1, 0, 0]', -1, True)) n (Halfspace([-1, 0, 0]', 1, False)) n (Halfspace([0, -1, 0]', 1, False)) n (Halfspace([0, 1, 0]', 1, False)) n (Sphere(3, [0, 0, 0]', False)),
             (Halfspace([-1, 0, 0]', -1, True)) n (Halfspace([-1, 0, 0]', 1, False)) n (Halfspace([0, 1, 0]', -1, True)) n (Halfspace([0, 1, 0]', 1, False)) n (Sphere(3, [0, 0, 0]', False)),
             (Halfspace([-1, 0, 0]', -1, True)) n (Halfspace([0, -1, 0]', -1, True)) n (Halfspace([0, -1, 0]', 1, False)) n (Halfspace([1, 0, 0]', -1, True)) n (Sphere(3, [0, 0, 0]', False)),
             (Halfspace([-1, 0, 0]', -1, True)) n (Halfspace([0, -1, 0]', -1, True)) n (Halfspace([0, 1, 0]', -1, True)) n (Halfspace([1, 0, 0]', -1, True)) n (Sphere(3, [0, 0, 0]', False)),
             (Halfspace([-1, 0, 0]', -1, True)) n (Halfspace([0, -1, 0]', 1, False)) n (Halfspace([0, 1, 0]', 1, False)) n (Halfspace([1, 0, 0]', -1, True)) n (Sphere(3, [0, 0, 0]', False)),
             (Halfspace([-1, 0, 0]', -1, True)) n (Halfspace([0, 1, 0]', -1, True)) n (Halfspace([0, 1, 0]', 1, False)) n (Halfspace([1, 0, 0]', -1, True)) n (Sphere(3, [0, 0, 0]', False)),
             (Halfspace([-1, 0, 0]', 1, False)) n (Halfspace([0, -1, 0]', -1, True)) n (Halfspace([0, -1, 0]', 1, False)) n (Halfspace([1, 0, 0]', 1, False)) n (Sphere(3, [0, 0, 0]', False)),
             (Halfspace([-1, 0, 0]', 1, False)) n (Halfspace([0, -1, 0]', -1, True)) n (Halfspace([0, 1, 0]', -1, True)) n (Halfspace([1, 0, 0]', 1, False)) n (Sphere(3, [0, 0, 0]', False)),
             (Halfspace([-1, 0, 0]', 1, False)) n (Halfspace([0, -1, 0]', 1, False)) n (Halfspace([0, 1, 0]', 1, False)) n (Halfspace([1, 0, 0]', 1, False)) n (Sphere(3, [0, 0, 0]', False)),
             (Halfspace([-1, 0, 0]', 1, False)) n (Halfspace([0, 1, 0]', -1, True)) n (Halfspace([0, 1, 0]', 1, False)) n (Halfspace([1, 0, 0]', 1, False)) n (Sphere(3, [0, 0, 0]', False)),
             (Halfspace([0, -1, 0]', -1, True)) n (Halfspace([0, -1, 0]', 1, False)) n (Halfspace([1, 0, 0]', -1, True)) n (Halfspace([1, 0, 0]', 1, False)) n (Sphere(3, [0, 0, 0]', False)),
             (Halfspace([0, -1, 0]', -1, True)) n (Halfspace([0, 1, 0]', -1, True)) n (Halfspace([1, 0, 0]', -1, True)) n (Halfspace([1, 0, 0]', 1, False)) n (Sphere(3, [0, 0, 0]', False)),
             (Halfspace([0, -1, 0]', 1, False)) n (Halfspace([0, 1, 0]', 1, False)) n (Halfspace([1, 0, 0]', -1, True)) n (Halfspace([1, 0, 0]', 1, False)) n (Sphere(3, [0, 0, 0]', False)),
             (Halfspace([0, 1, 0]', -1, True)) n (Halfspace([0, 1, 0]', 1, False)) n (Halfspace([1, 0, 0]', -1, True)) n (Halfspace([1, 0, 0]', 1, False)) n (Sphere(3, [0, 0, 0]', False))})
        >>> floppy3x3x1 = floppy3x3x1.simp()
        >>> print(str(floppy3x3x1))
        RotationalPhysicalPuzzle(
            {(Halfspace([-1, 0, 0]', -1, True)) n (Halfspace([0, -1, 0]', -1, True)) n (Halfspace([0, 1, 0]', -1, True)) n (Halfspace([1, 0, 0]', -1, True)),
             (Halfspace([-1, 0, 0]', -1, True)) n (Halfspace([0, -1, 0]', 1, False)) n (Halfspace([1, 0, 0]', -1, True)) n (Sphere(3, [0, 0, 0]', False)),
             (Halfspace([-1, 0, 0]', -1, True)) n (Halfspace([0, 1, 0]', 1, False)) n (Halfspace([1, 0, 0]', -1, True)) n (Sphere(3, [0, 0, 0]', False)),
             (Halfspace([-1, 0, 0]', 1, False)) n (Halfspace([0, -1, 0]', -1, True)) n (Halfspace([0, 1, 0]', -1, True)) n (Sphere(3, [0, 0, 0]', False)),
             (Halfspace([-1, 0, 0]', 1, False)) n (Halfspace([0, -1, 0]', 1, False)) n (Sphere(3, [0, 0, 0]', False)),
             (Halfspace([-1, 0, 0]', 1, False)) n (Halfspace([0, 1, 0]', 1, False)) n (Sphere(3, [0, 0, 0]', False)),
             (Halfspace([0, -1, 0]', -1, True)) n (Halfspace([0, 1, 0]', -1, True)) n (Halfspace([1, 0, 0]', 1, False)) n (Sphere(3, [0, 0, 0]', False)),
             (Halfspace([0, -1, 0]', 1, False)) n (Halfspace([1, 0, 0]', 1, False)) n (Sphere(3, [0, 0, 0]', False)),
             (Halfspace([0, 1, 0]', 1, False)) n (Halfspace([1, 0, 0]', 1, False)) n (Sphere(3, [0, 0, 0]', False))})
        """
        simplified = set()
        for elem in self:
            elem = self.engine.simp(elem)
            if elem is not None:
                simplified.add(elem)
        return type(self)(simplified)

    def select_by(self, region):
        selected = set()
        unselected = set()
        for elem in self:
            res1 = self.engine.is_subset(elem, region)
            res2 = self.engine.is_disjoint(elem, region)
            if res1:
                selected.add(elem)
            elif res2:
                unselected.add(elem)
            else:
                raise ValueError
        return type(self)(selected), type(self)(unselected)

    def transform_by(self, trans):
        return type(self)(map(lambda e: self.engine.transform(e, trans), self))

    def no_collision(self):
        for elem1, elem2 in combinations(self, 2):
            if not self.engine.is_disjoint(elem1, elem2):
                return False
        return True

    def no_collision_with(self, other):
        for elem1, elem2 in product(self, other):
            if not self.engine.is_disjoint(elem1, elem2):
                return False
        return True

    def apply(self, operation):
        """
        >>> from sympy import *
        >>> from symplus.matplus import *
        >>> from magicpy.model.euclid import *
        >>> from magicpy.model.affine import *
        >>> cube2x2x2 = RotationalPhysicalPuzzle({Sphere()})
        >>> cube2x2x2 = cube2x2x2.cut_by(
        ...     (Halfspace(-i), Halfspace(i)),
        ...     (Halfspace(-j), Halfspace(j)),
        ...     (Halfspace(-k), Halfspace(k)))
        >>> print(str(cube2x2x2))
        RotationalPhysicalPuzzle(
            {(Halfspace([-1, 0, 0]', 0, False)) n (Halfspace([0, -1, 0]', 0, False)) n (Halfspace([0, 0, -1]', 0, False)) n (Sphere(1, [0, 0, 0]', False)),
             (Halfspace([-1, 0, 0]', 0, False)) n (Halfspace([0, -1, 0]', 0, False)) n (Halfspace([0, 0, 1]', 0, False)) n (Sphere(1, [0, 0, 0]', False)),
             (Halfspace([-1, 0, 0]', 0, False)) n (Halfspace([0, 0, -1]', 0, False)) n (Halfspace([0, 1, 0]', 0, False)) n (Sphere(1, [0, 0, 0]', False)),
             (Halfspace([-1, 0, 0]', 0, False)) n (Halfspace([0, 0, 1]', 0, False)) n (Halfspace([0, 1, 0]', 0, False)) n (Sphere(1, [0, 0, 0]', False)),
             (Halfspace([0, -1, 0]', 0, False)) n (Halfspace([0, 0, -1]', 0, False)) n (Halfspace([1, 0, 0]', 0, False)) n (Sphere(1, [0, 0, 0]', False)),
             (Halfspace([0, -1, 0]', 0, False)) n (Halfspace([0, 0, 1]', 0, False)) n (Halfspace([1, 0, 0]', 0, False)) n (Sphere(1, [0, 0, 0]', False)),
             (Halfspace([0, 0, -1]', 0, False)) n (Halfspace([0, 1, 0]', 0, False)) n (Halfspace([1, 0, 0]', 0, False)) n (Sphere(1, [0, 0, 0]', False)),
             (Halfspace([0, 0, 1]', 0, False)) n (Halfspace([0, 1, 0]', 0, False)) n (Halfspace([1, 0, 0]', 0, False)) n (Sphere(1, [0, 0, 0]', False))})
        >>> rot = rotate(pi/4, i); rot
        TransformationPath(10, t, EuclideanTransformation(Matrix([
        [0],
        [0],
        [0]]), Matrix([
        [cos(pi*t/80)],
        [sin(pi*t/80)],
        [           0],
        [           0]]), 1))
        >>> cube2x2x2 = cube2x2x2.apply(RegionalOperation(Halfspace(i), rot))
        >>> print(str(cube2x2x2))
        RotationalPhysicalPuzzle(
            {(Halfspace([-1, 0, 0]', 0, False)) n (Halfspace([0, -1, 0]', 0, False)) n (Halfspace([0, 0, -1]', 0, False)) n (Sphere(1, [0, 0, 0]', False)),
             (Halfspace([-1, 0, 0]', 0, False)) n (Halfspace([0, -1, 0]', 0, False)) n (Halfspace([0, 0, 1]', 0, False)) n (Sphere(1, [0, 0, 0]', False)),
             (Halfspace([-1, 0, 0]', 0, False)) n (Halfspace([0, 0, -1]', 0, False)) n (Halfspace([0, 1, 0]', 0, False)) n (Sphere(1, [0, 0, 0]', False)),
             (Halfspace([-1, 0, 0]', 0, False)) n (Halfspace([0, 0, 1]', 0, False)) n (Halfspace([0, 1, 0]', 0, False)) n (Sphere(1, [0, 0, 0]', False)),
             (Halfspace([0, -sqrt(2)/2, -sqrt(2)/2]', 0, False)) n (Halfspace([0, -sqrt(2)/2, sqrt(2)/2]', 0, False)) n (Halfspace([1, 0, 0]', 0, False)) n (Sphere(1, [0, 0, 0]', False)),
             (Halfspace([0, -sqrt(2)/2, -sqrt(2)/2]', 0, False)) n (Halfspace([0, sqrt(2)/2, -sqrt(2)/2]', 0, False)) n (Halfspace([1, 0, 0]', 0, False)) n (Sphere(1, [0, 0, 0]', False)),
             (Halfspace([0, -sqrt(2)/2, sqrt(2)/2]', 0, False)) n (Halfspace([0, sqrt(2)/2, sqrt(2)/2]', 0, False)) n (Halfspace([1, 0, 0]', 0, False)) n (Sphere(1, [0, 0, 0]', False)),
             (Halfspace([0, sqrt(2)/2, -sqrt(2)/2]', 0, False)) n (Halfspace([0, sqrt(2)/2, sqrt(2)/2]', 0, False)) n (Halfspace([1, 0, 0]', 0, False)) n (Sphere(1, [0, 0, 0]', False))})
        """
        if isinstance(operation, TotalOperation):
            for i in range(int(operation.action.length)+1):
                if not self.transform_by(operation.action(i)).is_valid_state():
                    raise IllegalOperationError
            return self.transform_by(operation.action())

        elif isinstance(operation, TargetedOperation):
            if not operation.target <= self:
                raise IllegalOperationError
            target = type(self)(operation.target)
            others = type(self)(self-target)

            for i in range(int(operation.action.length)+1):
                movedtarget = target.transform_by(operation.action(i))
                if not type(self)(others | movedtarget).is_valid_state():
                    raise IllegalOperationError
            return type(self)(others | movedtarget)

        elif isinstance(operation, RegionalOperation):
            target, others = self.select_by(operation.region)

            for i in range(int(operation.action.length)+1):
                movedtarget = target.transform_by(operation.action(i))
                if not type(self)(others | movedtarget).is_valid_state():
                    raise IllegalOperationError
            return type(self)(others | movedtarget)

        else:
            raise TypeError

class EuclideanPhysicalPuzzle(PhysicalPuzzle):
    engine = cube_engine()
    actions = PathMonoid(SE3)
    states = EuclideanTopology()

    def is_valid_state(self):
        if not all(simplify(self.states.contains(elem)) == True for elem in self):
            return False
        if not self.no_collision():
            return False
        return True

    def is_valid_operation(self, operation):
        if isinstance(operation, TotalOperation):
            return simplify(self.actions.contains(operation.action)) == True
        elif isinstance(operation, TargetedOperation):
            return (simplify(self.actions.contains(operation.action)) == True and
                    operation.target <= self)
        elif isinstance(operation, RegionalOperation):
            return (simplify(self.actions.contains(operation.action)) == True and
                    simplify(self.states.contains(operation.region)) == True)
        else:
            return False

    def __str__(self):
        elemstr = ',\n     '.join(sorted(map(mstr, self)))
        return '%s(\n    {%s})'%(type(self).__name__, elemstr)

    def apply(self, operation):
        if isinstance(operation, TotalOperation):
            return self.transform_by(operation.action())

        elif isinstance(operation, TargetedOperation):
            if not operation.target <= self:
                raise IllegalOperationError
            target = type(self)(operation.target)
            others = type(self)(self-target)

            for i in range(int(operation.action.length)):
                movedtarget = target.transform_by(operation.action(i))
                if not others.no_collision_with(movedtarget):
                    raise IllegalOperationError
            movedtarget = target.transform_by(operation.action())
            if not others.no_collision_with(movedtarget):
                raise IllegalOperationError
            return type(self)(others | movedtarget)

        elif isinstance(operation, RegionalOperation):
            target, others = self.select_by(operation.region)

            if self.is_stable_operation(operation) != True:
                for i in range(int(operation.action.length)):
                    movedtarget = target.transform_by(operation.action(i))
                    if not others.no_collision_with(movedtarget):
                        raise IllegalOperationError
            movedtarget = target.transform_by(operation.action())
            if not others.no_collision_with(movedtarget):
                raise IllegalOperationError
            return type(self)(others | movedtarget)

        else:
            raise TypeError

    def is_stable_operation(self, operation):
        # """
        # >>> from sympy import *
        # >>> from symplus.matplus import *
        # >>> from magicpy.model.euclid import *
        # >>> from magicpy.model.affine import *
        # >>> pz = PhysicalPuzzle({})
        # >>> pz.is_stable_operation(RegionalOperation(Halfspace(), rotate(i*pi/4)))
        # True
        # >>> pz.is_stable_operation(RegionalOperation(cylinder(), shift(i*3)))
        # True
        # >>> pz.is_stable_operation(RegionalOperation(Sphere(), rotate(i*pi/3))) # too weak
        # """
        if isinstance(operation, TotalOperation):
            return True

        elif isinstance(operation, TargetedOperation):
            return None

        elif isinstance(operation, RegionalOperation):
            return None
            # # too weak
            # extended = operation.action.function.expr
            # if simplify(transform(operation.region, extended)) == simplify(operation.region):
            #     return True

            # # too unstable, expensive
            # for i in range(int(operation.action.length)+1):
            #     moved = self.engine.transform(operation.region, operation.action(i))
            #     if not self.engine.equal(operation.region, moved):
            #         return False
            # return True

            return None

        else:
            raise TypeError

class RotationalPhysicalPuzzle(EuclideanPhysicalPuzzle):
    actions = PathMonoid(SO3)

class TranslationalPhysicalPuzzle(EuclideanPhysicalPuzzle):
    actions = PathMonoid(T3)


