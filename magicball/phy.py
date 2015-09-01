from itertools import combinations
from sympy.core import S
from sympy.sets import Set
from magicball.model.affine import SE3, SO3, T3, transform
from magicball.symplus.setplus import Topology
from magicball.symplus.path import PathMonoid, Path


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


class PhysicalPuzzle(set):
    def __new__(cls, regions):
        if any(not is_region(reg) for reg in regions):
            raise TypeError
        return set.__new__(cls, regions)

    def no_collision(self):
        for reg1, reg2 in combinations(self, 2):
            if not reg1.is_disjoint(reg2):
                return False
        return True

    def catch_by(self, region):
        def catcher(reg):
            res1 = region.is_superset(reg)
            res2 = region.is_disjoint(reg)
            if not res1 and not res2:
                raise ValueError
            return res1
        return filter(catcher, self)

    def move(self, motion):
        return map(lambda r: transform(r, motion), self)

    def apply(self, regmot):
        target = PhysicalPuzzle(self.catch_by(regmot.region))
        others = tuple(self - target)
        for i in range(int(regmot.motion.length)+1):
            movedtarget = tuple(target.move(regmot.motion[:i]))
            if not PhysicalPuzzle.no_collision(others + movedtarget):
                raise ValueError
        movedtarget = tuple(target.move(regmot.motion))
        return PhysicalPuzzle(others + movedtarget)

