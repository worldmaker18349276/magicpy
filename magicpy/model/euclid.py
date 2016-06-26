from sympy.core import Basic, S, sympify, symbols
from sympy.core.singleton import Singleton
from sympy.simplify import simplify
from sympy.logic import true
from sympy.sets import Set, Intersection, Union, Complement
from sympy.matrices.immutable import ImmutableMatrix as Mat
from symplus.util import *
from symplus.setplus import AbstractSet
from symplus.topoplus import NaturalTopology, AbsoluteComplement, Exterior
from symplus.matplus import norm, normalize, dot, cross, project, i, j, k, x, y, z, r


# primitive sets

class EuclideanSpace(Set):
    def _complement(self, other):
        if isinstance(other, EuclideanSpace):
            if hasattr(other, '_absolute_complement'):
                self_ = self._absolute_complement()
            if self_ is not None:
                return Intersection(self_, other, evaluate=True)

    def _union(self, other):
        if isinstance(other, WholeSpace):
            return other

    def _intersect(self, other):
        if isinstance(other, WholeSpace):
            return self

class WholeSpace(EuclideanSpace, metaclass=Singleton):
    def _absolute_complement(self):
        return S.EmptySet

    def _union(self, other):
        if isinstance(other, EuclideanSpace):
            return self

    def _intersect(self, other):
        if isinstance(other, EuclideanSpace):
            return other

    def _contains(self, other):
        return is_Tuple(other) and len(other) == 3

    def as_abstract(self):
        return AbstractSet(symbols('x y z', real=True), true)

    @property
    def interior(self):
        return self

    @property
    def closure(self):
        return self

    @property
    def is_open(self):
        return True

    @property
    def is_closed(self):
        return True

class Halfspace(EuclideanSpace):
    def __new__(cls, direction=[1,0,0], offset=0, closed=False, normalization=True):
        """
        >>> from sympy import *
        >>> from symplus.strplus import mprint
        >>> mprint(Halfspace())
        Halfspace([1, 0, 0]', 0, False)
        >>> mprint(Halfspace([1,2,0], 3))
        Halfspace([sqrt(5)/5, 2*sqrt(5)/5, 0]', 3, False)
        >>> Halfspace().contains((1,2,3))
        True
        >>> Halfspace([1,2,0], 3).contains((1,2,3))
        False
        """
        direction = Mat(direction)
        if normalization:
            if norm(direction) == 0:
                raise ValueError
            direction = simplify(normalize(direction))
        offset = sympify(offset)
        closed = sympify(bool(closed))
        return Basic.__new__(cls, direction, offset, closed)

    @property
    def direction(self):
        return self.args[0]

    @property
    def offset(self):
        return self.args[1]

    @property
    def closed(self):
        return self.args[2]

    def _contains(self, other):
        if not is_Tuple(other) or len(other) != 3:
            return false
        v = Mat(other)
        if self.closed:
            return dot(v, self.direction) >= self.offset
        else:
            return dot(v, self.direction) > self.offset

    def as_abstract(self):
        """
        >>> from sympy import *
        >>> Halfspace().as_abstract()
        AbstractSet((x, y, z), x > 0)
        >>> Halfspace([1,2,0], 3).as_abstract()
        AbstractSet((x, y, z), sqrt(5)*x/5 + 2*sqrt(5)*y/5 > 3)
        """
        if self.closed:
            expr = dot(r, self.direction) >= self.offset
        else:
            expr = dot(r, self.direction) > self.offset
        return AbstractSet((x,y,z), expr)

    def _absolute_complement(self):
        """
        >>> from sympy import *
        >>> from symplus.strplus import mprint
        >>> mprint(AbsoluteComplement(Halfspace()))
        Halfspace([-1, 0, 0]', 0, True)
        >>> mprint(AbsoluteComplement(Halfspace([1,2,0], 3)))
        Halfspace([-sqrt(5)/5, -2*sqrt(5)/5, 0]', -3, True)
        >>> AbsoluteComplement(Halfspace()).contains((1,2,3))
        False
        >>> AbsoluteComplement(Halfspace([1,2,0], 3)).contains((1,2,3))
        True
        """
        return Halfspace(direction=-self.direction,
                         offset=-self.offset,
                         closed=~self.closed)

    @property
    def interior(self):
        return Halfspace(direction=self.direction,
                         offset=self.offset,
                         closed=false)

    @property
    def closure(self):
        return Halfspace(direction=self.direction,
                         offset=self.offset,
                         closed=true)

    @property
    def is_open(self):
        return ~self.closed

    @property
    def is_closed(self):
        return self.closed

