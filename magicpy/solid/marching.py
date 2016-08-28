from __future__ import division
from itertools import product
from functools import reduce
from operator import and_, or_, xor
from sympy.core import S
from sympy.core.compatibility import lru_cache
from sympy.sets import Set, Intersection, Union, Complement
from sympy.logic import Not, And, Or, Xor, Implies, Equivalent
from sympy.logic.boolalg import true, false, Boolean, is_nnf
from sympy.utilities import lambdify
from symplus.simplus import logicrelsimp
from symplus.setplus import AbstractSet, as_abstract
from magicpy.solid.general import SymbolicSolidEngine
import sys
if sys.version_info[0] == 2:  range = xrange


def setbit1(bits, index):
    return bits|(1<<index)

def setbit0(bits, index):
    return bits&~(1<<index)

def getbit(bits, index):
    return bits&(1<<index) != 0

def bitmap(func, voxels):
    bits = 0
    t = 1
    for elem in voxels:
        if func(elem):
            bits |= t
        t <<= 1
    return bits

class Voxels:
    def __init__(self, voxels_iter_getter, length):
        self._getter = voxels_iter_getter
        self.length = length
        self.ran = ~((~1)<<length)

    def __iter__(self):
        return self._getter()

    def __len__(self):
        return self.length

    @lru_cache(maxsize=128)
    def _bits_of_set(self, zet):
        if isinstance(zet, AbstractSet):
            var = zet.variables
            expr = zet.expr
            func = lambdify(var, expr)
            if len(var) == 1:
                return bitmap(func, self)
            else:
                return bitmap(lambda v: func(*v), self)
        else:
            return bitmap(zet.__contains__, self)

    def bits_of_set(self, zet):
        if isinstance(zet, Intersection):
            return reduce(and_, (self.bits_of_set(e) for e in zet.args))
        elif isinstance(zet, Union):
            return reduce(or_, (self.bits_of_set(e) for e in zet.args))
        elif isinstance(zet, Complement):
            return self.bits_of_set(zet.args[0]) &~self.bits_of_set(zet.args[1])
        elif isinstance(zet, AbstractSet):
            return self.bits_of_expr(zet.variables, zet.expr)
        else:
            return self._bits_of_set(as_abstract(zet))

    def bits_of_expr(self, var, expr):
        if isinstance(expr, And):
            return reduce(and_, (self.bits_of_expr(var, e) for e in expr.args))
        elif isinstance(expr, Or):
            return reduce(or_, (self.bits_of_expr(var, e) for e in expr.args))
        elif isinstance(expr, Not):
            return self.ran &~self.bits_of_expr(var, expr.args[0])
        elif isinstance(expr, Xor):
            return reduce(xor, (self.bits_of_expr(var, e) for e in expr.args))
        elif isinstance(expr, (Implies, Equivalent)):
            return self.bits_of_expr(var, expr.to_nnf(simplify=False))
        else:
            return self._bits_of_set(AbstractSet(var, expr))

def cube_voxels(r=2.0, n=10):
    rn = int(r*n)
    def voxels_iter_getter():
        return ((x/n, y/n, z/n) for x, y, z in product(range(-rn, rn+1), repeat=3))
    return Voxels(voxels_iter_getter, (2*rn+1)**3)


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

def And_(*args):
    if len(args) > 1:
        return And(*args, evaluate=False)
    elif len(args) == 1:
        return args[0]
    else:
        return true

def Or_(*args):
    if len(args) > 1:
        return Or(*args, evaluate=False)
    elif len(args) == 1:
        return args[0]
    else:
        return false

def marchingsetsimp(voxels, zet, subs={}, ran=None):
    """
    >>> from sympy import *
    >>> from symplus.setplus import *
    >>> x, y, z = symbols('x y z', real=True)
    >>> voxels = cube_voxels(2,10)
    >>> s1 = AbstractSet((x,y,z), x*2+y-z>0)
    >>> s2 = AbstractSet((x,y,z), x*2+y-z>1)
    >>> s12 = Intersection_(s1, s2); s12
    Intersection(AbstractSet((x, y, z), 2*x + y - z > 0), AbstractSet((x, y, z), 2*x + y - z > 1))
    >>> marchingsetsimp(voxels, s12)
    AbstractSet((x, y, z), 2*x + y - z > 1)
    >>> s3 = AbstractSet((x,y,z), x+2*y>0)
    >>> s4 = AbstractSet((x,y,z), x-2*y>0)
    >>> s5 = AbstractSet((x,y,z), 2*x+y>-1)
    >>> s345 = Intersection_(s3, s4, s5)
    >>> marchingsetsimp(voxels, s345)
    Intersection(AbstractSet((x, y, z), x - 2*y > 0), AbstractSet((x, y, z), x + 2*y > 0))
    >>> s6 = AbstractSet((x,y,z), 2*x+y<-1)
    >>> s346 = Intersection_(s3, s4, s6)
    >>> marchingsetsimp(voxels, s346)
    EmptySet()
    """
    if not isinstance(zet, Set):
        raise TypeError('zet is not Set: %r' % zet)

    if zet.subs(subs) in (S.EmptySet, S.UniversalSet):
        return zet

    if zet.has(Complement):
        raise TypeError('zet is not nnf: %r' % zet)

    if ran is None:
        ran = voxels.ran

    bits = voxels.bits_of_set(zet.subs(subs)) & ran
    if bits == 0:
        return S.EmptySet
    elif bits == ran:
        return S.UniversalSet

    if isinstance(zet, Intersection):
        # remove unimportant arguments
        args = set(zet.args)
        for arg in list(args):
            args.discard(arg)
            bits_ = voxels.bits_of_set(Intersection_(*args).subs(subs)) & ran
            if bits_ != bits:
                args.add(arg)

        # simplify remaining arguments
        for arg in list(args):
            args.discard(arg)
            ran_ = ran & voxels.bits_of_set(Intersection_(*args).subs(subs))
            args.add(marchingsetsimp(voxels, arg, subs, ran_))
        return Intersection_(*args)

    elif isinstance(zet, Union):
        # remove unimportant arguments
        args = set(zet.args)
        for arg in list(args):
            args.discard(arg)
            bits_ = voxels.bits_of_set(Union_(*args).subs(subs)) & ran
            if bits_ != bits:
                args.add(arg)

        # simplify remaining arguments
        for arg in list(args):
            args.discard(arg)
            ran_ = ran &~voxels.bits_of_set(Union_(*args).subs(subs))
            args.add(marchingsetsimp(voxels, arg, subs, ran_))
        return Union_(*args)

    else:
        return zet

