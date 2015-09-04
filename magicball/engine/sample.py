from itertools import product, combinations
from functools import lru_cache, reduce
from operator import and_, or_
from sympy.sets import Set, Intersection, Union, Complement, EmptySet
from sympy.sets.sets import UniversalSet
from sympy.utilities import lambdify
from magicball.symplus.relplus import logicrelsimp
from magicball.symplus.setplus import AbstractSet


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
        self.ran = ~(-2<<length)

    def __iter__(self):
        return self._getter()

    def __len__(self):
        return self.length

    @lru_cache(maxsize=128)
    def _get_bits(self, aset):
        if isinstance(aset, AbstractSet):
            f = lambdify(aset.variables, aset.expr)
            if len(aset.variables) == 1:
                return bitmap(f, self)
            else:
                return bitmap(lambda v: f(*v), self)
        else:
            return bitmap(lambda v: v in aset, self)

    def get_bits(self, aset):
        if isinstance(aset, Intersection):
            return reduce(and_, map(self.get_bits, aset.args))
        elif isinstance(aset, Union):
            return reduce(or_, map(self.get_bits, aset.args))
        elif isinstance(aset, Complement):
            return self.get_bits(aset.args[0]) &~self.get_bits(aset.args[1])
        elif isinstance(aset, EmptySet):
            return 0
        elif isinstance(aset, UniversalSet):
            return self.ran
        elif isinstance(aset, Set):
            return self._get_bits(aset)
        else:
            raise TypeError

def cube_sample(length=2, n=10):
    def sample_iter():
        return map(lambda v: (v[0]/n, v[1]/n, v[2]/n),
                   product(range(-length*n, length*n+1), repeat=3))
    return SpaceSample(sample_iter, (2*length*n+1)**3)


def n_(*args):
    if len(args) > 1:
        return Intersection(*args, evaluate=False)
    elif len(args) == 1:
        return args[0]
    else:
        return UniversalSet()

def u_(*args):
    if len(args) > 1:
        return Union(*args, evaluate=False)
    elif len(args) == 1:
        return args[0]
    else:
        return EmptySet()

def spsetsimp(sample, aset, ran=None):
    """
    >>> from sympy import *
    >>> from magicball.symplus.setplus import *
    >>> x, y, z = symbols('x y z', real=True)
    >>> sample = cube_sample(2,10)
    >>> s1 = AbstractSet((x,y,z), x*2+y-z>0)
    >>> s2 = AbstractSet((x,y,z), x*2+y-z>1)
    >>> s12 = Intersection(s1, s2, evaluate=False); s12
    Intersection(AbstractSet((x, y, z), 2*x + y - z > 0), \
AbstractSet((x, y, z), 2*x + y - z > 1))
    >>> spsetsimp(sample, s12)
    AbstractSet((x, y, z), 2*x + y - z > 1)
    >>> s3 = AbstractSet((x,y,z), x+2*y>0)
    >>> s4 = AbstractSet((x,y,z), x-2*y>0)
    >>> s5 = AbstractSet((x,y,z), 2*x+y>-1)
    >>> s345 = Intersection(s3, s4, s5, evaluate=False)
    >>> spsetsimp(sample, s345)
    Intersection(AbstractSet((x, y, z), x - 2*y > 0), \
AbstractSet((x, y, z), x + 2*y > 0))
    >>> s6 = AbstractSet((x,y,z), 2*x+y<-1)
    >>> s346 = Intersection(s3, s4, s6, evaluate=False)
    >>> spsetsimp(sample, s346)
    EmptySet()
    """
    if not isinstance(aset, Set):
        raise TypeError('aset is not set: %r' % aset)

    if isinstance(aset, (EmptySet, UniversalSet)):
        return aset

    if ran is None:
        ran = sample.ran

    bits = sample.get_bits(aset) & ran
    if bits == 0:
        return EmptySet()
    elif bits == ran:
        return UniversalSet()

    if isinstance(aset, Intersection):
        # select important arguments
        args = []
        for arg in aset.args:
            args_ = set(aset.args) - {arg}
            bits_ = sample.get_bits(n_(*args_)) & ran
            if bits_ != bits:
                args.append(arg)

        # simplify arguments
        for i in range(len(args)):
            args_ = set(args) - {args[i]}
            ran_ = ran & sample.get_bits(n_(*args_))
            args[i] = spsetsimp(sample, args[i], ran_)
        return n_(*args)

    elif isinstance(aset, Union):
        # select important arguments
        args = []
        for arg in aset.args:
            args_ = set(aset.args) - {arg}
            bits_ = sample.get_bits(u_(*args_)) & ran
            if bits_ != bits:
                args.append(arg)

        # simplify arguments
        for i in range(len(args)):
            args_ = set(args) - {args[i]}
            ran_ = ran &~sample.get_bits(n_(*args_))
            args[i] = spsetsimp(sample, args[i], ran_)
        return u_(*args)

    else:
        return aset


class SpaceSampleEngine:
    def __init__(self, sample=cube_sample()):
        self.sample = sample

    def is_disjoint(self, aset1, aset2):
        return self.sample.get_bits(aset1) & self.sample.get_bits(aset2) == 0

    def is_subset(self, aset1, aset2):
        return self.sample.get_bits(aset1) &~self.sample.get_bits(aset2) == 0

    def equal(self, aset1, aset2):
        return self.sample.get_bits(aset1) == self.sample.get_bits(aset2)

    def simp(self, aset):
        aset = aset.doit()
        expr = logicrelsimp(aset.expr)
        aset = AbstractSet(aset.variables, expr)
        aset = aset.expand()
        aset = spsetsimp(self.sample, aset)
        return aset

