from itertools import product, islice
from functools import reduce
from operator import and_, or_
from sympy.core.compatibility import lru_cache
from sympy.sets import Set, Intersection, Union, Complement
from sympy.utilities import lambdify
from symplus.setplus import AbstractSet, as_abstract, AbsoluteComplement
from magicpy.solid.general import SolidEngine
from magicpy.util import map, range


def setbit1(bits, index):
    return bits|(1<<index)

def setbit0(bits, index):
    return bits&~(1<<index)

def getbit(bits, index):
    return bits&(1<<index) != 0

def bitcount(bits):
    if bits < 0:
        return -bitcount(~bits)
    else:
        return bin(bits).count("1")

def bitmap(func, voxels):
    bits = 0
    t = 1
    for elem in voxels:
        if func(elem):
            bits |= t
        t <<= 1
    return bits

class Voxels(object):
    def __init__(self, iter_gen, length, dv):
        self._iter_gen = iter_gen
        self.length = length
        self.ran = ~((~1)<<length)
        self.dv = dv

    def __iter__(self):
        return islice(self._iter_gen(), self.length)

    def __len__(self):
        return self.length

def cube_voxels(r=2.0, n=10):
    rn = int(r*n)
    dr = 1.0/n
    gen = lambda: ((xn*dr, yn*dr, zn*dr)
                   for xn, yn, zn in product(range(-rn, rn+1), repeat=3))
    return Voxels(gen, (2*rn+1)**3, dr**3)


class VoxelEngine(SolidEngine):
    def __init__(self, voxels, operations=(Union, Intersection, AbsoluteComplement, Complement)):
        self.voxels = voxels
        self.operations = operations

    def construct(self, zet):
        if isinstance(zet, self.operations[0]):
            return self.fuse(map(self.construct, zet.args))
        elif isinstance(zet, self.operations[1]):
            return self.common(map(self.construct, zet.args))
        elif isinstance(zet, self.operations[2]):
            return self.complement(self.construct(zet.args[0]))
        elif len(self.operations) > 3 and isinstance(zet, self.operations[3]):
            return self.cut(*map(self.construct, zet.args))
        elif isinstance(zet, Set):
            return self._construct(zet)
        else:
            raise TypeError

    @lru_cache(maxsize=128)
    def _construct(self, zet):
        if not isinstance(zet, AbstractSet):
            zet = as_abstract(zet)
        var = zet.variables
        expr = zet.expr
        func = lambdify(var, expr)
        if len(var) == 1:
            return bitmap(func, self.voxels)
        else:
            return bitmap(lambda v: func(*v), self.voxels)

    def common(self, objs):
        return reduce(and_, objs)

    def fuse(self, objs):
        return reduce(or_, objs)

    def complement(self, obj):
        return ~obj

    def cut(self, obj1, obj2):
        return obj1 & ~obj2

    def is_null(self, obj):
        return obj == 0

    def is_outside(self, obj, reg):
        return obj&reg == 0

    def is_inside(self, obj, reg):
        return obj&~reg == 0

    def is_equal(self, obj1, obj2):
        return obj1 == obj2

    def volume_of(self, obj):
        return self.voxels.dv * bitcount(obj)

def cube_engine(r=2.0, n=10):
    return VoxelEngine(cube_voxels(r, n))

