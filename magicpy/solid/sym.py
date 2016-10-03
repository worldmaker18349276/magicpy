from sympy import S
from sympy.sets import EmptySet
from symplus.setplus import (Image,
    OpenRegularizedIntersection, OpenRegularizedUnion,
    OpenRegularizedAbsoluteComplement, simplify_boolean)
from symplus.euclid import EuclideanSpace, Halfspace, as_algebraic
from symplus.affine import AffineTransformation
from magicpy.solid.general import SolidEngine


class SymbolicSolidEngine(SolidEngine):
    def __init__(self):
        self.variables = {}

    def common(self, zets):
        return OpenRegularizedIntersection(*zets)

    def fuse(self, zets):
        return OpenRegularizedUnion(*zets)

    def complement(self, zet):
        return OpenRegularizedAbsoluteComplement(zet)

    def transform(self, zet, trans):
        # if not isinstance(trans, AffineTransformation):
        #     raise TypeError
        return Image(trans, zet, evaluate=True)

    def is_null(self, zet):
        return zet == EmptySet()

    def simp(self, zet):
        zet = zet.replace(
            lambda e: isinstance(e, Set) and hasattr(e, "as_algebraic"),
            lambda e: e.as_algebraic(),
            simultaneous=False)
        zet = zet.replace(
            lambda e: isinstance(e, Image),
            lambda e: e.func(*e.args, evaluate=True),
            simultaneous=False)
        zet = zet.replace(
            lambda e: isinstance(e, Halfspace) and hash(e.direction) < hash(-e.direction),
            lambda e: AbsoluteComplement(AbsoluteComplement(e, evaluate=True), evaluate=False),
            simultaneous=False)
        zet = regularize(zet, closed=False)
        zet = simplify_boolean(zet,
                               op=(OpenRegularizedUnion,
                                   OpenRegularizedIntersection,
                                   OpenRegularizedAbsoluteComplement))

class SymbolicSolidEngineVolumeAlgo(SymbolicSolidEngine):
    def __init__(self, subengine):
        SymbolicSolidEngine.__init__(self)
        self.subengine = subengine

    def _cvrt(self, zet, ran=None):
        sub = self.subengine.construct(zet.subs(self.variables))
        if ran is not None:
            sub = self.subengine.common([sub, ran])
        return sub

    def _veq(self, sub1, sub2, ran=None):
        if ran is not None:
            sub1 = self.subengine.common([sub1, ran])
            sub2 = self.subengine.common([sub2, ran])
        if hasattr(self.subengine, "is_equal"):
            return self.subengine.is_equal(sub1, sub2)
        else:
            v1 = self.subengine.volume_of(sub1)
            v2 = self.subengine.volume_of(sub2)
            return abs(v1-v2) < 1e-06

    def is_null(self, zet):
        return self.subengine.is_null(self._cvrt(zet))

    def is_outside(self, zet1, zet2):
        return self.subengine.is_outside(self._cvrt(zet1), self._cvrt(zet2))

    def is_inside(self, zet1, zet2):
        return self.subengine.is_inside(self._cvrt(zet1), self._cvrt(zet2))

    def no_collision(self, zets):
        return self.subengine.no_collision(map(self._cvrt, zets))

    def no_cross_collision(self, cols):
        cols = [map(self._cvrt, col) for col in cols]
        return self.subengine.no_cross_collision(cols)

    def simp(self, zet):
        return self._volalgo(super(SymbolicSolidEngineVolumeAlgo, self).simp(zet))

    def _volalgo(self, zet, ran=None):
        if zet.subs(self.variables) in (S.EmptySet, S.UniversalSet):
            return zet

        if ran is None:
            ran = self._cvrt(S.UniversalSet)

        sub = self._cvrt(zet, ran)
        if self.subengine.is_null(sub):
            return S.EmptySet
        elif self._veq(sub, ran):
            return S.UniversalSet

        if isinstance(zet, OpenRegularizedIntersection):
            # remove unimportant arguments
            args = set(zet.args)
            for arg in list(args):
                args.discard(arg)
                sub_ = self._cvrt(self.common(args), ran)
                if not self._veq(sub_, sub):
                    args.add(arg)

            # simplify remaining arguments
            for arg in list(args):
                args.discard(arg)
                remaining = self._cvrt(self.common(args))
                ran_ = self.subengine.common([ran, remaining])
                args.add(self._volalgo(arg, ran_))
            return self.common(args)

        elif isinstance(zet, OpenRegularizedUnion):
            # remove unimportant arguments
            args = set(zet.args)
            for arg in list(args):
                args.discard(arg)
                sub_ = self._cvrt(self.fuse(args), ran)
                if not self._veq(sub_, sub):
                    args.add(arg)

            # simplify remaining arguments
            for arg in list(args):
                args.discard(arg)
                remaining = self._cvrt(self.fuse(args))
                ran_ = self.subengine.cut(ran, remaining)
                args.add(self._volalgo(arg, ran_))
            return self.fuse(args)

        else:
            return zet

