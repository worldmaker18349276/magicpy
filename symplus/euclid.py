from sympy.core import Basic, S, sympify, symbols
from sympy.core.compatibility import with_metaclass
from sympy.core.singleton import Singleton
from sympy.simplify import simplify
from sympy.logic import false, true
from sympy.sets import Set, Intersection, Union, Complement, EmptySet
from sympy.matrices import eye
from symplus.typlus import is_Tuple
from symplus.strplus import mstr_inline_Matrix
from symplus.setplus import AbstractSet, as_abstract, NaturalTopology, AbsoluteComplement, Exterior
from symplus.matplus import Mat, norm, normalize, dot, cross, project, i, j, k, x, y, z, r


# primitive sets

class EuclideanSpace(Set):
    def _complement(self, other):
        if hasattr(self, '_absolute_complement'):
            self_ = self._absolute_complement()
        if self_ is not None:
            return Intersection(self_, other, evaluate=True)

    def _union(self, other):
        if isinstance(other, WholeSpace):
            return other

    def _intersect(self, other):
        if isinstance(other, WholeSpace):
            return self

class WholeSpace(with_metaclass(Singleton, EuclideanSpace)):
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

class AlgebraicEuclideanSpace(EuclideanSpace):
    pass

class BoundedEuclideanSpace(EuclideanSpace):
    pass

