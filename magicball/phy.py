from itertools import combinations, product
from sympy.core import S
from sympy.sets import Set, Intersection
from magicball.model.affine import SE3, SO3, T3, transform
from magicball.symplus.setplus import AbstractSet, Topology
from magicball.symplus.relplus import logicrelsimp
from magicball.symplus.path import PathMonoid, Path
from magicball.num.sample import spsetsimp, cube_sample
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
        if is_region(region):
            raise TypeError
        if is_motion(motion):
            raise TypeError
        self.region = region
        self.motion = motion


class PhysicalPuzzle(frozenset):
    def __new__(cls, regions, sample=cube_sample()):
        obj = frozenset.__new__(cls, regions)
        obj.sample = sample
        return obj

    def new(self, regions):
        return PhysicalPuzzle(regions, sample=self.sample)

    def no_collision(self):
        for reg1, reg2 in combinations(self, 2):
            if not self.sample.is_disjoint(reg1, reg2):
                return False
        return True

    def no_collision_with(self, other):
        for reg1, reg2 in product(self, other):
            if not self.sample.is_disjoint(reg1, reg2):
                return False
        return True

    def select_by(self, region):
        selected = set()
        unselected = set()
        for reg in self:
            res1 = self.sample.is_subset(reg, region)
            res2 = self.sample.is_disjoint(reg, region)
            if res1:
                selected.add(reg)
            elif res2:
                unselected.add(reg)
            else:
                raise ValueError
        return self.new(selected), self.new(unselected)

    def move_by(self, motion):
        return self.new(map(lambda r: transform(r, motion), self))

    def apply(self, regmot):
        target, others = self.select_by(regmot.region)
        for i in range(int(regmot.motion.length)+1):
            movedtarget = target.move_by(regmot.motion[:i])
            if not others.no_collision_with(movedtarget):
                raise ValueError
        movedtarget = target.move_by(regmot.motion)
        return self.new(others + movedtarget)

    def __str__(self):
        return '\n'.join(sorted(str(p.doit().expr) for p in self))

    def cut_by(self, *knives):
        """
        >>> from magicball.model.euclid import *
        >>> cube2x2x2 = PhysicalPuzzle({sphere()})
        >>> cube2x2x2 = cube2x2x2.cut_by(halfspace(i), halfspace(j), halfspace(k))
        >>> print(str(cube2x2x2))
        And(x <= 0, x**2 + y**2 + z**2 < 1, y <= 0, z <= 0)
        And(x <= 0, x**2 + y**2 + z**2 < 1, y <= 0, z > 0)
        And(x <= 0, x**2 + y**2 + z**2 < 1, y > 0, z <= 0)
        And(x <= 0, x**2 + y**2 + z**2 < 1, y > 0, z > 0)
        And(x > 0, x**2 + y**2 + z**2 < 1, y <= 0, z <= 0)
        And(x > 0, x**2 + y**2 + z**2 < 1, y <= 0, z > 0)
        And(x > 0, x**2 + y**2 + z**2 < 1, y > 0, z <= 0)
        And(x > 0, x**2 + y**2 + z**2 < 1, y > 0, z > 0)
        """
        subspaces = tuple(zip(knives, map(complement, knives)))
        cutted = set()
        for sub in product(self, *subspaces):
            cutted.add(Intersection(*sub, evaluate=False))
        return self.new(cutted)

    def simp(self):
        """
        >>> from sympy import *
        >>> from magicball.model.euclid import *
        >>> sample = cube_sample(4, 5)
        >>> knives = halfspace(i, 1), halfspace(j, 1), halfspace(-i, 1), halfspace(-j, 1)
        >>> floppy3x3x1 = PhysicalPuzzle({sphere(3)}, sample)
        >>> floppy3x3x1 = floppy3x3x1.cut_by(*knives)
        >>> print(str(floppy3x3x1))
        And(-x <= 1, -y <= 1, x <= 1, x**2 + y**2 + z**2 < 9, y <= 1)
        And(-x <= 1, -y <= 1, x <= 1, x**2 + y**2 + z**2 < 9, y > 1)
        And(-x <= 1, -y <= 1, x > 1, x**2 + y**2 + z**2 < 9, y <= 1)
        And(-x <= 1, -y <= 1, x > 1, x**2 + y**2 + z**2 < 9, y > 1)
        And(-x <= 1, -y > 1, x <= 1, x**2 + y**2 + z**2 < 9, y <= 1)
        And(-x <= 1, -y > 1, x <= 1, x**2 + y**2 + z**2 < 9, y > 1)
        And(-x <= 1, -y > 1, x > 1, x**2 + y**2 + z**2 < 9, y <= 1)
        And(-x <= 1, -y > 1, x > 1, x**2 + y**2 + z**2 < 9, y > 1)
        And(-x > 1, -y <= 1, x <= 1, x**2 + y**2 + z**2 < 9, y <= 1)
        And(-x > 1, -y <= 1, x <= 1, x**2 + y**2 + z**2 < 9, y > 1)
        And(-x > 1, -y <= 1, x > 1, x**2 + y**2 + z**2 < 9, y <= 1)
        And(-x > 1, -y <= 1, x > 1, x**2 + y**2 + z**2 < 9, y > 1)
        And(-x > 1, -y > 1, x <= 1, x**2 + y**2 + z**2 < 9, y <= 1)
        And(-x > 1, -y > 1, x <= 1, x**2 + y**2 + z**2 < 9, y > 1)
        And(-x > 1, -y > 1, x > 1, x**2 + y**2 + z**2 < 9, y <= 1)
        And(-x > 1, -y > 1, x > 1, x**2 + y**2 + z**2 < 9, y > 1)
        >>> floppy3x3x1 = floppy3x3x1.simp()
        >>> print(str(floppy3x3x1))
        And(x + 1 < 0, x**2 + y**2 + z**2 - 9 < 0, y + 1 < 0)
        And(x + 1 < 0, x**2 + y**2 + z**2 - 9 < 0, y + 1 >= 0, y - 1 <= 0)
        And(x + 1 < 0, x**2 + y**2 + z**2 - 9 < 0, y - 1 > 0)
        And(x + 1 >= 0, x - 1 <= 0, x**2 + y**2 + z**2 - 9 < 0, y + 1 < 0)
        And(x + 1 >= 0, x - 1 <= 0, x**2 + y**2 + z**2 - 9 < 0, y + 1 >= 0, y - 1 <= 0)
        And(x + 1 >= 0, x - 1 <= 0, x**2 + y**2 + z**2 - 9 < 0, y - 1 > 0)
        And(x - 1 > 0, x**2 + y**2 + z**2 - 9 < 0, y + 1 < 0)
        And(x - 1 > 0, x**2 + y**2 + z**2 - 9 < 0, y + 1 >= 0, y - 1 <= 0)
        And(x - 1 > 0, x**2 + y**2 + z**2 - 9 < 0, y - 1 > 0)
        """
        simplified = set()
        for aset in self:
            aset = aset.doit()
            expr = logicrelsimp(aset.expr)
            aset = AbstractSet(aset.variables, expr)
            aset = aset.expand()
            aset = spsetsimp(self.sample, aset)
            if aset != S.EmptySet:
                simplified.add(aset)
        return self.new(simplified)

