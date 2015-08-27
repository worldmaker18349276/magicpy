from matplus import DummyMatrixSymbol
from util import *
from sympy.sets.sets import Set, EmptySet, UniversalSet
from sympy.core.basic import Basic
from sympy.core.containers import Tuple
from sympy.core.symbol import Symbol, Dummy
from sympy.logic.inference import satisfiable, valid
from sympy.logic.boolalg import true, false, BooleanFunction, Equivalent
from sympy.matrices.expressions.matexpr import MatrixSymbol
from sympy.simplify.simplify import simplify


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

    def _hashable_content(self):
        return (self.expr.xreplace(self.canonical_variables),)

    def _intersect(self, other):
        """intersect two set builder

        >>> from sympy import *
        >>> x, y = Symbol('x'), Symbol('y')
        >>> AbstractSet(x, abs(x)>1)._intersect(AbstractSet(y, abs(y)<3))
        AbstractSet(x, And(Abs(x) < 3, Abs(x) > 1))
        >>> AbstractSet(x, abs(x)>1)._intersect(AbstractSet((x,y), abs(x-y)>1))
        EmptySet()
        >>> AbstractSet(x, abs(x)>1)._intersect(AbstractSet(y, y<x))
        AbstractSet(x_, And(Abs(x_) > 1, x_ < x))
        >>> x2 = Symbol('x2', positive=True)
        >>> AbstractSet(x, abs(x)>1)._intersect(AbstractSet(x2, x2<y))
        AbstractSet(x, And(Abs(x) > 1, x < y))
        >>> m, n = MatrixSymbol('m', 2, 2), MatrixSymbol('n', 2, 2)
        >>> AbstractSet(m, Eq(m[0,0]+m[1,1],0))._intersect(AbstractSet(n, Eq(det(n),0)))
        AbstractSet(m, And(Determinant(m) == 0, m[0, 0] + m[1, 1] == 0))
        >>> AbstractSet(m, Eq(m[0,0]+m[1,1],0))._intersect(AbstractSet(x, abs(x)>1))
        EmptySet()
        """
        if isinstance(other, AbstractSet):
            vars1 = self.variables
            vars2 = other.variables
            if not var_type_match(vars1, vars2):
                return EmptySet()

            vars12 = rename_variables_in(vars1, self.free_symbols | other.free_symbols)
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
        AbstractSet(x, Or(Abs(x) < 3, Abs(x) > 1))
        >>> AbstractSet(x, abs(x)>1)._union(AbstractSet((x,y), abs(x-y)>1))
        >>> AbstractSet(x, abs(x)>1)._union(AbstractSet(y, y<x))
        AbstractSet(x_, Or(Abs(x_) > 1, x_ < x))
        >>> x2 = Symbol('x2', positive=True)
        >>> AbstractSet(x, abs(x)>1)._union(AbstractSet(x2, x2<y))
        AbstractSet(x, Or(Abs(x) > 1, x < y))
        >>> m, n = MatrixSymbol('m', 2, 2), MatrixSymbol('n', 2, 2)
        >>> AbstractSet(m, Eq(m[0,0]+m[1,1],0))._union(AbstractSet(n, Eq(det(n),0)))
        AbstractSet(m, Or(Determinant(m) == 0, m[0, 0] + m[1, 1] == 0))
        >>> AbstractSet(m, Eq(m[0,0]+m[1,1],0))._union(AbstractSet(x, abs(x)>1))
        """
        if isinstance(other, AbstractSet):
            vars1 = self.variables
            vars2 = other.variables
            if not var_type_match(vars1, vars2):
                return None

            vars12 = rename_variables_in(vars1, self.free_symbols | other.free_symbols)
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
        AbstractSet(x, And(Abs(x) > 1, Abs(x) >= 3))
        >>> AbstractSet(x, abs(x)>1)._complement(AbstractSet((x,y), abs(x-y)>1))
        EmptySet()
        >>> AbstractSet(x, abs(x)>1)._complement(AbstractSet(y, y<x))
        AbstractSet(x_, And(Abs(x_) > 1, x_ >= x))
        >>> x2 = Symbol('x2', positive=True)
        >>> AbstractSet(x, abs(x)>1)._complement(AbstractSet(x2, x2<y))
        AbstractSet(x, And(Abs(x) > 1, x >= y))
        >>> m, n = MatrixSymbol('m', 2, 2), MatrixSymbol('n', 2, 2)
        >>> AbstractSet(m, Eq(m[0,0]+m[1,1],0))._complement(AbstractSet(n, Eq(det(n),0)))
        AbstractSet(m, And(Determinant(m) != 0, m[0, 0] + m[1, 1] == 0))
        >>> AbstractSet(m, Eq(m[0,0]+m[1,1],0))._complement(AbstractSet(x, abs(x)>1))
        EmptySet()
        """
        if isinstance(other, AbstractSet):
            vars1 = self.variables
            vars2 = other.variables
            if not var_type_match(vars1, vars2):
                return EmptySet()

            vars12 = rename_variables_in(vars1, self.free_symbols | other.free_symbols)
            expr12 = (self.expr.xreplace(dict(zip(vars1, vars12))) &~
                      other.expr.xreplace(dict(zip(vars2, vars12))))
            if not satisfiable(expr12):
                return EmptySet()

            return AbstractSet(vars12, expr12)
        else:
            return None

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
        var = self.variables
        val = other if is_Tuple(other) else Tuple(other)
        if not var_type_match(var, val):
            return false
        return simplify(self.expr.xreplace(dict(zip(var, val))))
    
    def is_subset(self, other):
        """
        >>> from sympy import *
        >>> x, y = Symbol('x'), Symbol('y')
        >>> AbstractSet(x, x-y>1).is_subset(AbstractSet(x, (x-y>1)|(x+y>1)))
        True
        >>> AbstractSet((x,y), x-y>1).is_subset(AbstractSet((x,y), abs(x-y)>1))
        Forall((x, y), Or(Abs(x - y) > 1, x - y <= 1))
        """
        if isinstance(other, AbstractSet):
            vars1 = self.variables
            vars2 = other.variables
            if not var_type_match(vars1, vars2):
                return false
            vars12 = rename_variables_in(vars1, self.free_symbols | other.free_symbols)
            return forall(vars12, self._contains(vars12) >> other._contains(vars12))
        else:
            raise ValueError("Unknown argument '%s'" % other)

    def is_disjoint(self, other):
        """
        >>> from sympy import *
        >>> x, y = Symbol('x'), Symbol('y')
        >>> AbstractSet(x, x-y>1).is_disjoint(AbstractSet(x, (x-y<=1)&(x+y>1)))
        True
        >>> AbstractSet((x,y), x-y>1).is_disjoint(AbstractSet((x,y), abs(x-y)<1))
        Forall((x, y), Or(Abs(x - y) >= 1, x - y <= 1))
        """
        if isinstance(other, AbstractSet):
            vars1 = self.variables
            vars2 = other.variables
            if not var_type_match(vars1, vars2):
                return true
            vars12 = rename_variables_in(vars1, self.free_symbols | other.free_symbols)
            return forall(vars12, self._contains(vars12) >> ~other._contains(vars12))
        else:
            raise ValueError("Unknown argument '%s'" % other)

    def is_equivalent(self, other):
        """
        >>> from sympy import *
        >>> x, y = Symbol('x'), Symbol('y')
        >>> AbstractSet(x, x-y>1).is_equivalent(AbstractSet(x, x-y>1))
        True
        >>> AbstractSet(x, x<1).is_equivalent(AbstractSet(x, x-1<0))
        Forall(x, Or(And(x - 1 < 0, x < 1), And(x - 1 >= 0, x >= 1)))
        """
        if isinstance(other, AbstractSet):
            vars1 = self.variables
            vars2 = other.variables
            if not var_type_match(vars1, vars2):
                return false
            vars12 = rename_variables_in(vars1, self.free_symbols | other.free_symbols)
            return forall(vars12, Equivalent(self._contains(vars12),
                                             other._contains(vars12)))
        else:
            raise ValueError("Unknown argument '%s'" % other)


