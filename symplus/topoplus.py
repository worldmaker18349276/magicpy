from sympy.core import S, Ne, Eq, Gt, Ge, Lt, Le, oo
from sympy.logic import true, false, Or, And
from sympy.sets import Set, Interval, Intersection, Union, Complement, ProductSet
from symplus.setplus import AbstractSet


def is_open(set):
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
    if isinstance(set, Interval):
        return (set.left_open | (set.start==-oo)) & (set.right_open | (set.end==oo))

    elif isinstance(set, AbstractSet):
        if isinstance(set.expr, (Or, And)):
            return is_open(set.expand())
        elif isinstance(set.expr, (Ne, Gt, Lt)):
            return true
        elif isinstance(set.expr, (Eq, Ge, Le)):
            return false

    elif isinstance(set, (Intersection, Union)):
        if all(is_open(s) == true for s in set.args):
            return true

    elif isinstance(set, Complement):
        if is_open(set.args[0]) & is_closed(set.args[1]) == true:
            return true

    elif isinstance(set, ProductSet):
        return And(*[is_open(s) for s in set.args])

    try:
        res = set.is_open
        if res in (true, false):
            return res
        else:
            return Eq(Intersection(set, set.boundary), S.EmptySet)
    except NotImplementedError:
        raise NotImplementedError

def is_closed(set):
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
    if isinstance(set, Interval):
        return ((~set.left_open) | (set.start==-oo)) & ((~set.right_open) | (set.end==oo))

    elif isinstance(set, AbstractSet):
        if isinstance(set.expr, (Or, And)):
            return is_closed(set.expand())
        elif isinstance(set.expr, (Eq, Ge, Le)):
            return true
        elif isinstance(set.expr, (Ne, Gt, Lt)):
            return false

    elif isinstance(set, (Intersection, Union)):
        if all(is_closed(s) == true for s in set.args):
            return true

    elif isinstance(set, Complement):
        if is_closed(set.args[0]) & is_open(set.args[1]) == true:
            return true

    elif isinstance(set, ProductSet):
        return And(*[is_closed(s) for s in set.args])

    try:
        res = set.is_closed
        if res in (true, false):
            return res
        else:
            return Eq(Intersection(set, set.boundary), set.boundary)
    except NotImplementedError:
        raise NotImplementedError


class TrivialTopology(Set):
    """
    >>> from sympy import *
    >>> from symplus.setplus import *
    >>> t = TrivialTopology(Interval(-3,3))
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

