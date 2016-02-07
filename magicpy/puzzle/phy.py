from itertools import combinations, product
from sympy.core import S, Lambda
from sympy.sets import Set
from sympy.simplify import simplify
from sympy.matrices import MatrixBase
from symplus.setplus import AbstractSet, NaturalTopology
from symplus.strplus import mstr
from magicpy.engine.marching import cube_engine
from magicpy.model.path import PathMonoid, Path
from magicpy.model.affine import SE3, SO3, T3, transform
from magicpy.model.euclid import complement


motionSet = PathMonoid(SE3)
rotationSet = PathMonoid(SO3)
translationSet = PathMonoid(T3)

regionSet = NaturalTopology(S.Reals**3)


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
    def __new__(cls, elements, engine=cube_engine(), actions=motionSet):
        obj = frozenset.__new__(cls, elements)
        obj.engine = engine
        obj.actions = actions
        return obj

    def new(self, elements):
        return PhysicalPuzzle(elements, engine=self.engine, actions=self.actions)

    def is_valid_state(self):
        if not all(simplify(regionSet.contains(elem)) == True for elem in self):
            return False
        if not self.no_collision():
            return False

    def is_valid_operation(self, operation):
        if isinstance(operation, TotalOperation):
            return simplify(self.actions.contains(operation.action)) == True
        elif isinstance(operation, TargetedOperation):
            return simplify(self.actions.contains(operation.action)) == True
        elif isinstance(operation, RegionalOperation):
            return (simplify(self.actions.contains(operation.action)) == True and
                    simplify(regionSet.contains(operation.region)) == True)
        else:
            return False

    def __str__(self):
        if self.actions is motionSet:
            actionstr = 'PathMonoid(SE3)'
        elif self.actions is rotationSet:
            actionstr = 'PathMonoid(SO3)'
        elif self.actions is translationSet:
            actionstr = 'PathMonoid(T3)'
        else:
            actionstr = mstr(self.actions)
        return '%s(\n    {%s},\n    actions=%s)'%(
            type(self).__name__,
            ',\n     '.join(sorted(map(mstr, self))),
            actionstr)

    def cut_by(self, *knives):
        """
        >>> from symplus.matplus import *
        >>> from magicpy.model.euclid import *
        >>> cube2x2x2 = PhysicalPuzzle({sphere()})
        >>> cube2x2x2 = cube2x2x2.cut_by(
        ...     (halfspace(-i), halfspace(i)),
        ...     (halfspace(-j), halfspace(j)),
        ...     (halfspace(-k), halfspace(k)))
        >>> print(str(cube2x2x2))
        PhysicalPuzzle(
            {{(x, y, z) : (-x > 0) & (-y > 0) & (-z > 0) & (x**2 + y**2 + z**2 < 1)},
             {(x, y, z) : (-x > 0) & (-y > 0) & (x**2 + y**2 + z**2 < 1) & (z > 0)},
             {(x, y, z) : (-x > 0) & (-z > 0) & (x**2 + y**2 + z**2 < 1) & (y > 0)},
             {(x, y, z) : (-x > 0) & (x**2 + y**2 + z**2 < 1) & (y > 0) & (z > 0)},
             {(x, y, z) : (-y > 0) & (-z > 0) & (x > 0) & (x**2 + y**2 + z**2 < 1)},
             {(x, y, z) : (-y > 0) & (x > 0) & (x**2 + y**2 + z**2 < 1) & (z > 0)},
             {(x, y, z) : (-z > 0) & (x > 0) & (x**2 + y**2 + z**2 < 1) & (y > 0)},
             {(x, y, z) : (x > 0) & (x**2 + y**2 + z**2 < 1) & (y > 0) & (z > 0)}},
            actions=PathMonoid(SE3))
        """
        cutted = set()
        for sub in product(self, *knives):
            cutted.add(self.engine.intersection(*sub))
        return self.new(cutted)

    def combine(self, region=None):
        if region is None:
            return self.new({self.engine.union(*self)})
        else:
            selected, others = self.select_by(region)
            return self.new(others | selected.combine())

    def simp(self):
        """
        >>> from sympy import *
        >>> from symplus.matplus import *
        >>> from magicpy.model.euclid import *
        >>> from magicpy.engine.marching import *
        >>> engine = cube_engine(4, 5)
        >>> knives = halfspace(i, 1), halfspace(j, 1), halfspace(-i, 1), halfspace(-j, 1)
        >>> floppy3x3x1 = PhysicalPuzzle({sphere(3)}, engine)
        >>> floppy3x3x1 = floppy3x3x1.cut_by(*map(with_complement, knives))
        >>> print(str(floppy3x3x1))
        PhysicalPuzzle(
            {{(x, y, z) : (-x <= 1) & (-y <= 1) & (x <= 1) & (x**2 + y**2 + z**2 < 9) & (y <= 1)},
             {(x, y, z) : (-x <= 1) & (-y <= 1) & (x <= 1) & (x**2 + y**2 + z**2 < 9) & (y > 1)},
             {(x, y, z) : (-x <= 1) & (-y <= 1) & (x > 1) & (x**2 + y**2 + z**2 < 9) & (y <= 1)},
             {(x, y, z) : (-x <= 1) & (-y <= 1) & (x > 1) & (x**2 + y**2 + z**2 < 9) & (y > 1)},
             {(x, y, z) : (-x <= 1) & (-y > 1) & (x <= 1) & (x**2 + y**2 + z**2 < 9) & (y <= 1)},
             {(x, y, z) : (-x <= 1) & (-y > 1) & (x <= 1) & (x**2 + y**2 + z**2 < 9) & (y > 1)},
             {(x, y, z) : (-x <= 1) & (-y > 1) & (x > 1) & (x**2 + y**2 + z**2 < 9) & (y <= 1)},
             {(x, y, z) : (-x <= 1) & (-y > 1) & (x > 1) & (x**2 + y**2 + z**2 < 9) & (y > 1)},
             {(x, y, z) : (-x > 1) & (-y <= 1) & (x <= 1) & (x**2 + y**2 + z**2 < 9) & (y <= 1)},
             {(x, y, z) : (-x > 1) & (-y <= 1) & (x <= 1) & (x**2 + y**2 + z**2 < 9) & (y > 1)},
             {(x, y, z) : (-x > 1) & (-y <= 1) & (x > 1) & (x**2 + y**2 + z**2 < 9) & (y <= 1)},
             {(x, y, z) : (-x > 1) & (-y <= 1) & (x > 1) & (x**2 + y**2 + z**2 < 9) & (y > 1)},
             {(x, y, z) : (-x > 1) & (-y > 1) & (x <= 1) & (x**2 + y**2 + z**2 < 9) & (y <= 1)},
             {(x, y, z) : (-x > 1) & (-y > 1) & (x <= 1) & (x**2 + y**2 + z**2 < 9) & (y > 1)},
             {(x, y, z) : (-x > 1) & (-y > 1) & (x > 1) & (x**2 + y**2 + z**2 < 9) & (y <= 1)},
             {(x, y, z) : (-x > 1) & (-y > 1) & (x > 1) & (x**2 + y**2 + z**2 < 9) & (y > 1)}},
            actions=PathMonoid(SE3))
        >>> floppy3x3x1 = floppy3x3x1.simp()
        >>> print(str(floppy3x3x1))
        PhysicalPuzzle(
            {{(x, y, z) : (x + 1 < 0) & (x**2 + y**2 + z**2 - 9 < 0) & (y + 1 < 0)},
             {(x, y, z) : (x + 1 < 0) & (x**2 + y**2 + z**2 - 9 < 0) & (y + 1 >= 0) & (y - 1 <= 0)},
             {(x, y, z) : (x + 1 < 0) & (x**2 + y**2 + z**2 - 9 < 0) & (y - 1 > 0)},
             {(x, y, z) : (x + 1 >= 0) & (x - 1 <= 0) & (x**2 + y**2 + z**2 - 9 < 0) & (y + 1 < 0)},
             {(x, y, z) : (x + 1 >= 0) & (x - 1 <= 0) & (x**2 + y**2 + z**2 - 9 < 0) & (y + 1 >= 0) & (y - 1 <= 0)},
             {(x, y, z) : (x + 1 >= 0) & (x - 1 <= 0) & (x**2 + y**2 + z**2 - 9 < 0) & (y - 1 > 0)},
             {(x, y, z) : (x - 1 > 0) & (x**2 + y**2 + z**2 - 9 < 0) & (y + 1 < 0)},
             {(x, y, z) : (x - 1 > 0) & (x**2 + y**2 + z**2 - 9 < 0) & (y + 1 >= 0) & (y - 1 <= 0)},
             {(x, y, z) : (x - 1 > 0) & (x**2 + y**2 + z**2 - 9 < 0) & (y - 1 > 0)}},
            actions=PathMonoid(SE3))
        """
        simplified = set()
        for elem in self:
            elem = self.engine.simp(elem)
            if elem != S.EmptySet:
                simplified.add(elem)
        return self.new(simplified)

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
        return self.new(selected), self.new(unselected)

    def transform_by(self, mat):
        return self.new(map(lambda e: self.engine.transform(e, mat), self))

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
        >>> cube2x2x2 = PhysicalPuzzle({sphere()})
        >>> cube2x2x2 = cube2x2x2.cut_by(
        ...     (halfspace(-i), halfspace(i)),
        ...     (halfspace(-j), halfspace(j)),
        ...     (halfspace(-k), halfspace(k)))
        >>> cube2x2x2 = cube2x2x2.simp()
        >>> print(str(cube2x2x2))
        PhysicalPuzzle(
            {{(x, y, z) : (x < 0) & (x**2 + y**2 + z**2 - 1 < 0) & (y < 0) & (z < 0)},
             {(x, y, z) : (x < 0) & (x**2 + y**2 + z**2 - 1 < 0) & (y < 0) & (z > 0)},
             {(x, y, z) : (x < 0) & (x**2 + y**2 + z**2 - 1 < 0) & (y > 0) & (z < 0)},
             {(x, y, z) : (x < 0) & (x**2 + y**2 + z**2 - 1 < 0) & (y > 0) & (z > 0)},
             {(x, y, z) : (x > 0) & (x**2 + y**2 + z**2 - 1 < 0) & (y < 0) & (z < 0)},
             {(x, y, z) : (x > 0) & (x**2 + y**2 + z**2 - 1 < 0) & (y < 0) & (z > 0)},
             {(x, y, z) : (x > 0) & (x**2 + y**2 + z**2 - 1 < 0) & (y > 0) & (z < 0)},
             {(x, y, z) : (x > 0) & (x**2 + y**2 + z**2 - 1 < 0) & (y > 0) & (z > 0)}},
            actions=PathMonoid(SE3))
        >>> rot = rotate(i*pi/4); rot
        Path(Lambda(t, Matrix([
        [1,            0,             0, 0],
        [0, cos(pi*t/20), -sin(pi*t/20), 0],
        [0, sin(pi*t/20),  cos(pi*t/20), 0],
        [0,            0,             0, 1]])), 5)
        >>> cube2x2x2 = cube2x2x2.apply(RegionalOperation(halfspace(i), rot))
        >>> cube2x2x2 = cube2x2x2.simp()
        >>> print(str(cube2x2x2))
        PhysicalPuzzle(
            {{(x, y, z) : (x < 0) & (x**2 + y**2 + z**2 - 1 < 0) & (y < 0) & (z < 0)},
             {(x, y, z) : (x < 0) & (x**2 + y**2 + z**2 - 1 < 0) & (y < 0) & (z > 0)},
             {(x, y, z) : (x < 0) & (x**2 + y**2 + z**2 - 1 < 0) & (y > 0) & (z < 0)},
             {(x, y, z) : (x < 0) & (x**2 + y**2 + z**2 - 1 < 0) & (y > 0) & (z > 0)},
             {(x, y, z) : (x > 0) & (x**2 + y**2 + z**2 - 1 < 0) & (y + z < 0) & (y - z < 0)},
             {(x, y, z) : (x > 0) & (x**2 + y**2 + z**2 - 1 < 0) & (y + z < 0) & (y - z > 0)},
             {(x, y, z) : (x > 0) & (x**2 + y**2 + z**2 - 1 < 0) & (y + z > 0) & (y - z < 0)},
             {(x, y, z) : (x > 0) & (x**2 + y**2 + z**2 - 1 < 0) & (y + z > 0) & (y - z > 0)}},
            actions=PathMonoid(SE3))
        """
        if isinstance(operation, TotalOperation):
            return self.transform_by(operation.action())

        elif isinstance(operation, TargetedOperation):
            if not operation.target <= self:
                raise IllegalOperationError
            target = self.new(operation.target)
            others = self.new(self-target)
            for i in range(int(operation.action.length)+1):
                movedtarget = target.transform_by(operation.action(i))
                if not others.no_collision_with(movedtarget):
                    raise IllegalOperationError
            movedtarget = target.transform_by(operation.action())
            if not others.no_collision_with(movedtarget):
                raise IllegalOperationError
            return self.new(others | movedtarget)

        elif isinstance(operation, RegionalOperation):
            target, others = self.select_by(operation.region)
            if self.is_stable_operation(operation) != True:
                for i in range(int(operation.action.length)+1):
                    movedtarget = target.transform_by(operation.action(i))
                    if not others.no_collision_with(movedtarget):
                        raise IllegalOperationError
            movedtarget = target.transform_by(operation.action())
            if not others.no_collision_with(movedtarget):
                raise IllegalOperationError
            return self.new(others | movedtarget)

        else:
            raise TypeError

    def is_stable_operation(self, operation):
        """
        >>> from sympy import *
        >>> from symplus.matplus import *
        >>> from magicpy.model.euclid import *
        >>> from magicpy.model.affine import *
        >>> pz = PhysicalPuzzle({})
        >>> pz.is_stable_operation(RegionalOperation(halfspace(), rotate(i*pi/4)))
        True
        >>> pz.is_stable_operation(RegionalOperation(cylinder(), shift(i*3)))
        True
        >>> pz.is_stable_operation(RegionalOperation(sphere(), rotate(i*pi/3))) # too weak
        """
        if isinstance(operation, TotalOperation):
            return True

        elif isinstance(operation, TargetedOperation):
            return None

        elif isinstance(operation, RegionalOperation):
            extended = operation.action.function.expr
            # too weak
            if simplify(transform(operation.region, extended)) == simplify(operation.region):
                return True

            # # too unstable, expensive
            # for i in range(int(operation.action.length)+1):
            #     moved = self.engine.transform(operation.region, operation.action(i))
            #     if not self.engine.equal(operation.region, moved):
            #         return False
            # return True

            return None

        else:
            raise TypeError

