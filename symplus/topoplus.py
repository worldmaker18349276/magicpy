from sympy.core import S, Ne, Eq, Gt, Ge, Lt, Le, oo, symbols
from sympy.core.evaluate import global_evaluate
from sympy.logic import true, false, Or, And
from sympy.sets import Set, Interval, Intersection, Union, Complement, ProductSet, FiniteSet
from symplus.setplus import AbstractSet


def is_open(zet):
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
    if isinstance(zet, Interval):
        return (zet.left_open | (zet.start==-oo)) & (zet.right_open | (zet.end==oo))

    elif isinstance(zet, AbstractSet):
        if isinstance(zet.expr, (Or, And)):
            return is_open(zet.expand())
        elif isinstance(zet.expr, (Ne, Gt, Lt)):
            return true
        elif isinstance(zet.expr, (Eq, Ge, Le)):
            return false

    elif isinstance(zet, (Intersection, Union)):

        if And(*map(is_open, zet.args)) == true:
            return true

    elif isinstance(zet, Complement):
        if is_open(zet.args[0]) & is_closed(zet.args[1]) == true:
            return true

    elif isinstance(zet, ProductSet):
        return And(*map(is_open, zet.args))

    try:
        res = zet.is_open
        if res in (true, false):
            return res
        else:
            return Eq(Intersection(zet, zet.boundary), S.EmptySet)
    except NotImplementedError:
        raise NotImplementedError

def is_closed(zet):
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
    if isinstance(zet, Interval):
        return ((~zet.left_open) | (zet.start==-oo)) & ((~zet.right_open) | (zet.end==oo))

    elif isinstance(zet, AbstractSet):
        if isinstance(zet.expr, (Or, And)):
            return is_closed(zet.expand())
        elif isinstance(zet.expr, (Eq, Ge, Le)):
            return true
        elif isinstance(zet.expr, (Ne, Gt, Lt)):
            return false

    elif isinstance(zet, (Intersection, Union)):
        if And(*map(is_closed, zet.args)) == true:
            return true

    elif isinstance(zet, Complement):
        if is_closed(zet.args[0]) & is_open(zet.args[1]) == true:
            return true

    elif isinstance(zet, ProductSet):
        return And(*map(is_closed, zet.args))

    try:
        res = zet.is_closed
        if res in (true, false):
            return res
        else:
            return Eq(Intersection(zet, zet.boundary), zet.boundary)
    except NotImplementedError:
        raise NotImplementedError

class Interior(Set):
    def __new__(cls, set, **kwargs):
        evaluate = kwargs.pop('evaluate', global_evaluate[0])
        if evaluate:
            return Interior.eval(set)
        return Set.__new__(cls, set, **kwargs)

    @staticmethod
    def eval(zet):
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
        if isinstance(zet, Interior):
            return zet

        elif isinstance(zet, Interval):
            return Interval(zet.start, zet.end, left_open=True, right_open=True)

        elif isinstance(zet, AbstractSet):
            if isinstance(zet.expr, (Or, And)):
                return Interior.eval(zet.expand())
            elif isinstance(zet.expr, Ne):
                return zet
            elif isinstance(zet.expr, Eq):
                return AbstractSet(zet.variables, false)
            elif isinstance(zet.expr, (Gt, Ge)):
                return AbstractSet(zet.variables, Gt(*zet.expr.args))
            elif isinstance(zet.expr, (Lt, Le)):
                return AbstractSet(zet.variables, Lt(*zet.expr.args))

        elif isinstance(zet, Intersection):
            return zet.func(*map(Interior.eval, zet.args))

        elif isinstance(zet, Complement):
            return zet.func(Interior.eval(zet.args[0]), Closure.eval(zet.args[1]))

        elif isinstance(zet, ProductSet):
            return zet.func(*map(Interior.eval, zet.args))

        try:
            res = zet.interior
            if res is not None:
                return res
            else:
                return zet - zet.boundary
        except NotImplementedError:
            return Interior(zet, evaluate=False)

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
            return Closure.eval(set)
        return Set.__new__(cls, set, **kwargs)

    @staticmethod
    def eval(zet):
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
        if isinstance(zet, Closure):
            return zet

        elif isinstance(zet, Interval):
            return Interval(zet.start, zet.end, left_open=False, right_open=False)

        elif isinstance(zet, AbstractSet):
            if isinstance(zet.expr, (Or, And)):
                return Closure.eval(zet.expand())
            elif isinstance(zet.expr, Eq):
                return zet
            elif isinstance(zet.expr, Ne):
                return AbstractSet(zet.variables, true)
            elif isinstance(zet.expr, (Ge, Gt)):
                return AbstractSet(zet.variables, Ge(*zet.expr.args))
            elif isinstance(zet.expr, (Le, Lt)):
                return AbstractSet(zet.variables, Le(*zet.expr.args))

        elif isinstance(zet, Union):
            return zet.func(*map(Closure.eval, zet.args))

        elif isinstance(zet, ProductSet):
            return zet.func(*map(Closure.eval, zet.args))

        try:
            res = zet.closure
            if res is not None:
                return res
            else:
                return zet + zet.boundary
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

def AbsoluteComplement(zet):
    return zet._absolute_complement()

def Exterior(zet):
    return Interior(AbsoluteComplement(zet))

# topology(open set definition)

class Topology(Set):
    @property
    def space(self):
        raise NotImplementedError

    def contains(self, other):
        return is_open(other)

    def boundary_of(self, zet):
        raise NotImplementedError

    def closure_of(self, zet):
        return zet + self.boundary_of(zet)

    def interior_of(self, zet):
        return zet - self.boundary_of(zet)

    def complement_of(self, zet):
        return self.space - zet

    def exterior_of(self, zet):
        return self.interior_of(self.complement_of(zet))

    def is_open_set(self, zet):
        return Eq(zet, self.interior_of(zet))

    def is_closed_set(self, zet):
        return Eq(zet, self.closure_of(zet))

    def is_regular_open_set(self, zet):
        return Eq(zet, self.interior_of(self.closure_of(zet)))

    def is_regular_open_set(self, zet):
        return Eq(zet, self.closure_of(self.interior_of(zet)))

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

    def boundary_of(self, zet):
        return S.EmptySet

    def closure_of(self, zet):
        return zet

    def interior_of(self, zet):
        return zet

    def is_open_set(self, zet):
        return true

    def is_closed_set(self, zet):
        return true

    def is_regular_open_set(self, zet):
        return true

    def is_regular_open_set(self, zet):
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

    def boundary_of(self, zet):
        raise zet.boundary

    def closure_of(self, zet):
        return Closure(zet)

    def interior_of(self, zet):
        return Interior(zet)

    def is_open_set(self, zet):
        return is_open(zet)

    def is_closed_set(self, zet):
        return is_closed(zet)


Reals = AbstractSet(symbols('x', real=True), true)

