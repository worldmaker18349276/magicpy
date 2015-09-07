from sympy.logic import Not
from sympy.matrices.immutable import ImmutableMatrix as Mat
from magicball.symplus.setplus import AbstractSet
from magicball.symplus.matplus import norm, normalize, dot, cross, x, y, z, r


def halfspace(direction=[1,0,0], offset=0, closed=False):
    """
    >>> from sympy import *
    >>> halfspace()
    AbstractSet((x, y, z), x > 0)
    >>> halfspace([1,2,0], -3)
    AbstractSet((x, y, z), sqrt(5)*x/5 + 2*sqrt(5)*y/5 > -3)
    """
    direction = Mat(direction)
    if norm(direction) == 0:
        raise ValueError
    direction = normalize(direction)
    if closed:
        expr = dot(r, direction) >= offset
    else:
        expr = dot(r, direction) > offset
    return AbstractSet((x,y,z), expr)

def sphere(radius=1, center=[0,0,0], closed=False):
    """
    >>> from sympy import *
    >>> sphere()
    AbstractSet((x, y, z), x**2 + y**2 + z**2 < 1)
    >>> sphere(3, [1,0,2])
    AbstractSet((x, y, z), y**2 + (x - 1)**2 + (z - 2)**2 < 9)
    """
    center = Mat(center)
    if closed:
        expr = norm(r-center)**2 <= radius**2
    else:
        expr = norm(r-center)**2 < radius**2
    return AbstractSet((x,y,z), expr)

def cylinder(direction=[1,0,0], radius=1, closed=False):
    """
    >>> from sympy import *
    >>> cylinder()
    AbstractSet((x, y, z), y**2 + z**2 < 1)
    >>> cylinder([0,1,1], 2)
    AbstractSet((x, y, z), x**2 + (sqrt(2)*y/2 - sqrt(2)*z/2)**2 < 4)
    """
    direction = Mat(direction)
    if norm(direction) == 0:
        raise ValueError
    direction = normalize(direction)
    if closed:
        expr = norm(cross(r, direction))**2 <= radius**2
    else:
        expr = norm(cross(r, direction))**2 < radius**2
    return AbstractSet((x,y,z), expr)

def cone(direction=[1,0,0], slope=1, closed=False):
    """
    >>> from sympy import *
    >>> cone()
    AbstractSet((x, y, z), y**2 + z**2 < x**2)
    >>> cone([3,4,0], 5)
    AbstractSet((x, y, z), z**2 + (4*x/5 - 3*y/5)**2 < (3*x + 4*y)**2)
    """
    direction = Mat(direction)
    if norm(direction) == 0:
        raise ValueError
    direction = normalize(direction)
    if closed:
        expr = norm(cross(r, direction))**2 <= (slope*dot(r, direction))**2
    else:
        expr = norm(cross(r, direction))**2 < (slope*dot(r, direction))**2
    return AbstractSet((x,y,z), expr)

def revolution(func, direction=[1,0,0]):
    """
    >>> from sympy import *
    >>> revolution(lambda h, s: h**2<s**2)
    AbstractSet((x, y, z), x**2 < y**2 + z**2)
    >>> revolution(lambda h, s: h+1<s**2, [3,4,0])
    AbstractSet((x, y, z), 3*x/5 + 4*y/5 + 1 < z**2 + (4*x/5 - 3*y/5)**2)
    """
    direction = Mat(direction)
    if norm(direction) == 0:
        raise ValueError
    direction = normalize(direction)
    expr = func(dot(r, direction), norm(cross(r, direction)))
    return AbstractSet((x,y,z), expr)

def complement(aset):
    return AbstractSet(aset.variables, Not(aset.expr))

def with_complement(aset):
    return (aset, complement(aset))

