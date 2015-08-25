from sympy.sets.sets import Set, EmptySet
from sympy.core.compatibility import iterable
from sympy.core.containers import Tuple
from sympy.core.symbol import Dummy
from sympy.core.basic import Basic
from sympy.simplify import simplify
from sympy.logic.inference import satisfiable, valid
from sympy.logic.boolalg import true, false


class AbstractSet(Set):
    is_AbstractSet = True
    
    def __new__(cls, variable, expr):
        """create AbstractSet by variable and expression

        >>> from sympy import *
        >>> x, y = Symbol('x'), Symbol('y')
        >>> AbstractSet(x, abs(x)>1)
        AbstractSet(x, Abs(x) > 1)
        >>> AbstractSet((x,), abs(x)>1)
        AbstractSet(x, Abs(x) > 1)
        >>> AbstractSet((x, y), abs(x-y)>1)
        AbstractSet((x, y), Abs(x - y) > 1)
        >>> AbstractSet([x, y], abs(x-y)>1)
        AbstractSet((x, y), Abs(x - y) > 1)
        >>> AbstractSet(x, x>1)
        (1, oo)
        >>> AbstractSet(x, (x>1) & (x**2<2))
        (1, sqrt(2))
        >>> AbstractSet(x, x>y)
        AbstractSet(x, x > y)
        >>> AbstractSet(1, x>y)
        Traceback (most recent call last):
            ...
        TypeError: variable is not a symbol: 1
        >>> AbstractSet(x, x+y)
        Traceback (most recent call last):
            ...
        TypeError: expression is not boolean or relational: x + y
        """
        for v in variable if iterable(variable) else [variable]:
            if not getattr(v, 'is_Symbol', False):
                raise TypeError('variable is not a symbol: %s' % v)
        if not is_Boolean(expr):
            raise TypeError('expression is not boolean or relational: %r' % expr)

        if iterable(variable):
            if len(variable) > 1:
                variable = Tuple(*variable)
            else:
                variable = variable[0]

        if expr.free_symbols == {variable}:
            try:
                return expr.as_set()
            except:
                return Set.__new__(cls, variable, expr)
        else:
            return Set.__new__(cls, variable, expr)

    @property
    def variable(self):
        """get variable of set builder

        >>> from sympy import *
        >>> x, y = Symbol('x'), Symbol('y')
        >>> AbstractSet(x, abs(x)>1).variable
        x
        >>> AbstractSet((x,), abs(x)>1).variable
        x
        >>> AbstractSet((x,y), abs(x-y)>1).variable
        (x, y)
        >>> AbstractSet(x, x>y).variable
        x
        """
        return self._args[0]

    @property
    def variables(self):
        """get variable with tuple of set builder

        >>> from sympy import *
        >>> x, y = Symbol('x'), Symbol('y')
        >>> AbstractSet(x, abs(x)>1).variables
        (x,)
        >>> AbstractSet((x,), abs(x)>1).variables
        (x,)
        >>> AbstractSet((x,y), abs(x-y)>1).variables
        (x, y)
        >>> AbstractSet(x, x>y).variables
        (x,)
        """
        return self._args[0] if iterable(self._args[0]) else Tuple(self._args[0])

    @property
    def expr(self):
        """get expression of set builder

        >>> from sympy import *
        >>> x, y = Symbol('x'), Symbol('y')
        >>> AbstractSet(x, abs(x)>1).expr
        Abs(x) > 1
        >>> AbstractSet((x,), abs(x)>1).expr
        Abs(x) > 1
        >>> AbstractSet((x,y), abs(x-y)>1).expr
        Abs(x - y) > 1
        >>> AbstractSet(x, x>y).expr
        x > y
        """
        return self._args[1]

    @property
    def free_symbols(self):
        """get free symbols of set builder

        >>> from sympy import *
        >>> x, y = Symbol('x'), Symbol('y')
        >>> AbstractSet(x, abs(x)>1).free_symbols
        set()
        >>> AbstractSet((x,), abs(x)>1).free_symbols
        set()
        >>> AbstractSet((x,y), abs(x-y)>1).free_symbols
        set()
        >>> AbstractSet(x, x>y).free_symbols
        {y}
        """
        return self.expr.free_symbols - set(self.variables)

    def _intersect(self, other):
        """intersect two set builder

        >>> from sympy import *
        >>> x, y = Symbol('x'), Symbol('y')
        >>> AbstractSet(x, abs(x)>1)._intersect(AbstractSet(y, abs(y)<3))
        AbstractSet(_x, And(Abs(_x) < 3, Abs(_x) > 1))
        >>> AbstractSet(x, abs(x)>1)._intersect(AbstractSet((x,y), abs(x-y)>1))
        EmptySet()
        >>> AbstractSet(x, abs(x)>1)._intersect(AbstractSet(y, y<x))
        AbstractSet(_x, And(Abs(_x) > 1, _x < x))
        >>> x2 = Symbol('x2', positive=True)
        >>> AbstractSet(x, abs(x)>1)._intersect(AbstractSet(x2, x2<y))
        AbstractSet(_x, And(Abs(_x) > 1, _x < y))
        """
        if isinstance(other, AbstractSet):
            vars1 = self.variables
            vars2 = other.variables
            if len(vars1) != len(vars2):
                return EmptySet()

            vars12 = tuple(var1.as_dummy() for var1 in vars1)
            expr12 = (self.expr.xreplace(dict(zip(vars1, vars12))) &
                      other.expr.xreplace(dict(zip(vars2, vars12))))
            if not satisfiable(expr12):
                return EmptySet()

            return AbstractSet(vars12, expr12)
        else:
            return None

    def _union(self, other):
        """union two set builder

        >>> from sympy import *
        >>> x, y = Symbol('x'), Symbol('y')
        >>> AbstractSet(x, abs(x)>1)._union(AbstractSet(y, abs(y)<3))
        AbstractSet(_x, Or(Abs(_x) < 3, Abs(_x) > 1))
        >>> AbstractSet(x, abs(x)>1)._union(AbstractSet((x,y), abs(x-y)>1))
        >>> AbstractSet(x, abs(x)>1)._union(AbstractSet(y, y<x))
        AbstractSet(_x, Or(Abs(_x) > 1, _x < x))
        >>> x2 = Symbol('x2', positive=True)
        >>> AbstractSet(x, abs(x)>1)._union(AbstractSet(x2, x2<y))
        AbstractSet(_x, Or(Abs(_x) > 1, _x < y))
        """
        if isinstance(other, AbstractSet):
            vars1 = self.variables
            vars2 = other.variables
            if len(vars1) != len(vars2):
                return None

            vars12 = tuple(var1.as_dummy() for var1 in vars1)
            expr12 = (self.expr.xreplace(dict(zip(vars1, vars12))) |
                      other.expr.xreplace(dict(zip(vars2, vars12))))
            if not satisfiable(expr12):
                return EmptySet()

            return AbstractSet(vars12, expr12)
        else:
            return None

    def _complement(self, other):
        """complement two set builder

        >>> from sympy import *
        >>> x, y = Symbol('x'), Symbol('y')
        >>> AbstractSet(x, abs(x)>1)._complement(AbstractSet(y, abs(y)<3))
        AbstractSet(_x, And(Abs(_x) > 1, Abs(_x) >= 3))
        >>> AbstractSet(x, abs(x)>1)._complement(AbstractSet((x,y), abs(x-y)>1))
        >>> AbstractSet(x, abs(x)>1)._complement(AbstractSet(y, y<x))
        AbstractSet(_x, And(Abs(_x) > 1, _x >= x))
        >>> x2 = Symbol('x2', positive=True)
        >>> AbstractSet(x, abs(x)>1)._complement(AbstractSet(x2, x2<y))
        AbstractSet(_x, And(Abs(_x) > 1, _x >= y))
        """
        if isinstance(other, AbstractSet):
            vars1 = self.variables
            vars2 = other.variables
            if len(vars1) != len(vars2):
                return None

            vars12 = tuple(var1.as_dummy() for var1 in vars1)
            expr12 = (self.expr.xreplace(dict(zip(vars1, vars12))) &~
                      other.expr.xreplace(dict(zip(vars2, vars12))))
            if not satisfiable(expr12):
                return EmptySet()

            return AbstractSet(vars12, expr12)
        else:
            return Set._complement(self, other)

    def _contains(self, other):
        """
        >>> from sympy import *
        >>> x, y, z = Symbol('x'), Symbol('y'), Symbol('z')
        >>> AbstractSet(x, abs(x)>1)._contains(2)
        True
        >>> AbstractSet((x,y), abs(x-y)>1)._contains((3,1))
        True
        >>> AbstractSet((x,y), abs(x-y)>1)._contains((x+3,x+1))
        True
        >>> AbstractSet(x, x>y)._contains(z)
        z > y
        """
        if len(self.variables) == 1:
            return self.expr.xreplace({self.variable: other})
        else:
            if (not isinstance(other, (tuple, Tuple)) or
                len(self.variable) != len(other)):
               return false
            return self.expr.xreplace(dict(zip(self.variable, other)))
    
    def is_subset(self, other):
        if isinstance(other, AbstractSet):
            if len(self.variables) != len(other.variables):
                return false
            if len(self.variables) == 1:
                x = Dummy('x')
                return forall(x, self._contains(x) >> other._contains(x))
            else:
                x = tuple(Dummy('x'+str(n)) for n in range(len(self.variables)))
                return forall(x, self._contains(x) >> other._contains(x))
        else:
            raise ValueError("Unknown argument '%s'" % other)

    def is_disjoint(self, other):
        if isinstance(other, AbstractSet):
            if len(self.variables) != len(other.variables):
                return true
            if len(self.variables) == 1:
                x = Dummy('x')
                return forall(x, self._contains(x) >> ~other._contains(x))
            else:
                x = tuple(Dummy('x'+str(n)) for n in range(len(self.variables)))
                return forall(x, self._contains(x) >> ~other._contains(x))
        else:
            raise ValueError("Unknown argument '%s'" % other)


def is_Boolean(b):
    return getattr(b, 'is_Boolean', False) or getattr(b, 'is_Relational', False) or b in (true, false)

def forall(variables, expr):
    variables = Tuple(*variables) if iterable(variables) else Tuple(variables)
    for v in variables:
        if not getattr(v, 'is_Symbol', False):
            raise TypeError('variable is not a symbol: %s' % v)
    if not is_Boolean(expr):
        raise TypeError('expression is not boolean or relational: %r' % expr)

    if expr.free_symbols - set(variables) == set():
        return simplify(expr)
    else:
        raise TypeError('unable to evaluate forall: Forall(%s, %r)' % (variables, expr))

if __name__ == '__main__':
    import doctest
    doctest.testmod()