class Sphere(EuclideanSpace):
    def __new__(cls, radius=1, center=[0,0,0], closed=False, normalization=True):
        """
        >>> from sympy import *
        >>> from symplus.strplus import mprint
        >>> mprint(Sphere())
        Sphere(1, [0, 0, 0]', False)
        >>> mprint(Sphere(3, [1,0,2]))
        Sphere(3, [1, 0, 2]', False)
        >>> Sphere().contains((1,1,1))
        False
        >>> Sphere(3, [1,0,2]).contains((1,1,1))
        True
        """
        radius = sympify(radius)
        center = Mat(center)
        closed = sympify(bool(closed))
        return Basic.__new__(cls, radius, center, closed)

    @property
    def radius(self):
        return self.args[0]

    @property
    def center(self):
        return self.args[1]

    @property
    def closed(self):
        return self.args[2]

    def _contains(self, other):
        if not is_Tuple(other) or len(other) != 3:
            return false
        v = Mat(other)

        if self.closed:
            if self.radius > 0:
                return norm(v-self.center)**2 <= self.radius**2
            else:
                return norm(v-self.center)**2 >= self.radius**2
        else:
            if self.radius > 0:
                return norm(v-self.center)**2 < self.radius**2
            else:
                return norm(v-self.center)**2 > self.radius**2

    def as_abstract(self):
        """
        >>> from sympy import *
        >>> Sphere().as_abstract()
        AbstractSet((x, y, z), x**2 + y**2 + z**2 < 1)
        >>> Sphere(3, [1,0,2]).as_abstract()
        AbstractSet((x, y, z), y**2 + (x - 1)**2 + (z - 2)**2 < 9)
        """
        if self.closed:
            if self.radius > 0:
                expr = norm(r-self.center)**2 <= self.radius**2
            else:
                expr = norm(r-self.center)**2 >= self.radius**2
        else:
            if self.radius > 0:
                expr = norm(r-self.center)**2 < self.radius**2
            else:
                expr = norm(r-self.center)**2 > self.radius**2
        return AbstractSet((x,y,z), expr)

    def _absolute_complement(self):
        """
        >>> from sympy import *
        >>> from symplus.strplus import mprint
        >>> mprint(AbsoluteComplement(Sphere()))
        Sphere(-1, [0, 0, 0]', True)
        >>> mprint(AbsoluteComplement(Sphere(3, [1,0,2])))
        Sphere(-3, [1, 0, 2]', True)
        >>> AbsoluteComplement(Sphere()).contains((1,1,1))
        True
        >>> AbsoluteComplement(Sphere(3, [1,0,2])).contains((1,1,1))
        False
        """
        return Sphere(radius=-self.radius,
                         center=self.center,
                         closed=~self.closed)

    @property
    def interior(self):
        return Sphere(radius=self.radius,
                         center=self.center,
                         closed=false)

    @property
    def closure(self):
        return Sphere(radius=self.radius,
                         center=self.center,
                         closed=true)

    @property
    def is_open(self):
        return ~self.closed

    @property
    def is_closed(self):
        return self.closed

