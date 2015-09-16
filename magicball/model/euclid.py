from sympy.core import Basic, S
from sympy.logic import true
from sympy.sets import Set
from sympy.matrices.immutable import ImmutableMatrix as Mat
from magicball.symplus.setplus import AbstractSet
from magicball.symplus.matplus import norm, normalize, dot, cross, project, x, y, z, r


RR3 = AbstractSet((x, y, z), true)


class halfspace(Set):
    def __new__(cls, direction=[1,0,0], offset=0, closed=False):
        direction = Mat(direction)
        if norm(direction) == 0:
            raise ValueError
        direction = normalize(direction)
        closed = bool(closed)
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

    def as_abstract(self):
        """
        >>> from sympy import *
        >>> halfspace().as_abstract()
        AbstractSet((x, y, z), x > 0)
        >>> halfspace([1,2,0], -3).as_abstract()
        AbstractSet((x, y, z), sqrt(5)*x/5 + 2*sqrt(5)*y/5 > -3)
        """
        if self.closed:
            expr = dot(r, self.direction) >= self.offset
        else:
            expr = dot(r, self.direction) > self.offset
        return AbstractSet((x,y,z), expr)


class sphere(Set):
    def __new__(cls, radius=1, center=[0,0,0], closed=False):
        radius = abs(radius)
        center = Mat(center)
        closed = bool(closed)
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

    def as_abstract(self):
        """
        >>> from sympy import *
        >>> sphere().as_abstract()
        AbstractSet((x, y, z), x**2 + y**2 + z**2 < 1)
        >>> sphere(3, [1,0,2]).as_abstract()
        AbstractSet((x, y, z), y**2 + (x - 1)**2 + (z - 2)**2 < 9)
        """
        if self.closed:
            expr = norm(r-self.center)**2 <= self.radius**2
        else:
            expr = norm(r-self.center)**2 < self.radius**2
        return AbstractSet((x,y,z), expr)


class cylinder(Set):
    def __new__(cls, direction=[1,0,0], radius=1, center=[0,0,0], closed=False):
        direction = Mat(direction)
        if norm(direction) == 0:
            raise ValueError
        direction = normalize(direction)
        direction = max(direction, -direction, key=tuple)
        radius = abs(radius)
        center = Mat(center)
        center = center - project(center, direction)
        closed = bool(closed)
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

    def as_abstract(self):
        """
        >>> from sympy import *
        >>> cylinder().as_abstract()
        AbstractSet((x, y, z), y**2 + z**2 < 1)
        >>> cylinder([0,1,1], 2).as_abstract()
        AbstractSet((x, y, z), x**2 + (sqrt(2)*y/2 - sqrt(2)*z/2)**2 < 4)
        """
        p = r - self.center
        if self.closed:
            expr = norm(cross(p, self.direction))**2 <= self.radius**2
        else:
            expr = norm(cross(p, self.direction))**2 < self.radius**2
        return AbstractSet((x,y,z), expr)


class cone(Set):
    def __new__(cls, direction=[1,0,0], slope=1, center=[0,0,0], closed=False):
        direction = Mat(direction)
        if norm(direction) == 0:
            raise ValueError
        direction = normalize(direction)
        direction = max(direction, -direction, key=tuple)
        slope = abs(slope)
        center = Mat(center)
        closed = bool(closed)
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

    def as_abstract(self):
        """
        >>> from sympy import *
        >>> cone().as_abstract()
        AbstractSet((x, y, z), y**2 + z**2 < x**2)
        >>> cone([3,4,0], 5).as_abstract()
        AbstractSet((x, y, z), z**2 + (4*x/5 - 3*y/5)**2 < (3*x + 4*y)**2)
        """
        p = r - self.center
        if self.closed:
            expr = norm(cross(p, self.direction))**2 <= (self.slope*dot(p, self.direction))**2
        else:
            expr = norm(cross(p, self.direction))**2 < (self.slope*dot(p, self.direction))**2
        return AbstractSet((x,y,z), expr)


class revolution(Set):
    def __new__(cls, func, direction=[1,0,0], center=[0,0,0]):
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

    def as_abstract(self):
        """
        >>> from sympy import *
        >>> revolution(lambda h, s: h**2<s**2).as_abstract()
        AbstractSet((x, y, z), x**2 < y**2 + z**2)
        >>> revolution(lambda h, s: h+1<s**2, [3,4,0]).as_abstract()
        AbstractSet((x, y, z), 3*x/5 + 4*y/5 + 1 < z**2 + (4*x/5 - 3*y/5)**2)
        """
        p = r - self.center
        expr = self.func(dot(p, self.direction), norm(cross(p, self.direction)))
        return AbstractSet((x,y,z), expr)


def complement(aset):
    return RR3 - aset

def with_complement(aset):
    return (aset, complement(aset))