def marchingfuncsimp(voxels, var, expr, subs={}, ran=None):
    """
    >>> from sympy import *
    >>> from symplus.setplus import *
    >>> x, y, z = symbols('x y z', real=True)
    >>> voxels = cube_voxels(2,10)
    >>> s1 = x*2+y-z>0
    >>> s2 = x*2+y-z>1
    >>> s12 = s1 & s2; s12
    And(2*x + y - z > 0, 2*x + y - z > 1)
    >>> marchingfuncsimp(voxels, (x,y,z), s12)
    2*x + y - z > 1
    >>> s3 = x+2*y>0
    >>> s4 = x-2*y>0
    >>> s5 = 2*x+y>-1
    >>> s345 = s3 & s4 & s5
    >>> marchingfuncsimp(voxels, (x,y,z), s345)
    And(x + 2*y > 0, x - 2*y > 0)
    >>> s6 = 2*x+y<-1
    >>> s346 = s3 & s4 & s6
    >>> marchingfuncsimp(voxels, (x,y,z), s346)
    False
    """
    if not isinstance(expr, Boolean):
        raise TypeError('expr is not Boolean: %r' % expr)

    if expr.subs(subs) in (true, false):
        return expr

    if not is_nnf(expr, False):
        raise TypeError('expr is not nnf: %r' % expr)

    if ran is None:
        ran = voxels.ran

    bits = voxels.bits_of_expr(var, expr.subs(subs)) & ran
    if bits == 0:
        return false
    elif bits == ran:
        return true

    if isinstance(expr, And):
        # remove unimportant arguments
        args = set(expr.args)
        for arg in list(args):
            args.discard(arg)
            bits_ = voxels.bits_of_expr(var, And_(*args).subs(subs)) & ran
            if bits_ != bits:
                args.add(arg)

        # simplify remaining arguments
        for arg in list(args):
            args.discard(arg)
            ran_ = ran & voxels.bits_of_expr(var, And_(*args).subs(subs))
            args.add(marchingfuncsimp(voxels, var, args, subs, ran_))
        return And_(*args)

    elif isinstance(expr, Or):
        # remove unimportant arguments
        args = set(expr.args)
        for arg in list(args):
            args.discard(arg)
            bits_ = voxels.bits_of_expr(var, Or_(*args).subs(subs)) & ran
            if bits_ != bits:
                args.add(arg)

        # simplify remaining arguments
        for arg in list(args):
            args.discard(arg)
            ran_ = ran &~voxels.bits_of_expr(Or_(*args).subs(subs))
            args.add(marchingfuncsimp(voxels, var, arg, subs, ran_))
        return Or_(*args)

    else:
        return expr


class MarchingCubesSolidEngine(SymbolicSolidEngine):
    def __init__(self, voxels):
        SymbolicSolidEngine.__init__(self)
        self.voxels = voxels

    def is_outside(self, zet1, zet2):
        zet1 = zet1.subs(self.variables)
        zet2 = zet2.subs(self.variables)
        return self.voxels.bits_of_set(zet1) & self.voxels.bits_of_set(zet2) == 0

    def is_inside(self, zet1, zet2):
        zet1 = zet1.subs(self.variables)
        zet2 = zet2.subs(self.variables)
        return self.voxels.bits_of_set(zet1) &~self.voxels.bits_of_set(zet2) == 0

    def equal(self, zet1, zet2):
        zet1 = zet1.subs(self.variables)
        zet2 = zet2.subs(self.variables)
        return self.voxels.bits_of_set(zet1) == self.voxels.bits_of_set(zet2)

    def simp(self, zet):
        zet = zet.doit()
        if zet.subs(self.variables) == S.EmptySet:
            return None

        elif isinstance(zet, AbstractSet):
            expr = logicrelsimp(zet.expr)
            expr = marchingfuncsimp(self.voxels, zet.variables, expr, self.variables)
            if expr == true:
                return S.UniversalSet
            elif expr == false:
                return None
            else:
                return AbstractSet(zet.variables, expr)

        elif isinstance(zet, Set):
            zet = marchingsetsimp(self.voxels, zet, self.variables)
            if zet == S.EmptySet:
                return None
            else:
                return zet

        else:
            return zet

def cube_engine(r=2, n=10):
    return MarchingCubesSolidEngine(cube_voxels(r, n))

