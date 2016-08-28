from itertools import combinations, product, starmap
from sympy.sets import Intersection, Union
from symplus.setplus import Image, AbsoluteComplement
from symplus.path import IdentityPath
import sys
if sys.version_info[0] == 2:  from future_builtins import map


class SolidEngine:
    def is_outside(self, obj, reg):
        return NotImplemented

    def is_inside(self, obj, reg):
        return self.is_outside(obj, self.complement(reg))

    def side_of(self, obj, reg, err=False):
        res = self.is_inside(obj, reg) - self.is_outside(obj, reg)
        if err and res == 0:
            raise ValueError
        return res

    def located_in(self, obj, regs, err=False):
        return next((i for i, reg in enumerate(regs) if self.side_of(obj, reg, err=err) == 1), None)

    def divide_into(self, objs, regs, err=False):
        groups = [[] for _ in range(len(regs))]
        remaining = []
        for obj in objs:
            i = self.located_in(obj, regs, err=err)
            if i is None:  remaining.appand(obj)
            else:          groups[i].appand(obj)
        return groups, remaining

    def no_collision(self, objs):
        return all(starmap(self.is_outside, combinations(objs, 2)))

    def no_cross_collision(self, cols):
        return all(map(self.no_collision, product(*cols)))

    def common(self, objs):
        return NotImplemented

    def cross_common(self, cols):
        return type(cols[0])(map(self.common, product(*cols)))

    def fuse_all(self, objs):
        return NotImplemented

    def fuse(self, col, glues=None, remain=True, err=False):
        if glues is None:
            return self.fuse_all(col)
        targets, remaining = self.divide_into(col, glues, err=err)
        fused = list(map(self.fuse_all, targets))
        if remain:
            fused = fused + remaining
        return type(col)(fused)

    def complement(self, obj):
        return NotImplemented

    def partition(self, *objs):
        knives = [(obj, self.complement(obj)) for obj in objs]
        return list(map(self.common, product(*knives)))

    def partition_by(self, col, *objs):
        return self.cross_common([col]+self.partition(*objs))

    def transform(self, obj, trans):
        return NotImplemented

    def simp(self, obj):
        return obj

    def simplify(self, col):
        return type(col)([obj for obj in map(self.simp, col) if obj is not None])


class SymbolicSolidEngine(SolidEngine):
    def __init__(self):
        self.variables = {}

    def common(self, zets):
        return Intersection(*zets)

    def fuse_all(self, zets):
        return Union(*zets)

    def complement(self, zet):
        return AbsoluteComplement(zet)

    def transform(self, zet, trans):
            return Image(trans, zet)

    def simp(self, zet):
        return simplify(zet)

