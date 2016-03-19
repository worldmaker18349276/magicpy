from sympy.core import S, Ne, Eq, Gt, Ge, Lt, Le, oo, symbols
from sympy.core.evaluate import global_evaluate
from sympy.logic import true, false, Or, And
from sympy.sets import Set, Interval, Intersection, Union, Complement, ProductSet, FiniteSet
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

        if And(*map(is_open, aset.args)) == true:
            return true

    elif isinstance(aset, Complement):
        if is_open(aset.args[0]) & is_closed(aset.args[1]) == true:
            return true

    elif isinstance(aset, ProductSet):
        return And(*map(is_open, aset.args))

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
        if And(*map(is_closed, aset.args)) == true:
            return true

    elif isinstance(aset, Complement):
        if is_closed(aset.args[0]) & is_open(aset.args[1]) == true:
            return true

    elif isinstance(aset, ProductSet):
        return And(*map(is_closed, aset.args))

    try:
        res = aset.is_closed
        if res in (true, false):
            return res
        else:
            return Eq(Intersection(aset, aset.boundary), aset.boundary)
    except NotImplementedError:
        raise NotImplementedError

class Interior(Set):
    def __new__(cls, set, **kwargs):
        evaluate = kwargs.pop('evaluate', global_evaluate[0])
        if evaluate:
            return Interior.reduce(set)
        return Set.__new__(cls, set, **kwargs)

    @staticmethod
    def reduce(aset):
        """
        >>> from sympy import *
        >>> from symplus.setplus import *
        >>> Interior(Interval(0,1, False, False))
        (0, 1)
        >>> Interior(Interval(1,2, True, False))
        (1, 2)
        >>> Interior(Interval(1,oo, False, False))
        (1, oo)
        >>> Interior(Interval(1,2, False, False) * Interval(0,1, False, False))
        (1, 2) x (0, 1)
        >>> x,y = symbols('x y')
        >>> Interior(AbstractSet(x, x**2<1))
        AbstractSet(x, x**2 < 1)
        >>> Interior(AbstractSet(x, (x<6)&(x>=4)))
        AbstractSet(x, And(x < 6, x > 4))
        >>> Interior(AbstractSet((x,y), x<=y))
        AbstractSet((x, y), x < y)
        """
        if isinstance(aset, Interior):
            return aset

        elif isinstance(aset, Interval):
            return Interval(aset.start, aset.end, left_open=True, right_open=True)

        elif isinstance(aset, AbstractSet):
            if isinstance(aset.expr, (Or, And)):
                return Interior.reduce(aset.expand())
            elif isinstance(aset.expr, Ne):
                return aset
            elif isinstance(aset.expr, Eq):
                return AbstractSet(aset.variables, false)
            elif isinstance(aset.expr, (Gt, Ge)):
                return AbstractSet(aset.variables, Gt(*aset.expr.args))
            elif isinstance(aset.expr, (Lt, Le)):
                return AbstractSet(aset.variables, Lt(*aset.expr.args))

        elif isinstance(aset, Intersection):
            return aset.func(*map(Interior.reduce, aset.args))

        elif isinstance(aset, Complement):
            return aset.func(Interior.reduce(aset.args[0]), Closure.reduce(aset.args[1]))

        elif isinstance(aset, ProductSet):
            return aset.func(*map(Interior.reduce, aset.args))

        try:
            res = aset.interior
            if res is not None:
                return res
            else:
                return aset - aset.boundary
        except NotImplementedError:
            return Interior(aset, evaluate=False)

    @property
    def set(self):
        return self.args[0]

    @property
    def is_open(self):
        return true

    @property
    def is_closed(self):
        return false

    def _absolute_complement(self):
        return Closure(AbsoluteComplement(self.set))

class Closure(Set):
    def __new__(cls, set, **kwargs):
        evaluate = kwargs.pop('evaluate', global_evaluate[0])
        if evaluate:
            return Closure.reduce(set)
        return Set.__new__(cls, set, **kwargs)

    @staticmethod
    def reduce(aset):
        """
        >>> from sympy import *
        >>> from symplus.setplus import *
        >>> Closure(Interval(0,1, False, False))
        [0, 1]
        >>> Closure(Interval(1,2, True, False))
        [1, 2]
        >>> Closure(Interval(1,oo, False, False))
        [1, oo)
        >>> Closure(Interval(1,2, False, False) * Interval(0,1, False, False))
        [1, 2] x [0, 1]
        >>> x,y = symbols('x y')
        >>> Closure(AbstractSet(x, x**2<1))
        AbstractSet(x, x**2 <= 1)
        >>> Closure(AbstractSet(x, (x<4)|(x>=6)))
        AbstractSet(x, Or(x <= 4, x >= 6))
        >>> Closure(AbstractSet((x,y), x<=y))
        AbstractSet((x, y), x <= y)
        """
        if isinstance(aset, Closure):
            return aset

        elif isinstance(aset, Interval):
            return Interval(aset.start, aset.end, left_open=False, right_open=False)

        elif isinstance(aset, AbstractSet):
            if isinstance(aset.expr, (Or, And)):
                return Closure.reduce(aset.expand())
            elif isinstance(aset.expr, Eq):
                return aset
            elif isinstance(aset.expr, Ne):
                return AbstractSet(aset.variables, true)
            elif isinstance(aset.expr, (Ge, Gt)):
                return AbstractSet(aset.variables, Ge(*aset.expr.args))
            elif isinstance(aset.expr, (Le, Lt)):
                return AbstractSet(aset.variables, Le(*aset.expr.args))

        elif isinstance(aset, Union):
            return aset.func(*map(Closure.reduce, aset.args))

        elif isinstance(aset, ProductSet):
            return aset.func(*map(Closure.reduce, aset.args))

        try:
            res = aset.closure
            if res is not None:
                return res
            else:
                return aset + aset.boundary
        except NotImplementedError:
            return None

    @property
    def set(self):
        return self.args[0]

    @property
    def is_open(self):
        return false

    @property
    def is_closed(self):
        return true

    def _absolute_complement(self):
        return Interior(AbsoluteComplement(self.set))

def AbsoluteComplement(aset):
    return aset._absolute_complement()

def Exterior(aset):
    return Interior(AbsoluteComplement(aset))

# topology(open set definition)

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

class DiscreteTopology(Topology):
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

class NaturalTopology(Topology):
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
        return Closure(aset)

    def interior_of(self, aset):
        return Interior(aset)

    def is_open_set(self, aset):
        return is_open(aset)

    def is_closed_set(self, aset):
        return is_closed(aset)


Reals = AbstractSet(symbols('x', real=True), true)

