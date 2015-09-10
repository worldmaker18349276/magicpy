from itertools import product
from functools import lru_cache, reduce
from operator import and_, or_, xor
from sympy.core import S
from sympy.logic import Not, And, Or, Xor, Implies, Equivalent
from sympy.logic.boolalg import true, false, Boolean, is_nnf
from sympy.utilities import lambdify
from magicball.symplus.relplus import logicrelsimp
from magicball.symplus.setplus import AbstractSet
from magicball.engine.basic import Engine


def setbit1(bits, index):
    return bits|(1<<index)

def setbit0(bits, index):
    return bits&~(1<<index)

def getbit(bits, index):
    return bits&(1<<index) != 0

def bitmap(func, sample):
    bits = 0
    t = 1
    for elem in sample:
        if func(elem):
            bits |= t
        t <<= 1
    return bits

class SpaceSample:
    def __init__(self, iter_getter, length):
        self._getter = iter_getter
        self.length = length
        self.ran = ~((~1)<<length)

    def __iter__(self):
        return self._getter()

    def __len__(self):
        return self.length

    @lru_cache(maxsize=128)
    def _get_bits(self, var, expr):
        func = lambdify(var, expr)
        if len(var) == 1:
            return bitmap(func, self)
        else:
            return bitmap(lambda v: func(*v), self)

    def get_bits(self, var, expr):
        if isinstance(expr, And):
            return reduce(and_, (self.get_bits(var, e) for e in expr.args))
        elif isinstance(expr, Or):
            return reduce(or_, (self.get_bits(var, e) for e in expr.args))
        elif isinstance(expr, Not):
            return self.ran &~self.get_bits(var, expr.args[0])
        elif isinstance(expr, Xor):
            return reduce(xor, (self.get_bits(var, e) for e in expr.args))
        elif isinstance(expr, (Implies, Equivalent)):
            return self.get_bits(var, expr.to_nnf(simplify=False))
        elif isinstance(expr, Boolean):
            return self._get_bits(var, expr)
        else:
            raise TypeError

    def bits_of_set(self, aset):
        if not isinstance(aset, AbstractSet):
            raise TypeError
        return self.get_bits(aset.variables, aset.expr)

def cube_sample(length=2, n=10):
    def sample_iter():
        return map(lambda v: (v[0]/n, v[1]/n, v[2]/n),
                   product(range(-length*n, length*n+1), repeat=3))
    return SpaceSample(sample_iter, (2*length*n+1)**3)


def And_(*args):
    if len(args) > 1:
        return And(*args, evaluate=False)
    elif len(args) == 1:
        return args[0]
    else:
        return true

def Or_(*args):
    if len(args) > 1:
        return V(*args, evaluate=False)
    elif len(args) == 1:
        return args[0]
    else:
        return false

def spfuncsimp(sample, var, expr, ran=None):
    """
    >>> from sympy import *
    >>> from magicball.symplus.setplus import *
    >>> x, y, z = symbols('x y z', real=True)
    >>> sample = cube_sample(2,10)
    >>> s1 = x*2+y-z>0
    >>> s2 = x*2+y-z>1
    >>> s12 = s1 & s2; s12
    And(2*x + y - z > 0, 2*x + y - z > 1)
    >>> spfuncsimp(sample, (x,y,z), s12)
    2*x + y - z > 1
    >>> s3 = x+2*y>0
    >>> s4 = x-2*y>0
    >>> s5 = 2*x+y>-1
    >>> s345 = s3 & s4 & s5
    >>> spfuncsimp(sample, (x,y,z), s345)
    And(x + 2*y > 0, x - 2*y > 0)
    >>> s6 = 2*x+y<-1
    >>> s346 = s3 & s4 & s6
    >>> spfuncsimp(sample, (x,y,z), s346)
    False
    """
    if not isinstance(expr, Boolean):
        raise TypeError('expr is not Boolean: %r' % expr)

    if expr in (true, false):
        return expr

    if not is_nnf(expr, False):
        raise TypeError('expr is not nnf: %r' % expr)

    if ran is None:
        ran = sample.ran

    bits = sample.get_bits(var, expr) & ran
    if bits == 0:
        return false
    elif bits == ran:
        return true

    if isinstance(expr, And):
        # select important arguments
        args = []
        for arg in expr.args:
            args_ = set(expr.args) - {arg}
            bits_ = sample.get_bits(var, And_(*args_)) & ran
            if bits_ != bits:
                args.append(arg)

        # simplify remaining arguments
        for i in range(len(args)):
            args_ = set(args) - {args[i]}
            ran_ = ran & sample.get_bits(var, And_(*args_))
            args[i] = spfuncsimp(sample, var, args[i], ran_)
        return And_(*args)

    elif isinstance(expr, Or):
        # select important arguments
        args = []
        for arg in expr.args:
            args_ = set(expr.args) - {arg}
            bits_ = sample.get_bits(var, Or_(*args_)) & ran
            if bits_ != bits:
                args.append(arg)

        # simplify remaining arguments
        for i in range(len(args)):
            args_ = set(args) - {args[i]}
            ran_ = ran &~sample.get_bits(Or_(*args_))
            args[i] = spfuncsimp(sample, var, args[i], ran_)
        return Or_(*args)

    else:
        return expr


class SpaceSampleEngine(Engine):
    def __init__(self, sample):
        self.sample = sample

    def is_disjoint(self, aset1, aset2):
        return self.sample.bits_of_set(aset1) & self.sample.bits_of_set(aset2) == 0

    def is_subset(self, aset1, aset2):
        return self.sample.bits_of_set(aset1) &~self.sample.bits_of_set(aset2) == 0

    def equal(self, aset1, aset2):
        return self.sample.bits_of_set(aset1) == self.sample.bits_of_set(aset2)

    def simp(self, aset):
        aset = aset.doit()
        if isinstance(aset, AbstractSet):
            expr = logicrelsimp(aset.expr)
            expr = spfuncsimp(self.sample, aset.variables, expr)
            if expr == true:
                return S.UniversalSet
            elif expr == false:
                return S.EmptySet
            else:
                return AbstractSet(aset.variables, expr)
        else:
            return aset

def cube_engine(length=2, n=10):
    return SpaceSampleEngine(cube_sample(length, n))