class InfiniteCylinder(EuclideanSpace):
    def __new__(cls, direction=[1,0,0], radius=1, center=[0,0,0], closed=False, normalization=True):
        """
        >>> from sympy import *
        >>> from symplus.strplus import mprint
        >>> mprint(InfiniteCylinder())
        InfiniteCylinder([1, 0, 0]', 1, [0, 0, 0]', False)
        >>> mprint(InfiniteCylinder([0,1,1], 2))
        InfiniteCylinder([0, sqrt(2)/2, sqrt(2)/2]', 2, [0, 0, 0]', False)
        >>> InfiniteCylinder().contains((1,1,1))
        False
        >>> InfiniteCylinder([0,1,1], 2).contains((1,1,1))
        True
        """
        direction = Mat(direction)
        if normalization:
            if norm(direction) == 0:
                raise ValueError
            direction = simplify(normalize(direction))
        direction = max(direction, -direction, key=tuple)
        radius = sympify(radius)
        center = Mat(center)
        if normalization:
            center = simplify(center - project(center, direction))
        closed = sympify(bool(closed))
        return Basic.__new__(cls, direction, radius, center, closed)

    @property
    def direction(self):
        return self.args[0]

    @property
    def radius(self):
        return self.args[1]

    @property
    def center(self):
        return self.args[2]

    @property
    def closed(self):
        return self.args[3]

    def _contains(self, other):
        if not is_Tuple(other) or len(other) != 3:
            return false
        v = Mat(other)
        p = v - self.center
        if self.closed:
            if self.radius > 0:
                return norm(cross(p, self.direction))**2 <= self.radius**2
            else:
                return norm(cross(p, self.direction))**2 >= self.radius**2
        else:
            if self.radius > 0:
                return norm(cross(p, self.direction))**2 < self.radius**2
            else:
                return norm(cross(p, self.direction))**2 > self.radius**2

    def as_abstract(self):
        """
        >>> from sympy import *
        >>> InfiniteCylinder().as_abstract()
        AbstractSet((x, y, z), y**2 + z**2 < 1)
        >>> InfiniteCylinder([0,1,1], 2).as_abstract()
        AbstractSet((x, y, z), x**2 + (sqrt(2)*y/2 - sqrt(2)*z/2)**2 < 4)
        """
        p = r - self.center
        if self.closed:
            if self.radius > 0:
                expr = norm(cross(p, self.direction))**2 <= self.radius**2
            else:
                expr = norm(cross(p, self.direction))**2 >= self.radius**2
        else:
            if self.radius > 0:
                expr = norm(cross(p, self.direction))**2 < self.radius**2
            else:
                expr = norm(cross(p, self.direction))**2 > self.radius**2
        return AbstractSet((x,y,z), expr)

    def _absolute_complement(self):
        """
        >>> from sympy import *
        >>> from symplus.strplus import mprint
        >>> mprint(AbsoluteComplement(InfiniteCylinder()))
        InfiniteCylinder([1, 0, 0]', -1, [0, 0, 0]', True)
        >>> mprint(AbsoluteComplement(InfiniteCylinder([0,1,1], 2)))
        InfiniteCylinder([0, sqrt(2)/2, sqrt(2)/2]', -2, [0, 0, 0]', True)
        >>> AbsoluteComplement(InfiniteCylinder()).contains((1,1,1))
        True
        >>> AbsoluteComplement(InfiniteCylinder([0,1,1], 2)).contains((1,1,1))
        False
        """
        return InfiniteCylinder(direction=self.direction,
                        radius=-self.radius,
                        center=self.center,
                        closed=~self.closed)

    @property
    def interior(self):
        return InfiniteCylinder(direction=self.direction,
                        radius=self.radius,
                        center=self.center,
                        closed=false)

    @property
    def closure(self):
        return InfiniteCylinder(direction=self.direction,
                        radius=self.radius,
                        center=self.center,
                        closed=true)

    @property
    def is_open(self):
        return ~self.closed

    @property
    def is_closed(self):
        return self.closed

class InfiniteCone(EuclideanSpace):
    def __new__(cls, direction=[1,0,0], slope=1, center=[0,0,0], closed=False, normalization=True):
        """
        >>> from sympy import *
        >>> from symplus.strplus import mprint
        >>> mprint(InfiniteCone())
        InfiniteCone([1, 0, 0]', 1, [0, 0, 0]', False)
        >>> mprint(InfiniteCone([3,4,0], 5))
        InfiniteCone([3/5, 4/5, 0]', 5, [0, 0, 0]', False)
        >>> InfiniteCone().contains((-1,0,1))
        False
        >>> InfiniteCone([3,4,0], 5).contains((-1,0,1))
        True
        """
        direction = Mat(direction)
        if normalization:
            if norm(direction) == 0:
                raise ValueError
            direction = simplify(normalize(direction))
        direction = max(direction, -direction, key=tuple)
        slope = sympify(slope)
        center = Mat(center)
        closed = sympify(bool(closed))
        return Basic.__new__(cls, direction, slope, center, closed)

    @property
    def direction(self):
        return self.args[0]

    @property
    def slope(self):
        return self.args[1]

    @property
    def center(self):
        return self.args[2]

    @property
    def closed(self):
        return self.args[3]

    def _contains(self, other):
        if not is_Tuple(other) or len(other) != 3:
            return false
        v = Mat(other)
        p = v - self.center
        if self.closed:
            if self.slope > 0:
                return norm(cross(p, self.direction))**2 <= (self.slope*dot(p, self.direction))**2
            else:
                return norm(cross(p, self.direction))**2 >= (self.slope*dot(p, self.direction))**2
        else:
            if self.slope > 0:
                return norm(cross(p, self.direction))**2 < (self.slope*dot(p, self.direction))**2
            else:
                return norm(cross(p, self.direction))**2 > (self.slope*dot(p, self.direction))**2

    def as_abstract(self):
        """
        >>> from sympy import *
        >>> InfiniteCone().as_abstract()
        AbstractSet((x, y, z), y**2 + z**2 < x**2)
        >>> InfiniteCone([3,4,0], 5).as_abstract()
        AbstractSet((x, y, z), z**2 + (4*x/5 - 3*y/5)**2 < (3*x + 4*y)**2)
        """
        p = r - self.center
        if self.closed:
            if self.slope > 0:
                expr = norm(cross(p, self.direction))**2 <= (self.slope*dot(p, self.direction))**2
            else:
                expr = norm(cross(p, self.direction))**2 >= (self.slope*dot(p, self.direction))**2
        else:
            if self.slope > 0:
                expr = norm(cross(p, self.direction))**2 < (self.slope*dot(p, self.direction))**2
            else:
                expr = norm(cross(p, self.direction))**2 > (self.slope*dot(p, self.direction))**2
        return AbstractSet((x,y,z), expr)

    def _absolute_complement(self):
        """
        >>> from sympy import *
        >>> from symplus.strplus import mprint
        >>> mprint(AbsoluteComplement(InfiniteCone()))
        InfiniteCone([1, 0, 0]', -1, [0, 0, 0]', True)
        >>> mprint(AbsoluteComplement(InfiniteCone([3,4,0], 5)))
        InfiniteCone([3/5, 4/5, 0]', -5, [0, 0, 0]', True)
        >>> AbsoluteComplement(InfiniteCone()).contains((-1,0,1))
        True
        >>> AbsoluteComplement(InfiniteCone([3,4,0], 5)).contains((-1,0,1))
        False
        """
        return InfiniteCone(direction=self.direction,
                    slope=-self.slope,
                    center=self.center,
                    closed=~self.closed)

    @property
    def interior(self):
        return InfiniteCone(direction=self.direction,
                    slope=self.slope,
                    center=self.center,
                    closed=false)

    @property
    def closure(self):
        return InfiniteCone(direction=self.direction,
                    slope=self.slope,
                    center=self.center,
                    closed=true)

    @property
    def is_open(self):
        return ~self.closed

    @property
    def is_closed(self):
        return self.closed

