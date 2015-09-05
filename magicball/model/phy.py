from itertools import combinations, product
from sympy.core import S
from sympy.sets import Set, Intersection
from magicball.model.affine import SE3, SO3, T3, transform
from magicball.symplus.setplus import AbstractSet, Topology
from magicball.symplus.strplus import mstr
from magicball.symplus.path import PathMonoid, Path
from magicball.engine.sample import SpaceSampleEngine, cube_engine
from magicball.model.euclid import complement


motionSet = PathMonoid(SE3)
rotationSet = PathMonoid(SO3)
translationSet = PathMonoid(T3)

regionSet = Topology(S.Reals**3)

def is_region(reg):
    return isinstance(reg, Set) and regionSet.contains(reg) == True

def is_motion(mot):
    return isinstance(mot, Path) and motionSet.contains(mot) == True

class RegionalMotion:
    def __init__(self, region, motion):
        # if is_region(region):
        #     raise TypeError
        # if is_motion(motion):
        #     raise TypeError
        self.region = region
        self.motion = motion


class PhysicalPuzzle(frozenset):
    def __new__(cls, regions, engine=cube_engine()):
        obj = frozenset.__new__(cls, regions)
        obj.engine = engine
        return obj

    def new(self, regions):
        return PhysicalPuzzle(regions, engine=self.engine)

    def __str__(self):
        return '%s({\n%s})'%(type(self).__name__, ',\n'.join(sorted(map(mstr, self))))

    def cut_by(self, *knives):
        """
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
            cutted.add(Intersection(*sub))
        return self.new(cutted)

    def simp(self):
        """
        >>> from sympy import *
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
        for aset in self:
            aset = self.engine.simp(aset)
            if aset != S.EmptySet:
                simplified.add(aset)
        return self.new(simplified)

    def no_collision(self):
        for reg1, reg2 in combinations(self, 2):
            if not self.engine.is_disjoint(reg1, reg2):
                return False
        return True

    def no_collision_with(self, other):
        for reg1, reg2 in product(self, other):
            if not self.engine.is_disjoint(reg1, reg2):
                return False
        return True

    def select_by(self, region):
        selected = set()
        unselected = set()
        for reg in self:
            res1 = self.engine.is_subset(reg, region)
            res2 = self.engine.is_disjoint(reg, region)
            if res1:
                selected.add(reg)
            elif res2:
                unselected.add(reg)
            else:
                raise ValueError
        return self.new(selected), self.new(unselected)

    def transform_by(self, mat):
        return self.new(map(lambda r: transform(r, mat), self))

    def move_by(self, action):
        """
        >>> from sympy import *
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
        [0, cos(pi*t/40), -sin(pi*t/40), 0],
        [0, sin(pi*t/40),  cos(pi*t/40), 0],
        [0,            0,             0, 1]])), 10)
        >>> cube2x2x2 = cube2x2x2.move_by(RegionalMotion(halfspace(i), rot))
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
        if isinstance(action, Path):
            return self.transform_by(action())
        elif isinstance(action, RegionalMotion):
            target, others = self.select_by(action.region)
            for i in range(int(action.motion.length)+1):
                movedtarget = target.transform_by(action.motion(i))
                if not others.no_collision_with(movedtarget):
                    raise ValueError
            movedtarget = target.transform_by(action.motion())
            return self.new(others | movedtarget)
        else:
            raise TypeError

