from itertools import product
from functools import lru_cache, reduce
from operator import and_, or_, xor
from sympy.core import S
from sympy.sets import Set, Intersection, Union, Complement
from sympy.logic import Not, And, Or, Xor, Implies, Equivalent
from sympy.logic.boolalg import true, false, Boolean, is_nnf
from sympy.utilities import lambdify
from symplus.simplus import logicrelsimp
from symplus.setplus import AbstractSet
from magicpy.engine.basic import Engine


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
    def _bits_of_set(self, aset):
        if isinstance(aset, AbstractSet):
            var = aset.variables
            expr = aset.expr
            func = lambdify(var, expr)
            if len(var) == 1:
                return bitmap(func, self)
            else:
                return bitmap(lambda v: func(*v), self)
        else:
            return bitmap(aset.__contains__, self)

    def bits_of_set(self, aset):
        if isinstance(aset, Intersection):
            return reduce(and_, (self.bits_of_set(e) for e in aset.args))
        elif isinstance(aset, Union):
            return reduce(or_, (self.bits_of_set(e) for e in aset.args))
        elif isinstance(aset, Complement):
            return self.bits_of_set(aset.args[0]) &~self.bits_of_set(aset.args[1])
        elif isinstance(aset, AbstractSet):
            return self.bits_of_expr(aset.variables, aset.expr)
        else:
            return self._bits_of_set(aset)

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

def cube_voxels(length=2, n=10):
    def voxels_iter_getter():
        return map(lambda v: (v[0]/n, v[1]/n, v[2]/n),
                   product(range(-length*n, length*n+1), repeat=3))
    return Voxels(voxels_iter_getter, (2*length*n+1)**3)


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

def marchingsetsimp(voxels, aset, ran=None):
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
    if not isinstance(aset, Set):
        raise TypeError('aset is not Set: %r' % aset)

    if aset in (S.EmptySet, S.UniversalSet):
        return aset

    if aset.has(Complement):
        raise TypeError('aset is not nnf: %r' % aset)

    if ran is None:
        ran = voxels.ran

    bits = voxels.bits_of_set(aset) & ran
    if bits == 0:
        return S.EmptySet
    elif bits == ran:
        return S.UniversalSet

    if isinstance(aset, Intersection):
        # select important arguments
        args = []
        for arg in aset.args:
            args_ = set(aset.args) - {arg}
            bits_ = voxels.bits_of_set(Intersection_(*args_)) & ran
            if bits_ != bits:
                args.append(arg)

        # simplify remaining arguments
        for i in range(len(args)):
            args_ = set(args) - {args[i]}
            ran_ = ran & voxels.bits_of_set(Intersection_(*args_))
            args[i] = marchingsetsimp(voxels, args[i], ran_)
        return Intersection_(*args)

    elif isinstance(aset, Union):
        # select important arguments
        args = []
        for arg in aset.args:
            args_ = set(aset.args) - {arg}
            bits_ = voxels.bits_of_set(Union_(*args_)) & ran
            if bits_ != bits:
                args.append(arg)

        # simplify remaining arguments
        for i in range(len(args)):
            args_ = set(args) - {args[i]}
            ran_ = ran &~voxels.bits_of_set(Union_(*args_))
            args[i] = marchingsetsimp(voxels, args[i], ran_)
        return Union_(*args)

    else:
        return aset

def marchingfuncsimp(voxels, var, expr, ran=None):
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

    if expr in (true, false):
        return expr

    if not is_nnf(expr, False):
        raise TypeError('expr is not nnf: %r' % expr)

    if ran is None:
        ran = voxels.ran

    bits = voxels.bits_of_expr(var, expr) & ran
    if bits == 0:
        return false
    elif bits == ran:
        return true

    if isinstance(expr, And):
        # select important arguments
        args = []
        for arg in expr.args:
            args_ = set(expr.args) - {arg}
            bits_ = voxels.bits_of_expr(var, And_(*args_)) & ran
            if bits_ != bits:
                args.append(arg)

        # simplify remaining arguments
        for i in range(len(args)):
            args_ = set(args) - {args[i]}
            ran_ = ran & voxels.bits_of_expr(var, And_(*args_))
            args[i] = marchingfuncsimp(voxels, var, args[i], ran_)
        return And_(*args)

    elif isinstance(expr, Or):
        # select important arguments
        args = []
        for arg in expr.args:
            args_ = set(expr.args) - {arg}
            bits_ = voxels.bits_of_expr(var, Or_(*args_)) & ran
            if bits_ != bits:
                args.append(arg)

        # simplify remaining arguments
        for i in range(len(args)):
            args_ = set(args) - {args[i]}
            ran_ = ran &~voxels.bits_of_expr(Or_(*args_))
            args[i] = marchingfuncsimp(voxels, var, args[i], ran_)
        return Or_(*args)

    else:
        return expr


class MarchingCubesEngine(Engine):
    def __init__(self, voxels):
        self.voxels = voxels

    def is_disjoint(self, aset1, aset2):
        return self.voxels.bits_of_set(aset1) & self.voxels.bits_of_set(aset2) == 0

    def is_subset(self, aset1, aset2):
        return self.voxels.bits_of_set(aset1) &~self.voxels.bits_of_set(aset2) == 0

    def equal(self, aset1, aset2):
        return self.voxels.bits_of_set(aset1) == self.voxels.bits_of_set(aset2)

    def simp(self, aset):
        aset = aset.doit()
        if isinstance(aset, AbstractSet):
            expr = logicrelsimp(aset.expr)
            expr = marchingfuncsimp(self.voxels, aset.variables, expr)
            if expr == true:
                return S.UniversalSet
            elif expr == false:
                return S.EmptySet
            else:
                return AbstractSet(aset.variables, expr)
        else:
            return aset

def cube_engine(length=2, n=10):
    return MarchingCubesEngine(cube_voxels(length, n))

