from itertools import combinations, product
from sympy.core import S, Lambda
from sympy.sets import Set
from sympy.simplify import simplify
from sympy.matrices import MatrixBase
from magicball.symplus.setplus import AbstractSet, Topology
from magicball.symplus.strplus import mstr
from magicball.symplus.path import PathMonoid, Path
from magicball.engine.sample import SpaceSampleEngine, cube_engine
from magicball.model.affine import SE3, SO3, T3, transform
from magicball.model.euclid import complement


motionSet = PathMonoid(SE3)
rotationSet = PathMonoid(SO3)
translationSet = PathMonoid(T3)

regionSet = Topology(S.Reals**3)

def is_region(aset):
    return isinstance(aset, Set) and simplify(regionSet.contains(aset)) == True

def is_motion(pth):
    return isinstance(pth, Path) and simplify(motionSet.contains(pth)) == True


def is_invariant_to(aset, trans):
    """
    >>> from sympy import *
    >>> from magicball.symplus.matplus import *
    >>> from magicball.model.euclid import *
    >>> from magicball.model.affine import *
    >>> is_invariant_to(sphere(), rotation(i*pi/3))
    True
    >>> is_invariant_to(cylinder(i+j), translation(i*3+j*3))
    True
    >>> is_invariant_to(sphere(), translation(i*3+k*4))
    """
    if isinstance(trans, MatrixBase):
        res = simplify(transform(aset, trans)) == simplify(aset)
        if res == True:
            return True
        else:
            return None
    elif isinstance(trans, Path):
        res = simplify(transform(aset, trans.function.expr)) == simplify(aset)
        if res == True:
            return True
        else:
            return None
    else:
        raise TypeError


class Motion:
    def __init__(self, path):
        self.path = path

class TargetedMotion:
    def __init__(self, target, path):
        self.target = target
        self.path = path

class RegionalMotion:
    def __init__(self, region, path):
        self.region = region
        self.path = path

    def is_stable(self):
        return is_invariant_to(self.region, self.path)

class IllegalOperationError(Exception):
    pass

class IllegalStateError(Exception):
    pass