class SetBuilder:
    def __getitem__(self, asets):
        """
        >>> from sympy import *
        >>> x, y = Symbol('x'), Symbol('y')
        >>> St[x : abs(x)>1]
        AbstractSet(x, Abs(x) > 1)
        >>> St[(x, y) : abs(x-y)>1]
        AbstractSet((x, y), Abs(x - y) > 1)
        >>> St[x : x-y>1, x : x<1]
        AbstractSet(x, And(x - y > 1, x < 1))
        >>> St[S.Reals, x : x<1]
        Intersection((-oo, oo), AbstractSet(x, x < 1))
        """
        asets = asets if isinstance(asets, tuple) else (asets,)
        st = UniversalSet()
        for aset in asets:
            if isinstance(aset, slice):
                if aset.start is None or aset.stop is None:
                    raise SyntaxError
                st &= AbstractSet(aset.start, aset.stop)
            elif isinstance(aset, Set):
                st &= aset
            else:
                raise SyntaxError
        return st

    def __call__(self, *asets):
        """
        >>> from sympy import *
        >>> x, y = Symbol('x'), Symbol('y')
        >>> St({x : abs(x)>1})
        AbstractSet(x, Abs(x) > 1)
        >>> St({(x, y) : abs(x-y)>1})
        AbstractSet((x, y), Abs(x - y) > 1)
        >>> St({x : x-y>1}, {x : x<1})
        AbstractSet(x, And(x - y > 1, x < 1))
        >>> St(S.Reals, {x : x<1})
        Intersection((-oo, oo), AbstractSet(x, x < 1))
        """
        st = UniversalSet()
        for aset in asets:
            if isinstance(aset, dict):
                if len(aset) != 1:
                    raise SyntaxError
                st &= AbstractSet(*list(aset.items())[0])
            elif isinstance(aset, Set):
                st &= aset
            else:
                raise SyntaxError
        return st

