from matplus import DummyMatrixSymbol
from sympy.sets.sets import Set, EmptySet
from sympy.core.containers import Tuple
from sympy.core.symbol import Symbol, Dummy
from sympy.logic.inference import satisfiable, valid
from sympy.logic.boolalg import true, false
from sympy.matrices.expressions.matexpr import MatrixSymbol


def as_dummy(var):
    if isinstance(var, Symbol):
        return var.as_dummy()
    elif isinstance(var, MatrixSymbol):
        return DummyMatrixSymbol('_'+var.name, var.shape[0], var.shape[1])
    else:
        raise TypeError('variable is not a symbol or matrix symbol: %s' % var)


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
        >>> m, n = MatrixSymbol('m', 2, 2), MatrixSymbol('n', 2, 2)
        >>> AbstractSet(m, Eq(m[0,0]+m[1,1],0))
        AbstractSet(m, m[0, 0] + m[1, 1] == 0)
        >>> AbstractSet((m, x), Eq(det(m),x))
        AbstractSet((m, x), Determinant(m) == x)
        >>> AbstractSet(x, x>1)
        (1, oo)
        >>> AbstractSet(x, (x>1) & (x**2<2))
        (1, sqrt(2))
        >>> AbstractSet(x, x>y)
        AbstractSet(x, x > y)
        >>> AbstractSet(1, x>y)
        Traceback (most recent call last):
            ...
        TypeError: variable is not a symbol or matrix symbol: 1
        >>> AbstractSet(x, x+y)
        Traceback (most recent call last):
            ...
        TypeError: expression is not boolean or relational: x + y
        """
        for v in variable if is_Tuple(variable) else (variable,):
            if not is_Symbol(v):
                raise TypeError('variable is not a symbol or matrix symbol: %s' % v)
        if not is_Boolean(expr):
            raise TypeError('expression is not boolean or relational: %r' % expr)

        if is_Tuple(variable):
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
        return self._args[0] if is_Tuple(self._args[0]) else Tuple(self._args[0])

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
        >>> m, n = MatrixSymbol('m', 2, 2), MatrixSymbol('n', 2, 2)
        >>> AbstractSet(m, Eq(m[0,0]+m[1,1],0))._intersect(AbstractSet(n, Eq(det(n),0)))
        AbstractSet(_m, And(Determinant(_m) == 0, _m[0, 0] + _m[1, 1] == 0))
        >>> AbstractSet(m, Eq(m[0,0]+m[1,1],0))._intersect(AbstractSet(x, abs(x)>1))
        EmptySet()
        """
        if isinstance(other, AbstractSet):
            vars1 = self.variables
            vars2 = other.variables
            if len(vars1) != len(vars2):
                return EmptySet()
            if any(not var_type_match(v1, v2) for v1, v2 in zip(vars1, vars2)):
                return EmptySet()

            vars12 = tuple(as_dummy(var1) for var1 in vars1)
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
        >>> m, n = MatrixSymbol('m', 2, 2), MatrixSymbol('n', 2, 2)
        >>> AbstractSet(m, Eq(m[0,0]+m[1,1],0))._union(AbstractSet(n, Eq(det(n),0)))
        AbstractSet(_m, Or(Determinant(_m) == 0, _m[0, 0] + _m[1, 1] == 0))
        >>> AbstractSet(m, Eq(m[0,0]+m[1,1],0))._union(AbstractSet(x, abs(x)>1))
        """
        if isinstance(other, AbstractSet):
            vars1 = self.variables
            vars2 = other.variables
            if len(vars1) != len(vars2):
                return None
            if any(not var_type_match(v1, v2) for v1, v2 in zip(vars1, vars2)):
                return None

            vars12 = tuple(as_dummy(var1) for var1 in vars1)
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
        EmptySet()
        >>> AbstractSet(x, abs(x)>1)._complement(AbstractSet(y, y<x))
        AbstractSet(_x, And(Abs(_x) > 1, _x >= x))
        >>> x2 = Symbol('x2', positive=True)
        >>> AbstractSet(x, abs(x)>1)._complement(AbstractSet(x2, x2<y))
        AbstractSet(_x, And(Abs(_x) > 1, _x >= y))
        >>> m, n = MatrixSymbol('m', 2, 2), MatrixSymbol('n', 2, 2)
        >>> AbstractSet(m, Eq(m[0,0]+m[1,1],0))._complement(AbstractSet(n, Eq(det(n),0)))
        AbstractSet(_m, And(Determinant(_m) != 0, _m[0, 0] + _m[1, 1] == 0))
        >>> AbstractSet(m, Eq(m[0,0]+m[1,1],0))._complement(AbstractSet(x, abs(x)>1))
        EmptySet()
        """
        if isinstance(other, AbstractSet):
            vars1 = self.variables
            vars2 = other.variables
            if len(vars1) != len(vars2):
                return EmptySet()
            if any(not var_type_match(v1, v2) for v1, v2 in zip(vars1, vars2)):
                return EmptySet()

            vars12 = tuple(as_dummy(var1) for var1 in vars1)
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
        >>> AbstractSet(x, x>y)._contains(Matrix(2,2,[1,2,3,4]))
        False
        """
        other = other if is_Tuple(other) else Tuple(other)

        var = self.variables
        if not isinstance(other, (tuple, Tuple)):
           return false
        if len(var) != len(other):
           return false
        if any(not var_type_match(v1, v2) for v1, v2 in zip(var, other)):
            return false
        return self.expr.xreplace(dict(zip(var, other)))
    
    def is_subset(self, other):
        if isinstance(other, AbstractSet):
            vars1 = self.variables
            vars2 = other.variables
            if len(vars1) != len(vars2):
                return false
            if any(not var_type_match(v1, v2) for v1, v2 in zip(vars1, vars2)):
                return false
            if len(vars1) == 1:
                x = Dummy('x')
                return forall(x, self._contains(x) >> other._contains(x))
            else:
                x = tuple(Dummy('x'+str(n)) for n in range(len(vars1)))
                return forall(x, self._contains(x) >> other._contains(x))
        else:
            raise ValueError("Unknown argument '%s'" % other)

    def is_disjoint(self, other):
        if isinstance(other, AbstractSet):
            vars1 = self.variables
            vars2 = other.variables
            if len(vars1) != len(vars2):
                return true
            if any(not var_type_match(v1, v2) for v1, v2 in zip(vars1, vars2)):
                return true
            if len(vars1) == 1:
                x = Dummy('x')
                return forall(x, self._contains(x) >> ~other._contains(x))
            else:
                x = tuple(Dummy('x'+str(n)) for n in range(len(vars1)))
                return forall(x, self._contains(x) >> ~other._contains(x))
        else:
            raise ValueError("Unknown argument '%s'" % other)


def is_Tuple(t):
    return isinstance(t, (list, tuple, Tuple))

def is_Matrix(m):
    return getattr(m, 'is_Matrix', False)

def is_Symbol(s):
    return isinstance(s, (Symbol, MatrixSymbol))

def is_Boolean(b):
    return getattr(b, 'is_Boolean', False) or getattr(b, 'is_Relational', False) or b in (true, false)

def var_type_match(var1, var2):
    if isinstance(var1, Symbol):
        return not is_Matrix(var2) # TODO: real/complex test
    elif isinstance(var1, MatrixSymbol):
        return is_Matrix(var2) and var1.shape == var2.shape
    else:
        raise TypeError('variable is not a symbol or matrix symbol: %s' % var1)


# TODO: improve algorithm
def forall(variables, expr):
    variables = Tuple(*variables) if is_Tuple(variables) else Tuple(variables)
    for v in variables:
        if not is_Symbol(v):
            raise TypeError('variable is not a symbol or matrix symbol: %s' % v)
    if not is_Boolean(expr):
        raise TypeError('expression is not boolean or relational: %r' % expr)

    if expr.free_symbols - set(variables) == set():
        return valid(expr)
    else:
        raise TypeError('unable to evaluate forall: Forall(%s, %r)' % (variables, expr))

if __name__ == '__main__':
    import doctest
    doctest.testmod()
