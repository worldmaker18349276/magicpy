from sympy.sets import Intersection, Union, Complement, EmptySet
from symplus.setplus import Image, AbsoluteComplement
from magicpy.solid.general import SolidEngine


def Intersection_(*args):
    if len(args) > 1:
        return Intersection(*args, evaluate=False)
    elif len(args) == 1:
        return args[0]
    else:
        return S.UniversalSet

def Union_(*args):
    if len(args) > 1:
        return Union(*args, evaluate=False)
    elif len(args) == 1:
        return args[0]
    else:
        return S.EmptySet

class SymbolicSolidEngine(SolidEngine):
    def __init__(self):
        self.variables = {}

    def common(self, zets):
        return Intersection_(*zets)

    def fuse(self, zets):
        return Union_(*zets)

    def complement(self, zet):
        return AbsoluteComplement(zet)

    def transform(self, zet, trans):
            return Image(trans, zet, evaluate=False)

    def is_null(self, zet):
        return zet == EmptySet()

    def simp(self, zet):
        return simplify(zet.doit(deep=True))

    # def to_nnf(self, zet):
    #     raise NotImplementedError


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

    def simp(self, zet, ran=None):
        if zet.subs(self.variables) in (S.EmptySet, S.UniversalSet):
            return zet

        if zet.has(Complement):
            raise TypeError('zet is not nnf: %r' % zet)

        if ran is None:
            ran = self._cvrt(S.UniversalSet)

        sub = self._cvrt(zet, ran)
        if self.subengine.is_null(sub):
            return S.EmptySet
        elif self._veq(sub, ran):
            return S.UniversalSet

        if isinstance(zet, Intersection):
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
                args.add(self.simp(arg, ran_))
            return self.common(args)

        elif isinstance(zet, Union):
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
                args.add(self.simp(arg, ran_))
            return self.fuse(args)

        else:
            return zet