class PhysicalPuzzle(frozenset):
    def __new__(cls, elements, engine=cube_engine()):
        obj = frozenset.__new__(cls, elements)
        obj.engine = engine
        return obj

    def new(self, elements):
        return PhysicalPuzzle(elements, engine=self.engine)

    def __str__(self):
        return '%s({\n%s})'%(type(self).__name__, ',\n'.join(sorted(map(mstr, self))))

    def cut_by(self, *knives):
        """
        >>> from magicball.symplus.matplus import *
        >>> from magicball.model.euclid import *
        >>> cube2x2x2 = PhysicalPuzzle({sphere()})
        >>> cube2x2x2 = cube2x2x2.cut_by(
        ...     (halfspace(-i), halfspace(i)),
        ...     (halfspace(-j), halfspace(j)),
        ...     (halfspace(-k), halfspace(k)))
        >>> print(str(cube2x2x2))
        PhysicalPuzzle({
        {(x, y, z) : (-x > 0) & (-y > 0) & (-z > 0) & (x**2 + y**2 + z**2 < 1)},
        {(x, y, z) : (-x > 0) & (-y > 0) & (x**2 + y**2 + z**2 < 1) & (z > 0)},
        {(x, y, z) : (-x > 0) & (-z > 0) & (x**2 + y**2 + z**2 < 1) & (y > 0)},
        {(x, y, z) : (-x > 0) & (x**2 + y**2 + z**2 < 1) & (y > 0) & (z > 0)},
        {(x, y, z) : (-y > 0) & (-z > 0) & (x > 0) & (x**2 + y**2 + z**2 < 1)},
        {(x, y, z) : (-y > 0) & (x > 0) & (x**2 + y**2 + z**2 < 1) & (z > 0)},
        {(x, y, z) : (-z > 0) & (x > 0) & (x**2 + y**2 + z**2 < 1) & (y > 0)},
        {(x, y, z) : (x > 0) & (x**2 + y**2 + z**2 < 1) & (y > 0) & (z > 0)}})
        """
        cutted = set()
        for sub in product(self, *knives):
            cutted.add(self.engine.intersection(*sub))
        return self.new(cutted)

    def combine(self, region=None):
        if region is None:
            return self.new(self.engine.union(*self))
        else:
            selected, others = self.select_by(region)
            return self.new(others | selected.combine())

    def simp(self):
        """
        >>> from sympy import *
        >>> from magicball.symplus.matplus import *
        >>> from magicball.model.euclid import *
        >>> from magicball.engine.sample import *
        >>> engine = cube_engine(4, 5)
        >>> knives = halfspace(i, 1), halfspace(j, 1), halfspace(-i, 1), halfspace(-j, 1)
        >>> floppy3x3x1 = PhysicalPuzzle({sphere(3)}, engine)
        >>> floppy3x3x1 = floppy3x3x1.cut_by(*map(with_complement, knives))
        >>> print(str(floppy3x3x1))
        PhysicalPuzzle({
        {(x, y, z) : (-x <= 1) & (-y <= 1) & (x <= 1) & (x**2 + y**2 + z**2 < 9) & (y <= 1)},
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
        {(x, y, z) : (-x > 1) & (-y > 1) & (x > 1) & (x**2 + y**2 + z**2 < 9) & (y > 1)}})
        >>> floppy3x3x1 = floppy3x3x1.simp()
        >>> print(str(floppy3x3x1))
        PhysicalPuzzle({
        {(x, y, z) : (x + 1 < 0) & (x**2 + y**2 + z**2 - 9 < 0) & (y + 1 < 0)},
        {(x, y, z) : (x + 1 < 0) & (x**2 + y**2 + z**2 - 9 < 0) & (y + 1 >= 0) & (y - 1 <= 0)},
        {(x, y, z) : (x + 1 < 0) & (x**2 + y**2 + z**2 - 9 < 0) & (y - 1 > 0)},
        {(x, y, z) : (x + 1 >= 0) & (x - 1 <= 0) & (x**2 + y**2 + z**2 - 9 < 0) & (y + 1 < 0)},
        {(x, y, z) : (x + 1 >= 0) & (x - 1 <= 0) & (x**2 + y**2 + z**2 - 9 < 0) & (y + 1 >= 0) & (y - 1 <= 0)},
        {(x, y, z) : (x + 1 >= 0) & (x - 1 <= 0) & (x**2 + y**2 + z**2 - 9 < 0) & (y - 1 > 0)},
        {(x, y, z) : (x - 1 > 0) & (x**2 + y**2 + z**2 - 9 < 0) & (y + 1 < 0)},
        {(x, y, z) : (x - 1 > 0) & (x**2 + y**2 + z**2 - 9 < 0) & (y + 1 >= 0) & (y - 1 <= 0)},
        {(x, y, z) : (x - 1 > 0) & (x**2 + y**2 + z**2 - 9 < 0) & (y - 1 > 0)}})
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

    def apply(self, action):
        """
        >>> from sympy import *
        >>> from magicball.symplus.matplus import *
        >>> from magicball.model.euclid import *
        >>> from magicball.model.affine import *
        >>> cube2x2x2 = PhysicalPuzzle({sphere()})
        >>> cube2x2x2 = cube2x2x2.cut_by(
        ...     (halfspace(-i), halfspace(i)),
        ...     (halfspace(-j), halfspace(j)),
        ...     (halfspace(-k), halfspace(k)))
        >>> cube2x2x2 = cube2x2x2.simp()
        >>> print(str(cube2x2x2))
        PhysicalPuzzle({
        {(x, y, z) : (x < 0) & (x**2 + y**2 + z**2 - 1 < 0) & (y < 0) & (z < 0)},
        {(x, y, z) : (x < 0) & (x**2 + y**2 + z**2 - 1 < 0) & (y < 0) & (z > 0)},
        {(x, y, z) : (x < 0) & (x**2 + y**2 + z**2 - 1 < 0) & (y > 0) & (z < 0)},
        {(x, y, z) : (x < 0) & (x**2 + y**2 + z**2 - 1 < 0) & (y > 0) & (z > 0)},
        {(x, y, z) : (x > 0) & (x**2 + y**2 + z**2 - 1 < 0) & (y < 0) & (z < 0)},
        {(x, y, z) : (x > 0) & (x**2 + y**2 + z**2 - 1 < 0) & (y < 0) & (z > 0)},
        {(x, y, z) : (x > 0) & (x**2 + y**2 + z**2 - 1 < 0) & (y > 0) & (z < 0)},
        {(x, y, z) : (x > 0) & (x**2 + y**2 + z**2 - 1 < 0) & (y > 0) & (z > 0)}})
        >>> rot = rotate(i*pi/4); rot
        Path(Lambda(t, Matrix([
        [1,            0,             0, 0],
        [0, cos(pi*t/20), -sin(pi*t/20), 0],
        [0, sin(pi*t/20),  cos(pi*t/20), 0],
        [0,            0,             0, 1]])), 5)
        >>> cube2x2x2 = cube2x2x2.apply(RegionalMotion(halfspace(i), rot))
        >>> cube2x2x2 = cube2x2x2.simp()
        >>> print(str(cube2x2x2))
        PhysicalPuzzle({
        {(x, y, z) : (x < 0) & (x**2 + y**2 + z**2 - 1 < 0) & (y < 0) & (z < 0)},
        {(x, y, z) : (x < 0) & (x**2 + y**2 + z**2 - 1 < 0) & (y < 0) & (z > 0)},
        {(x, y, z) : (x < 0) & (x**2 + y**2 + z**2 - 1 < 0) & (y > 0) & (z < 0)},
        {(x, y, z) : (x < 0) & (x**2 + y**2 + z**2 - 1 < 0) & (y > 0) & (z > 0)},
        {(x, y, z) : (x > 0) & (x**2 + y**2 + z**2 - 1 < 0) & (y + z < 0) & (y - z < 0)},
        {(x, y, z) : (x > 0) & (x**2 + y**2 + z**2 - 1 < 0) & (y + z < 0) & (y - z > 0)},
        {(x, y, z) : (x > 0) & (x**2 + y**2 + z**2 - 1 < 0) & (y + z > 0) & (y - z < 0)},
        {(x, y, z) : (x > 0) & (x**2 + y**2 + z**2 - 1 < 0) & (y + z > 0) & (y - z > 0)}})
        """
        if isinstance(action, Motion):
            return self.transform_by(action.path())

        elif isinstance(action, TargetedMotion):
            if not action.target <= self:
                raise IllegalOperationError
            target = self.new(action.target)
            others = self.new(self-target)
            for i in range(int(action.path.length)+1):
                movedtarget = target.transform_by(action.path(i))
                if not others.no_collision_with(movedtarget):
                    raise IllegalOperationError
            movedtarget = target.transform_by(action.path())
            return self.new(others | movedtarget)

        elif isinstance(action, RegionalMotion):
            target, others = self.select_by(action.region)
            if action.is_stable() != True:
                for i in range(int(action.path.length)+1):
                    movedtarget = target.transform_by(action.path(i))
                    if not others.no_collision_with(movedtarget):
                        raise IllegalOperationError
            movedtarget = target.transform_by(action.path())
            return self.new(others | movedtarget)

        else:
            raise TypeError

    def validate(self):
        if not self.no_collision():
            raise IllegalStateError

