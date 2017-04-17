from sympy import S, pi, N
from sympy.sets import EmptySet
from symplus.matplus import normalize, dot, project
from symplus.funcplus import FunctionInverse
from symplus.setplus import (Image, Intersection, Union, Complement, AbsoluteComplement,
    OpenRegularizedIntersection, OpenRegularizedUnion,
    OpenRegularizedAbsoluteComplement, simplify_boolean)
from symplus.euclid import (EuclideanSpace, Halfspace,
    Sphere, Box, Cylinder, Cone, EmptySpace,
    WholeSpace, Halfspace, InfiniteCylinder, SemiInfiniteCone)
from symplus.affine import (AffineTransformation, EuclideanTransformation,
    rmat2rquat, thax, thax_k2d)
from magicpy.solid.general import SolidEngine, OpenSCADDisplayer


class SymbolicSolidEngine(SolidEngine):
    def __init__(self):
        self.variables = {}
        self.operations = (OpenRegularizedUnion,
                           OpenRegularizedIntersection,
                           OpenRegularizedAbsoluteComplement)

    def common(self, zets):
        return self.operations[1](*zets)

    def fuse(self, zets):
        return self.operations[0](*zets)

    def complement(self, zet):
        return self.operations[2](zet)

    def transform(self, zets, *transs):
        for trans in transs:
            if isinstance(trans, Transformation):
                zets = [Image(trans, zet, evaluate=True) for zet in zets]
            else:
                zets = [Image(t, zet, evaluate=True) for zet in zets for t in trans]
        return zets

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
        zet = simplify_boolean(zet, op=self.operations)

class SymbolicSolidEngineVolumeAlgo(SymbolicSolidEngine):
    def __init__(self, subengine):
        SymbolicSolidEngine.__init__(self)
        self.subengine = subengine
        subengine.operations = self.operations

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

        if isinstance(zet, self.operations[1]):
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

        elif isinstance(zet, self.operations[0]):
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


class SymbolicOpenSCADDisplayer(OpenSCADDisplayer):
    """
    >>> import symplus as sp
    >>> import symplus.poly as poly
    >>> import magicpy.solid.sym as sym
    >>> dis = sym.SymbolicOpenSCADDisplayer()
    >>> doc = {}
    >>> doc['tetra'] = poly.tetrahedron
    >>> doc["dodeca"] = sp.Image(sp.translation([2,0,0]), poly.dodecahedron)
    >>> doc["icosa"] = sp.Image(sp.translation([-2,0,0]), poly.icosahedron)
    >>> doc["cube"] = sp.Image(sp.translation([0,2,0]), poly.cube)
    >>> doc["octa"] = sp.Image(sp.translation([0,-2,0]), poly.octahedron)
    >>> dis.settings["$vpd"] = 15
    >>> dis.show(doc)
    """
    def __init__(self):
        super().__init__()
        self.bdradius = 5.

    def interpret(self, obj):
        return self._interpret(self.bounding(obj))

    def bounding(self, obj, bd=None):
        if bd is None:
            bd = Sphere(radius=self.bdradius)

        if isinstance(obj, (Intersection, OpenRegularizedIntersection, Union,
                            OpenRegularizedIntersection, Complement)):
            return obj.func(*[self.bounding(arg, bd) for arg in obj.args])

        elif isinstance(obj, Image) and isinstance(obj.function, EuclideanTransformation):
            bd_ = Image(FunctionInverse(obj.function, evaluate=True), bd, evaluate=True)
            return Image(obj.function, self.bounding(obj.set, bd_))

        elif isinstance(obj, (AbsoluteComplement, OpenRegularizedAbsoluteComplement)):
            return Complement(bd, obj.set)

        elif isinstance(obj, (EmptySpace, Sphere, Box, Cylinder, Cone)):
            return obj

        elif isinstance(obj, WholeSpace):
            return bd

        elif isinstance(obj, Halfspace):
            d = normalize(obj.direction)
            offset2 = dot(bd.center, d) + bd.radius
            center = d*(obj.offset + offset2)/2
            height = offset2 - obj.offset
            return Cylinder(bd.radius, height, center, obj.direction)

        elif isinstance(obj, InfiniteCylinder):
            center = obj.center + project(bd.center - obj.center, direction)
            return Cylinder(obj.radius, bd.radius*2, center, obj.direction)

        elif isinstance(obj, SemiInfiniteCone):
            height = dot(bd.center - obj.center, normalize(direction))
            return Cone(obj.slope*height, height, obj.center, obj.direction)

        else:
            raise TypeError

    def _interpret(self, obj):
        if isinstance(obj, (Intersection, OpenRegularizedIntersection)):
            return "intersection(){%s}"%"".join(map(self.interpret, obj.args))

        elif isinstance(obj, (Union, OpenRegularizedIntersection)):
            return "union(){%s}"%"".join(map(self.interpret, obj.args))

        elif isinstance(obj, Complement):
            return "difference(){{{}{}}}".format(*map(self.interpret, obj.args))

        elif isinstance(obj, Image) and isinstance(obj.function, EuclideanTransformation):
            th, ax = thax(obj.function.rquat)
            return "translate({t!s})rotate({th!s},{ax!s}){p}{s}".format(
                t=list(N(obj.function.tvec, 5)),
                th=N(th/pi*180, 5), ax=list(N(ax, 5)),
                p="rotate(180,[0,0,1])mirror([0,0,1])" if obj.function.parity==1 else "",
                s=self.interpret(obj.set))

        elif isinstance(obj, EmptySpace):
            return "cube(0);"

        elif isinstance(obj, Sphere):
            return "translate({c!s})sphere({r!s});".format(
                c=list(N(obj.center, 5)),
                r=N(obj.radius, 5))

        elif isinstance(obj, Box):
            th, ax = thax(rmat2rquat(obj.orientation))
            return "translate({c!s})rotate({th!s},{ax!s})cube({s!s},center=true);".format(
                c=list(N(obj.center, 5)),
                th=N(th/pi*180, 5), ax=list(N(ax, 5)),
                s=list(N(obj.size, 5)))

        elif isinstance(obj, Cylinder):
            th, ax = thax_k2d(obj.direction)
            return "translate({c!s})rotate({th!s},{ax!s})cylinder({h!s},{r!s},{r!s},center=true);".format(
                c=list(N(obj.center, 5)),
                th=N(th/pi*180, 5), ax=list(N(ax, 5)),
                h=N(obj.height, 5),
                r=N(obj.radius, 5))

        elif isinstance(obj, Cone):
            th, ax = thax_k2d(obj.direction)
            return "translate({c!s})rotate({th!s},{ax!s})cylinder({h!s},0,{r!s},center=false);".format(
                c=list(N(obj.center, 5)),
                th=N(th/pi*180, 5), ax=list(N(ax, 5)),
                h=N(obj.height, 5),
                r=N(obj.radius, 5))

        else:
            raise TypeError