class Halfspace(AlgebraicEuclideanSpace):
    def __new__(cls, offset=0, direction=[0,0,1], closed=False, **kwargs):
        """
        >>> from sympy import *
        >>> from symplus.strplus import init_mprinting
        >>> init_mprinting()
        >>> Halfspace()
        Halfspace(0, [0 0 1]', False)
        >>> Halfspace(3, [1,2,0])
        Halfspace(3, [sqrt(5)/5 2*sqrt(5)/5 0]', False)
        >>> Halfspace().contains((1,2,3))
        True
        >>> Halfspace(3, [1,2,0]).contains((1,2,3))
        False
        """
        normalization = kwargs.pop("normalization", True)
        offset = sympify(offset)
        direction = Mat(direction)
        if normalization:
            if norm(direction) == 0:
                raise ValueError
            direction = simplify(normalize(direction))
        closed = sympify(bool(closed))
        return Basic.__new__(cls, offset, direction, closed)

    @property
    def offset(self):
        return self.args[0]

    @property
    def direction(self):
        return self.args[1]

    @property
    def closed(self):
        return self.args[2]

    def _sympystr(self, printer):
        return "%s(%s, %s, %s)"%(
            type(self).__name__,
            printer.doprint(self.offset), 
            printer.doprint(list(self.direction)),
            printer.doprint(self.closed))

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
        >>> from symplus.strplus import init_mprinting
        >>> init_mprinting()
        >>> Halfspace().as_abstract()
        {(x, y, z) | z > 0}
        >>> Halfspace(3, [1,2,0]).as_abstract()
        {(x, y, z) | sqrt(5)*x/5 + 2*sqrt(5)*y/5 > 3}
        """
        if self.closed:
            expr = dot(r, self.direction) >= self.offset
        else:
            expr = dot(r, self.direction) > self.offset
        return AbstractSet((x,y,z), expr)

    def _absolute_complement(self):
        """
        >>> from sympy import *
        >>> from symplus.strplus import init_mprinting
        >>> init_mprinting()
        >>> AbsoluteComplement(Halfspace())
        Halfspace(0, [0 0 -1]', True)
        >>> AbsoluteComplement(Halfspace(3, [1,2,0]))
        Halfspace(-3, [-sqrt(5)/5 -2*sqrt(5)/5 0]', True)
        >>> AbsoluteComplement(Halfspace()).contains((1,2,3))
        False
        >>> AbsoluteComplement(Halfspace(3, [1,2,0])).contains((1,2,3))
        True
        """
        return Halfspace(
            offset=-self.offset,
            direction=-self.direction,
            closed=~self.closed,
            normalization=False)

    @property
    def interior(self):
        return Halfspace(
            offset=self.offset,
            direction=self.direction,
            closed=false,
            normalization=False)

    @property
    def closure(self):
        return Halfspace(
            offset=self.offset,
            direction=self.direction,
            closed=true,
            normalization=False)

    @property
    def is_open(self):
        return ~self.closed

    @property
    def is_closed(self):
        return self.closed

class Sphere(AlgebraicEuclideanSpace, BoundedEuclideanSpace):
    def __new__(cls, radius=1, center=[0,0,0], closed=False, **kwargs):
        """
        >>> from sympy import *
        >>> from symplus.strplus import init_mprinting
        >>> init_mprinting()
        >>> Sphere()
        Sphere(1, [0 0 0]', False)
        >>> Sphere(3, [1,0,2])
        Sphere(3, [1 0 2]', False)
        >>> Sphere().contains((1,1,1))
        False
        >>> Sphere(3, [1,0,2]).contains((1,1,1))
        True
        """
        radius = sympify(abs(radius))
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

    def _sympystr(self, printer):
        return "%s(%s, %s, %s)"%(
            type(self).__name__,
            printer.doprint(self.radius),
            printer.doprint(list(self.center)),
            printer.doprint(self.closed))

    def _contains(self, other):
        if not is_Tuple(other) or len(other) != 3:
            return false
        v = Mat(other)

        if self.closed:
            return norm(v-self.center)**2 <= self.radius**2
        else:
            return norm(v-self.center)**2 < self.radius**2

    def as_abstract(self):
        """
        >>> from sympy import *
        >>> from symplus.strplus import init_mprinting
        >>> init_mprinting()
        >>> Sphere().as_abstract()
        {(x, y, z) | x**2 + y**2 + z**2 < 1}
        >>> Sphere(3, [1,0,2]).as_abstract()
        {(x, y, z) | y**2 + (x - 1)**2 + (z - 2)**2 < 9}
        """
        if self.closed:
            expr = norm(r-self.center)**2 <= self.radius**2
        else:
            expr = norm(r-self.center)**2 < self.radius**2
        return AbstractSet((x,y,z), expr)

    @property
    def interior(self):
        return Sphere(
            radius=self.radius,
            center=self.center,
            closed=false,
            normalization=False)

    @property
    def closure(self):
        return Sphere(
            radius=self.radius,
            center=self.center,
            closed=true,
            normalization=False)

    @property
    def is_open(self):
        return ~self.closed

    @property
    def is_closed(self):
        return self.closed

class InfiniteCylinder(AlgebraicEuclideanSpace):
    def __new__(cls, radius=1, center=[0,0,0], direction=[0,0,1], closed=False, **kwargs):
        """
        >>> from sympy import *
        >>> from symplus.strplus import init_mprinting
        >>> init_mprinting()
        >>> InfiniteCylinder()
        InfiniteCylinder(1, [0 0 0]', [0 0 1]', False)
        >>> InfiniteCylinder(2, [0,0,0], [0,1,1])
        InfiniteCylinder(2, [0 0 0]', [0 sqrt(2)/2 sqrt(2)/2]', False)
        >>> InfiniteCylinder().contains((1,1,1))
        False
        >>> InfiniteCylinder(2, [0,0,0], [0,1,1]).contains((1,1,1))
        True
        """
        normalization = kwargs.pop("normalization", True)
        radius = sympify(abs(radius))
        direction = Mat(direction)
        if normalization:
            if norm(direction) == 0:
                raise ValueError
            direction = simplify(normalize(direction))
        direction = max(direction, -direction, key=tuple)
        center = Mat(center)
        if normalization:
            center = simplify(center - project(center, direction))
        closed = sympify(bool(closed))
        return Basic.__new__(cls, radius, center, direction, closed)

    @property
    def radius(self):
        return self.args[0]

    @property
    def center(self):
        return self.args[1]

    @property
    def direction(self):
        return self.args[2]

    @property
    def closed(self):
        return self.args[3]

    def _sympystr(self, printer):
        return "%s(%s, %s, %s, %s)"%(
            type(self).__name__,
            printer.doprint(self.radius),
            printer.doprint(list(self.center)),
            printer.doprint(list(self.direction)),
            printer.doprint(self.closed))

    def _contains(self, other):
        if not is_Tuple(other) or len(other) != 3:
            return false
        v = Mat(other)
        p = v - self.center
        if self.closed:
            return norm(cross(p, self.direction))**2 <= self.radius**2
        else:
            return norm(cross(p, self.direction))**2 < self.radius**2

    def as_abstract(self):
        """
        >>> from sympy import *
        >>> from symplus.strplus import init_mprinting
        >>> init_mprinting()
        >>> InfiniteCylinder().as_abstract()
        {(x, y, z) | x**2 + y**2 < 1}
        >>> InfiniteCylinder(2, [0,0,0], [0,1,1]).as_abstract()
        {(x, y, z) | x**2 + (sqrt(2)*y/2 - sqrt(2)*z/2)**2 < 4}
        """
        p = r - self.center
        if self.closed:
            expr = norm(cross(p, self.direction))**2 <= self.radius**2
        else:
            expr = norm(cross(p, self.direction))**2 < self.radius**2
        return AbstractSet((x,y,z), expr)

    @property
    def interior(self):
        return InfiniteCylinder(
            radius=self.radius,
            center=self.center,
            direction=self.direction,
            closed=false,
            normalization=False)

    @property
    def closure(self):
        return InfiniteCylinder(
            radius=self.radius,
            center=self.center,
            direction=self.direction,
            closed=true,
            normalization=False)

    @property
    def is_open(self):
        return ~self.closed

    @property
    def is_closed(self):
        return self.closed

class SemiInfiniteCone(AlgebraicEuclideanSpace):
    def __new__(cls, slope=1, center=[0,0,0], direction=[0,0,1], closed=False, **kwargs):
        """
        >>> from sympy import *
        >>> from symplus.strplus import init_mprinting
        >>> init_mprinting()
        >>> SemiInfiniteCone()
        SemiInfiniteCone(1, [0 0 0]', [0 0 1]', False)
        >>> SemiInfiniteCone(5, [0,0,0], [3,4,0])
        SemiInfiniteCone(5, [0 0 0]', [3/5 4/5 0]', False)
        >>> SemiInfiniteCone().contains((-1,0,2))
        True
        >>> SemiInfiniteCone(5, [0,0,0], [3,4,0]).contains((-1,0,1))
        False
        """
        normalization = kwargs.pop("normalization", True)
        slope = sympify(abs(slope))
        center = Mat(center)
        direction = Mat(direction)
        if normalization:
            if norm(direction) == 0:
                raise ValueError
            direction = simplify(normalize(direction))
        closed = sympify(bool(closed))
        return Basic.__new__(cls, slope, center, direction, closed)

    @property
    def slope(self):
        return self.args[0]

    @property
    def center(self):
        return self.args[1]

    @property
    def direction(self):
        return self.args[2]

    @property
    def closed(self):
        return self.args[3]

    def _sympystr(self, printer):
        return "%s(%s, %s, %s, %s)"%(
            type(self).__name__,
            printer.doprint(self.slope),
            printer.doprint(list(self.center)),
            printer.doprint(list(self.direction)),
            printer.doprint(self.closed))

    def _contains(self, other):
        if not is_Tuple(other) or len(other) != 3:
            return false
        v = Mat(other)
        p = v - self.center
        if self.closed:
            return norm(cross(p, self.direction)) <= self.slope*dot(p, self.direction)
        else:
            return norm(cross(p, self.direction)) < self.slope*dot(p, self.direction)

    def as_abstract(self):
        """
        >>> from sympy import *
        >>> from symplus.strplus import init_mprinting
        >>> init_mprinting()
        >>> SemiInfiniteCone().as_abstract()
        {(x, y, z) | sqrt(x**2 + y**2) < z}
        >>> SemiInfiniteCone(5, [0,0,0], [3,4,0]).as_abstract()
        {(x, y, z) | sqrt(z**2 + (4*x/5 - 3*y/5)**2) < 3*x + 4*y}
        """
        p = r - self.center
        if self.closed:
            expr = norm(cross(p, self.direction)) <= self.slope*dot(p, self.direction)
        else:
            expr = norm(cross(p, self.direction)) < self.slope*dot(p, self.direction)
        return AbstractSet((x,y,z), expr)

    @property
    def interior(self):
        return SemiInfiniteCone(
            slope=self.slope,
            center=self.center,
            direction=self.direction,
            closed=false,
            normalization=False)

    @property
    def closure(self):
        return SemiInfiniteCone(
            slope=self.slope,
            center=self.center,
            direction=self.direction,
            closed=true,
            normalization=False)

    @property
    def is_open(self):
        return ~self.closed

    @property
    def is_closed(self):
        return self.closed

class Revolution(AlgebraicEuclideanSpace):
    def __new__(cls, func, center=[0,0,0], direction=[0,0,1], **kwargs):
        center = Mat(center)
        direction = Mat(direction)
        if norm(direction) == 0:
            raise ValueError
        direction = normalize(direction)
        return Basic.__new__(cls, func, center, direction)

    @property
    def func(self):
        return self.args[0]

    @property
    def center(self):
        return self.args[1]

    @property
    def direction(self):
        return self.args[2]

    def _sympystr(self, printer):
        return "%s(%s, %s, %s)"%(
            type(self).__name__,
            printer.doprint(self.func),
            printer.doprint(list(self.center)),
            printer.doprint(list(self.direction)))

    def _contains(self, other):
        if not is_Tuple(other) or len(other) != 3:
            return false
        v = Mat(other)
        p = v - self.center
        return self.func(dot(p, self.direction), norm(cross(p, self.direction)))

    def as_abstract(self):
        """
        >>> from sympy import *
        >>> from symplus.strplus import init_mprinting
        >>> init_mprinting()
        >>> Revolution(lambda h, s: h**2<s**2).as_abstract()
        {(x, y, z) | z**2 < x**2 + y**2}
        >>> Revolution(lambda h, s: h+1<s**2, [0,0,0], [3,4,0]).as_abstract()
        {(x, y, z) | 3*x/5 + 4*y/5 + 1 < z**2 + (4*x/5 - 3*y/5)**2}
        """
        p = r - self.center
        expr = self.func(dot(p, self.direction), norm(cross(p, self.direction)))
        return AbstractSet((x,y,z), expr)

class Box(BoundedEuclideanSpace):
    def __new__(cls, size=[2,2,2], center=[0,0,0], orientation=eye(3), closed=False, **kwargs):
        size = Mat([abs(size[0]), abs(size[1]), abs(size[2])])
        center = Mat(center)
        orientation = Mat(orientation)
        closed = sympify(bool(closed))
        return Basic.__new__(cls, size, center, orientation, closed)

    @property
    def size(self):
        return self.args[0]

    @property
    def center(self):
        return self.args[1]

    @property
    def orientation(self):
        return self.args[2]

    @property
    def closed(self):
        return self.args[3]

    def _sympystr(self, printer):
        return "%s(%s, %s, %s, %s)"%(
            type(self).__name__,
            printer.doprint(list(self.size)),
            printer.doprint(list(self.center)),
            mstr_inline_Matrix(self.orientation, printer=printer, aslist=True),
            printer.doprint(self.closed))

    def _mathstr(self, printer):
        return "%s(%s, %s, %s, %s)"%(
            type(self).__name__,
            printer.doprint(self.size),
            printer.doprint(self.center),
            mstr_inline_Matrix(self.orientation, printer=printer),
            printer.doprint(self.closed))

    def as_algebraic(self):
        i = self.orientation[:,0]
        j = self.orientation[:,1]
        k = self.orientation[:,2]
        offset = -self.size/sympify(2)
        return Intersection(
            Halfspace(offset=offset[0], direction= i, closed=self.closed, normalization=False),
            Halfspace(offset=offset[1], direction= j, closed=self.closed, normalization=False),
            Halfspace(offset=offset[2], direction= k, closed=self.closed, normalization=False),
            Halfspace(offset=offset[0], direction=-i, closed=self.closed, normalization=False),
            Halfspace(offset=offset[1], direction=-j, closed=self.closed, normalization=False),
            Halfspace(offset=offset[2], direction=-k, closed=self.closed, normalization=False))

    def _contains(self, other):
        return self.as_algebraic()._contains(other)

    def as_abstract(self):
        return as_abstract(self.as_algebraic())

    @property
    def interior(self):
        return Box(
            size=self.size,
            center=self.center,
            orientation=self.orientation,
            closed=false,
            normalization=False)

    @property
    def closure(self):
        return Box(
            size=self.size,
            center=self.center,
            orientation=self.orientation,
            closed=true,
            normalization=False)

    @property
    def is_open(self):
        return ~self.closed

    @property
    def is_closed(self):
        return self.closed

class Cylinder(BoundedEuclideanSpace):
    def __new__(cls, radius=1, height=2, center=[0,0,0], direction=[0,0,1], closed=False, **kwargs):
        normalization = kwargs.pop("normalization", True)
        radius = sympify(abs(radius))
        height = sympify(abs(height))
        center = Mat(center)
        direction = Mat(direction)
        if normalization:
            if norm(direction) == 0:
                raise ValueError
            direction = simplify(normalize(direction))
        direction = max(direction, -direction, key=tuple)
        closed = sympify(bool(closed))
        return Basic.__new__(cls, radius, height, center, direction, closed)

    @property
    def radius(self):
        return self.args[0]

    @property
    def height(self):
        return self.args[1]

    @property
    def center(self):
        return self.args[2]

    @property
    def direction(self):
        return self.args[3]

    @property
    def closed(self):
        return self.args[4]

    def _sympystr(self, printer):
        return "%s(%s, %s, %s, %s, %s)"%(
            type(self).__name__,
            printer.doprint(self.radius),
            printer.doprint(self.height),
            printer.doprint(list(self.center)),
            printer.doprint(list(self.direction)),
            printer.doprint(self.closed))

    def as_algebraic(self):
        center = simplify(self.center - project(self.center, self.direction))
        coffset = dot(self.center, self.direction)
        return Intersection(
            InfiniteCylinder(
                radius=self.radius,
                center=center,
                direction=self.direction,
                closed=self.closed,
                normalization=False),
            Halfspace(
                offset= coffset - self.height/sympify(2),
                direction= self.direction,
                closed=self.closed,
                normalization=False),
            Halfspace(
                offset=-coffset - self.height/sympify(2),
                direction=-self.direction,
                closed=self.closed,
                normalization=False))

    def _contains(self, other):
        return self.as_algebraic()._contains(other)

    def as_abstract(self):
        return as_abstract(self.as_algebraic())

    @property
    def interior(self):
        return Cylinder(
            radius=self.radius,
            height=self.height,
            center=self.center,
            direction=self.direction,
            closed=false,
            normalization=False)

    @property
    def closure(self):
        return Cylinder(
            radius=self.radius,
            height=self.height,
            center=self.center,
            direction=self.direction,
            closed=true,
            normalization=False)

    @property
    def is_open(self):
        return ~self.closed

    @property
    def is_closed(self):
        return self.closed

class Cone(BoundedEuclideanSpace):
    def __new__(cls, radius=1, height=1, center=[0,0,0], direction=[0,0,1], closed=False, **kwargs):
        normalization = kwargs.pop("normalization", True)
        radius = sympify(abs(radius))
        if height < 0:
            direction = -direction
        direction = Mat(direction)
        if normalization:
            if norm(direction) == 0:
                raise ValueError
            direction = simplify(normalize(direction))
        direction = max(direction, -direction, key=tuple)
        height = sympify(abs(height))
        center = Mat(center)
        closed = sympify(bool(closed))
        return Basic.__new__(cls, radius, height, center, direction, closed)

    @property
    def radius(self):
        return self.args[0]

    @property
    def height(self):
        return self.args[1]

    @property
    def center(self):
        return self.args[2]

    @property
    def direction(self):
        return self.args[3]

    @property
    def closed(self):
        return self.args[4]

    def _sympystr(self, printer):
        return "%s(%s, %s, %s, %s, %s)"%(
            type(self).__name__,
            printer.doprint(self.radius),
            printer.doprint(self.height),
            printer.doprint(list(self.center)),
            printer.doprint(list(self.direction)),
            printer.doprint(self.closed))

    def as_algebraic(self):
        coffset = dot(self.center, self.direction)
        return Intersection(
            SemiInfiniteCone(
                slope=self.radius/self.height,
                center=self.center,
                direction=self.direction,
                closed=self.closed,
                normalization=False),
            Halfspace(
                offset=-coffset - self.height,
                direction=-self.direction,
                closed=self.closed,
                normalization=False))

    def _contains(self, other):
        return self.as_algebraic()._contains(other)

    def as_abstract(self):
        return as_abstract(self.as_algebraic())

    @property
    def interior(self):
        return Cone(
            radius=self.radius,
            height=self.height,
            center=self.center,
            direction=self.direction,
            closed=false,
            normalization=False)

    @property
    def closure(self):
        return Cone(
            radius=self.radius,
            height=self.height,
            center=self.center,
            direction=self.direction,
            closed=true,
            normalization=False)

    @property
    def is_open(self):
        return ~self.closed

    @property
    def is_closed(self):
        return self.closed

EmptySpace = EmptySet

def as_algebraic(zet):
    if isinstance(zet, (Intersection, Union, Complement)):
        return zet.func(*(as_algebraic(arg) for arg in zet.args))
    elif isinstance(zet, BoundedEuclideanSpace):
        return zet.as_algebraic()
    elif isinstance(zet, AlgebraicEuclideanSpace):
        return zet
    else:
        raise TypeError


# topology of Euclidean Space

class EuclideanTopology(with_metaclass(Singleton, NaturalTopology)):
    def __new__(cls):
        return Set.__new__(cls)

    space = WholeSpace()

    def __str__(self):
        return "T_RR3"

    def _sympystr(self, printer):
        return self.__str__()

    def _mathstr(self, printer):
        return self.__str__()

T_RR3 = EuclideanTopology()