St = SetBuilder()


def as_dummy(var):
    if isinstance(var, Symbol):
        return var.as_dummy()
    elif isinstance(var, MatrixSymbol):
        return DummyMatrixSymbol('_'+var.name, var.shape[0], var.shape[1])
    else:
        raise TypeError('variable is not a symbol or matrix symbol: %s' % var)

def rename_variables_in(variables, varspace):
    names = [v.name for v in variables]
    namespace = [v.name for v in varspace]
    for i in range(len(names)):
        while names[i] in namespace or names[i] in names[:i]:
            names[i] += '_'
    return list(Symbol(n, **v.assumptions0)
                if isinstance(v, Symbol) else MatrixSymbol(n, v.rows, v.cols)
                for n, v in zip(names, variables))

def var_type_match(vars1, vars2):
    if len(vars1) != len(vars2):
        return false
    for v1, v2 in zip(vars1, vars2):
        if isinstance(v1, Symbol):
            if is_Matrix(v2): # TODO: real/complex test
                return false
        elif isinstance(v1, MatrixSymbol):
            if not is_Matrix(v2) or v1.shape != v2.shape:
                return false
        else:
            raise TypeError('variable is not a symbol or matrix symbol: %s' % v1)
    return true


class Forall(BooleanFunction):
    def __new__(cls, variable, expr):
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

        return Basic.__new__(cls, variable, expr)

    @property
    def variable(self):
        return self._args[0]

    @property
    def variables(self):
        return self._args[0] if is_Tuple(self._args[0]) else Tuple(self._args[0])

    @property
    def expr(self):
        return self._args[1]

    @property
    def free_symbols(self):
        return self.expr.free_symbols - set(self.variables)

    def _hashable_content(self):
        return (self.expr.xreplace(self.canonical_variables),)

class Exist(BooleanFunction):
    def __new__(cls, variable, expr):
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

        return Basic.__new__(cls, variable, expr)

    @property
    def variable(self):
        return self._args[0]

    @property
    def variables(self):
        return self._args[0] if is_Tuple(self._args[0]) else Tuple(self._args[0])

    @property
    def expr(self):
        return self._args[1]

    @property
    def free_symbols(self):
        return self.expr.free_symbols - set(self.variables)

    def _hashable_content(self):
        return (self.expr.xreplace(self.canonical_variables),)

def forall(variables, expr):
    expr = simplify(expr)
    if valid(expr) == True:
        return True
    return Forall(variables, expr)

def exist(variables, expr):
    expr = simplify(expr)
    if satisfiable(expr) == False:
        return False
    return Exist(variables, expr)


if __name__ == '__main__':
    import doctest
    doctest.testmod()
