from sympy.core import S, Ne, Eq, Gt, Ge, Lt, Le, oo, symbols
from sympy.logic import true, false, Or, And
from sympy.sets import Set, Interval, Intersection, Union, Complement, ProductSet
from symplus.setplus import AbstractSet


def is_open(aset):
    """
    >>> from sympy import *
    >>> from symplus.setplus import *
    >>> is_open(Interval(0,1, True, True))
    True
    >>> is_open(Interval(1,2, True, False))
    False
    >>> is_open(Interval(1,oo, True, False))
    True
    >>> is_open(Interval(1,2, True, True) * Interval(0,1, True, True))
    True
    >>> is_open(Interval(1,2, False, True) * Interval(0,1, True, True))
    False
    >>> x,y = symbols('x y')
    >>> is_open(AbstractSet(x, x**2<1))
    True
    >>> is_open(AbstractSet((x,y), x<=y))
    False
    """
    if isinstance(aset, Interval):
        return (aset.left_open | (aset.start==-oo)) & (aset.right_open | (aset.end==oo))

    elif isinstance(aset, AbstractSet):
        if isinstance(aset.expr, (Or, And)):
            return is_open(aset.expand())
        elif isinstance(aset.expr, (Ne, Gt, Lt)):
            return true
        elif isinstance(aset.expr, (Eq, Ge, Le)):
            return false

    elif isinstance(aset, (Intersection, Union)):
        if all(is_open(s) == true for s in aset.args):
            return true

    elif isinstance(aset, Complement):
        if is_open(aset.args[0]) & is_closed(aset.args[1]) == true:
            return true

    elif isinstance(aset, ProductSet):
        return And(*[is_open(s) for s in aset.args])

    try:
        res = aset.is_open
        if res in (true, false):
            return res
        else:
            return Eq(Intersection(aset, aset.boundary), S.EmptySet)
    except NotImplementedError:
        raise NotImplementedError

def is_closed(aset):
    """
    >>> from sympy import *
    >>> from symplus.setplus import *
    >>> is_closed(Interval(0,1, False, False))
    True
    >>> is_closed(Interval(1,2, True, False))
    False
    >>> is_closed(Interval(1,oo, False, False))
    True
    >>> is_closed(Interval(1,2, False, False) * Interval(0,1, False, False))
    True
    >>> is_closed(Interval(1,2, False, True) * Interval(0,1, True, True))
    False
    >>> x,y = symbols('x y')
    >>> is_closed(AbstractSet(x, x**2<1))
    False
    >>> is_closed(AbstractSet((x,y), x<=y))
    True
    """
    if isinstance(aset, Interval):
        return ((~aset.left_open) | (aset.start==-oo)) & ((~aset.right_open) | (aset.end==oo))

    elif isinstance(aset, AbstractSet):
        if isinstance(aset.expr, (Or, And)):
            return is_closed(aset.expand())
        elif isinstance(aset.expr, (Eq, Ge, Le)):
            return true
        elif isinstance(aset.expr, (Ne, Gt, Lt)):
            return false

    elif isinstance(aset, (Intersection, Union)):
        if all(is_closed(s) == true for s in aset.args):
            return true

    elif isinstance(aset, Complement):
        if is_closed(aset.args[0]) & is_open(aset.args[1]) == true:
            return true

    elif isinstance(aset, ProductSet):
        return And(*[is_closed(s) for s in aset.args])

    try:
        res = aset.is_closed
        if res in (true, false):
            return res
        else:
            return Eq(Intersection(aset, aset.boundary), aset.boundary)
    except NotImplementedError:
        raise NotImplementedError


class Topology(Set):
    @property
    def space(self):
        raise NotImplementedError

    def contains(self, other):
        return is_open(other)

    def boundary_of(self, aset):
        raise NotImplementedError

    def closure_of(self, aset):
        return aset + self.boundary_of(aset)

    def interior_of(self, aset):
        return aset - self.boundary_of(aset)

    def complement_of(self, aset):
        return self.space - aset

    def exterior_of(self, aset):
        return self.interior_of(self.complement_of(aset))

    def is_open_set(self, aset):
        return Eq(aset, self.interior_of(aset))

    def is_closed_set(self, aset):
        return Eq(aset, self.closure_of(aset))

    def is_regular_open_set(self, aset):
        return Eq(aset, self.interior_of(self.closure_of(aset)))

    def is_regular_open_set(self, aset):
        return Eq(aset, self.closure_of(self.interior_of(aset)))

class DiscreteTopology(Set):
    """
    >>> from sympy import *
    >>> from symplus.setplus import *
    >>> t = DiscreteTopology(Interval(-3,3))
    >>> t.contains(Interval(0,1, True, True))
    True
    >>> t.contains(Interval(-4,-2, True, True))
    False
    >>> t.contains(Interval(1,2, True, False))
    True
    >>> t.contains(Interval(1,2, True, True) * Interval(0,1, True, True))
    False
    """
    def __new__(cls, space):
        if not isinstance(space, Set):
            raise TypeError
        return Set.__new__(cls, space)

    @property
    def space(self):
        return self.args[0]

    def contains(self, other):
        return self.space.is_superset(other)

    def boundary_of(self, aset):
        return S.EmptySet

    def closure_of(self, aset):
        return aset

    def interior_of(self, aset):
        return aset

    def is_open_set(self, aset):
        return true

    def is_closed_set(self, aset):
        return true

    def is_regular_open_set(self, aset):
        return true

    def is_regular_open_set(self, aset):
        return true

class NaturalTopology(Set):
    """
    >>> from sympy import *
    >>> from symplus.setplus import *
    >>> t = NaturalTopology(Interval(-3,3))
    >>> t.contains(Interval(0,1, True, True))
    True
    >>> t.contains(Interval(-4,-2, True, True))
    False
    >>> t.contains(Interval(1,2, True, False))
    False
    >>> t.contains(Interval(1,2, True, True) * Interval(0,1, True, True))
    False
    """
    def __new__(cls, space):
        if not isinstance(space, Set):
            raise TypeError
        return Set.__new__(cls, space)

    @property
    def space(self):
        return self.args[0]

    def contains(self, other):
        return self.space.is_superset(other) & is_open(other)

    def boundary_of(self, aset):
        raise aset.boundary

    def closure_of(self, aset):
        return aset.closure

    def interior_of(self, aset):
        return aset.interior

    def is_open_set(self, aset):
        return is_open(aset)

    def is_closed_set(self, aset):
        return is_closed(aset)


Reals = AbstractSet(symbols('x', real=True), true)