class Revolution(EuclideanSpace):
    def __new__(cls, func, direction=[1,0,0], center=[0,0,0], normalization=True):
        direction = Mat(direction)
        if norm(direction) == 0:
            raise ValueError
        direction = normalize(direction)
        center = Mat(center)
        return Basic.__new__(cls, func, direction, center)

    @property
    def func(self):
        return self.args[0]

    @property
    def direction(self):
        return self.args[1]

    @property
    def center(self):
        return self.args[2]

    def _contains(self, other):
        if not is_Tuple(other) or len(other) != 3:
            return false
        v = Mat(other)
        p = v - self.center
        return self.func(dot(p, self.direction), norm(cross(p, self.direction)))

    def as_abstract(self):
        """
        >>> from sympy import *
        >>> Revolution(lambda h, s: h**2<s**2).as_abstract()
        AbstractSet((x, y, z), x**2 < y**2 + z**2)
        >>> Revolution(lambda h, s: h+1<s**2, [3,4,0]).as_abstract()
        AbstractSet((x, y, z), 3*x/5 + 4*y/5 + 1 < z**2 + (4*x/5 - 3*y/5)**2)
        """
        p = r - self.center
        expr = self.func(dot(p, self.direction), norm(cross(p, self.direction)))
        return AbstractSet((x,y,z), expr)

# topology of Euclidean Space

class EuclideanTopology(NaturalTopology, metaclass=Singleton):
    def __new__(cls):
        return Set.__new__(cls)

    space = WholeSpace()

T_RR3 = EuclideanTopology()


# useful constructors

def cube(size=[2,2,2]):
    return Intersection(
        Halfspace(direction=+i, offset=-size[0]/2, closed=False, normalization=False),
        Halfspace(direction=+j, offset=-size[1]/2, closed=False, normalization=False),
        Halfspace(direction=+k, offset=-size[2]/2, closed=False, normalization=False),
        Halfspace(direction=-i, offset=-size[0]/2, closed=False, normalization=False),
        Halfspace(direction=-j, offset=-size[1]/2, closed=False, normalization=False),
        Halfspace(direction=-k, offset=-size[2]/2, closed=False, normalization=False))

def sphere(radius=1):
    return Sphere(radius=radius, center=[0,0,0], closed=False)

def cylinder(radius=1, height=2):
    return Intersection(
        InfiniteCylinder(direction=i, radius=radius, center=[0,0,0], closed=False, normalization=False),
        Halfspace(direction=+i, offset=-height/2, closed=False, normalization=False),
        Halfspace(direction=-i, offset=-height/2, closed=False, normalization=False))

def cone(radius=1, height=1):
    return Intersection(
        InfiniteCone(direction=i, slope=radius/height, center=[0,0,0], closed=False, normalization=False),
        Halfspace(direction=+i, offset=0, closed=False, normalization=False),
        Halfspace(direction=-i, offset=-height, closed=False, normalization=False))

def with_exterior(zet):
    return (zet, Exterior(zet))

