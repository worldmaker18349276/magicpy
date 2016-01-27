import operator
from sympy.core import S, Tuple, Basic
from sympy.logic import true, false, And, Or, Not, Nand, Implies, Equivalent, to_nnf
from sympy.sets import Set, Intersection, Union, ProductSet, Contains
from symplus.util import *
from symplus.logicplus import Forall, Exist
from symplus.funcplus import Image


class AbstractSet(Set):
    def __new__(cls, variable, expr, **kwargs):
        """create AbstractSet by variable and expression

        >>> from sympy import *
        >>> x, y = symbols('x y')
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
        >>> AbstractSet(x, (x>1)&(x<3))
        AbstractSet(x, And(x < 3, x > 1))
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
        if not is_Boolean(expr) and not is_Symbol(expr):
            raise TypeError('expression is not boolean or relational: %r' % expr)

        if is_Tuple(variable):
            if len(variable) > 1:
                variable = Tuple(*variable)
            else:
                variable = variable[0]

        return Set.__new__(cls, variable, expr, **kwargs)

    @property
    def variable(self):
        """get variable of set builder

        >>> from sympy import *
        >>> x, y = symbols('x y')
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
        >>> x, y = symbols('x y')
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
        >>> x, y = symbols('x y')
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
        >>> x, y = symbols('x y')
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
        >>> x, y = symbols('x y')
        >>> AbstractSet(x, abs(x)>1)._intersect(AbstractSet(y, abs(y)<3))
        AbstractSet(x, And(Abs(x) < 3, Abs(x) > 1))
        >>> AbstractSet(x, abs(x)>1)._intersect(AbstractSet((x,y), abs(x-y)>1))
        EmptySet()
        >>> AbstractSet(x, abs(x)>1)._intersect(AbstractSet(y, y<x))
        AbstractSet(x_, And(Abs(x_) > 1, x_ < x))
        >>> x2 = symbols('x2', positive=True)
        >>> AbstractSet(x, abs(x)>1)._intersect(AbstractSet(x2, x2<y))
        AbstractSet(x, And(Abs(x) > 1, x < y))
        >>> m, n = MatrixSymbol('m', 2, 2), MatrixSymbol('n', 2, 2)
        >>> AbstractSet(m, Eq(m[0,0]+m[1,1],0))._intersect(AbstractSet(n, Eq(det(n),0)))
        AbstractSet(m, And(Determinant(m) == 0, m[0, 0] + m[1, 1] == 0))
        >>> AbstractSet(m, Eq(m[0,0]+m[1,1],0))._intersect(AbstractSet(x, abs(x)>1))
        EmptySet()
        >>> AbstractSet(x, abs(x)>1)._intersect(Interval(1,2))
        AbstractSet(x, And(Abs(x) > 1, x <= 2, x >= 1))
        """
        if isinstance(other, AbstractSet):
            vars1 = self.variables
            vars2 = other.variables
            if not var_type_match(vars1, vars2):
                return S.EmptySet

            vars12 = rename_variables_in(vars1, self.free_symbols | other.free_symbols)
            expr12 = And(self.expr.xreplace(dict(zip(vars1, vars12))),
                         other.expr.xreplace(dict(zip(vars2, vars12))))
            return AbstractSet(vars12, expr12)
        else:
            other_ = as_abstract(other)
            if isinstance(other_, AbstractSet):
                return self._intersect(other_)
            else:
                return None

    def _union(self, other):
        """union two set builder

        >>> from sympy import *
        >>> x, y = symbols('x y')
        >>> AbstractSet(x, abs(x)>1)._union(AbstractSet(y, abs(y)<3))
        AbstractSet(x, Or(Abs(x) < 3, Abs(x) > 1))
        >>> AbstractSet(x, abs(x)>1)._union(AbstractSet((x,y), abs(x-y)>1))
        >>> AbstractSet(x, abs(x)>1)._union(AbstractSet(y, y<x))
        AbstractSet(x_, Or(Abs(x_) > 1, x_ < x))
        >>> x2 = symbols('x2', positive=True)
        >>> AbstractSet(x, abs(x)>1)._union(AbstractSet(x2, x2<y))
        AbstractSet(x, Or(Abs(x) > 1, x < y))
        >>> m, n = MatrixSymbol('m', 2, 2), MatrixSymbol('n', 2, 2)
        >>> AbstractSet(m, Eq(m[0,0]+m[1,1],0))._union(AbstractSet(n, Eq(det(n),0)))
        AbstractSet(m, Or(Determinant(m) == 0, m[0, 0] + m[1, 1] == 0))
        >>> AbstractSet(m, Eq(m[0,0]+m[1,1],0))._union(AbstractSet(x, abs(x)>1))
        >>> AbstractSet(x, abs(x)>1)._union(Interval(1,2))
        AbstractSet(x, Or(Abs(x) > 1, And(x <= 2, x >= 1)))
        """
        if isinstance(other, AbstractSet):
            vars1 = self.variables
            vars2 = other.variables
            if not var_type_match(vars1, vars2):
                return None

            vars12 = rename_variables_in(vars1, self.free_symbols | other.free_symbols)
            expr12 = Or(self.expr.xreplace(dict(zip(vars1, vars12))),
                        other.expr.xreplace(dict(zip(vars2, vars12))))
            return AbstractSet(vars12, expr12)
        else:
            other_ = as_abstract(other)
            if isinstance(other_, AbstractSet):
                return self._union(other_)
            else:
                return None

    def _complement(self, other):
        """complement two set builder

        >>> from sympy import *
        >>> x, y = symbols('x y')
        >>> AbstractSet(x, abs(x)>1)._complement(AbstractSet(y, abs(y)<=3))
        AbstractSet(x, And(Abs(x) > 1, Abs(x) > 3))
        >>> AbstractSet(x, abs(x)>1)._complement(AbstractSet((x,y), abs(x-y)>1))
        EmptySet()
        >>> AbstractSet(x, abs(x)>1)._complement(AbstractSet(y, y<=x))
        AbstractSet(x_, And(Abs(x_) > 1, x_ > x))
        >>> x2 = symbols('x2', positive=True)
        >>> AbstractSet(x, abs(x)>1)._complement(AbstractSet(x2, x2<=y))
        AbstractSet(x, And(Abs(x) > 1, x > y))
        >>> m, n = MatrixSymbol('m', 2, 2), MatrixSymbol('n', 2, 2)
        >>> AbstractSet(m, Eq(m[0,0]+m[1,1],0))._complement(AbstractSet(n, Eq(det(n),0)))
        AbstractSet(m, And(Determinant(m) != 0, m[0, 0] + m[1, 1] == 0))
        >>> AbstractSet(m, Eq(m[0,0]+m[1,1],0))._complement(AbstractSet(x, abs(x)>1))
        EmptySet()
        >>> AbstractSet(x, abs(x)>1)._complement(Interval(1,2))
        AbstractSet(x, Or(Abs(x) > 1, And(x <= 2, x >= 1)))
        """
        if isinstance(other, AbstractSet):
            vars1 = self.variables
            vars2 = other.variables
            if not var_type_match(vars1, vars2):
                return S.EmptySet

            vars12 = rename_variables_in(vars1, self.free_symbols | other.free_symbols)
            expr12 = And(self.expr.xreplace(dict(zip(vars1, vars12))),
                         Not(other.expr.xreplace(dict(zip(vars2, vars12)))))
            return AbstractSet(vars12, expr12)
        else:
            other_ = as_abstract(other)
            if isinstance(other_, AbstractSet):
                return self._union(other_)
            else:
                return None

    def _contains(self, other):
        """
        >>> from sympy import *
        >>> x, y, z = symbols('x y z')
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
        return self.expr.xreplace(dict(zip(var, val)))
    
    def is_subset(self, other):
        """
        >>> from sympy import *
        >>> x, y = symbols('x y')
        >>> AbstractSet(x, x-y>1).is_subset(AbstractSet(x, (x-y>1)|(x+y>1)))
        True
        >>> AbstractSet((x,y), x-y>1).is_subset(AbstractSet((x,y), abs(x-y)>1))
        Forall((x, y), Implies(x - y > 1, Abs(x - y) > 1))
        >>> AbstractSet(x, abs(x)>1).is_subset(Interval(1,2))
        Forall(x, Implies(Abs(x) > 1, And(x <= 2, x >= 1)))
        """
        if isinstance(other, AbstractSet):
            vars1 = self.variables
            vars2 = other.variables
            if not var_type_match(vars1, vars2):
                return false
            vars12 = rename_variables_in(vars1, self.free_symbols | other.free_symbols)
            return Forall(vars12,
                          Implies(self.expr.xreplace(dict(zip(vars1, vars12))),
                                  other.expr.xreplace(dict(zip(vars2, vars12)))))
        else:
            other_ = as_abstract(other)
            if isinstance(other_, AbstractSet):
                return self.is_subset(other_)
            else:
                raise ValueError("Unknown argument '%s'" % other)

    def is_disjoint(self, other):
        """
        >>> from sympy import *
        >>> x, y = symbols('x y')
        >>> AbstractSet(x, x-y>1).is_disjoint(AbstractSet(x, (x-y<=1)&(x+y>1)))
        True
        >>> AbstractSet((x,y), x-y>1).is_disjoint(AbstractSet((x,y), abs(x-y)<1))
        Forall((x, y), Not(And(Abs(x - y) < 1, x - y > 1)))
        >>> AbstractSet(x, abs(x)>1).is_disjoint(Interval(1,2))
        Forall(x, Not(And(Abs(x) > 1, x <= 2, x >= 1)))
        """
        if isinstance(other, AbstractSet):
            vars1 = self.variables
            vars2 = other.variables
            if not var_type_match(vars1, vars2):
                return true
            vars12 = rename_variables_in(vars1, self.free_symbols | other.free_symbols)
            return Forall(vars12,
                          Nand(self.expr.xreplace(dict(zip(vars1, vars12))),
                               other.expr.xreplace(dict(zip(vars2, vars12)))))
        else:
            other_ = as_abstract(other)
            if isinstance(other_, AbstractSet):
                return self.is_disjoint(other_)
            else:
                raise ValueError("Unknown argument '%s'" % other)

    def is_equivalent(self, other):
        """
        >>> from sympy import *
        >>> x, y = symbols('x y')
        >>> AbstractSet(x, x-y>1).is_equivalent(AbstractSet(x, x-y>1))
        True
        >>> AbstractSet(x, x<1).is_equivalent(AbstractSet(x, x-1<0))
        Forall(x, Equivalent(x < 1, x - 1 < 0))
        >>> AbstractSet(x, abs(x)>1).is_equivalent(Interval(1,2))
        Forall(x, Equivalent(Abs(x) > 1, And(x <= 2, x >= 1)))
        """
        if isinstance(other, AbstractSet):
            vars1 = self.variables
            vars2 = other.variables
            if not var_type_match(vars1, vars2):
                return false
            vars12 = rename_variables_in(vars1, self.free_symbols | other.free_symbols)
            return Forall(vars12,
                          Equivalent(self.expr.xreplace(dict(zip(vars1, vars12))),
                                     other.expr.xreplace(dict(zip(vars2, vars12)))))
        else:
            other_ = as_abstract(other)
            if isinstance(other_, AbstractSet):
                return self.is_equivalent(other_)
            else:
                raise ValueError("Unknown argument '%s'" % other)

    def is_proper_subset(self, other):
        """
        >>> from sympy import *
        >>> x, y = symbols('x y')
        >>> AbstractSet(x, x-y>1).is_proper_subset(AbstractSet(x, x-y>1))
        False
        >>> AbstractSet(x, x-y>1).is_proper_subset(AbstractSet(x, (x-y>1)|(x+y>1)))
        Not(Forall(x, Equivalent(x - y > 1, Or(x + y > 1, x - y > 1))))
        """
        if isinstance(other, AbstractSet):
            return And(Not(self.is_equivalent(other)), self.is_subset(other))
        else:
            raise ValueError("Unknown argument '%s'" % other)

    def is_empty(self):
        """
        >>> from sympy import *
        >>> x, y = symbols('x y')
        >>> AbstractSet(x, false).is_empty()
        True
        >>> AbstractSet(x, (x>0)&(x<0))
        AbstractSet(x, And(x < 0, x > 0))
        >>> _.is_empty()
        Forall(x, Not(And(x < 0, x > 0)))
        """
        return Forall(self.variables, Not(self.expr))

    def expand(self, depth=-1):
        """
        >>> from sympy import *
        >>> x, y = symbols('x y')
        >>> AbstractSet(x, (x>0)&(x<0))
        AbstractSet(x, And(x < 0, x > 0))
        >>> _.expand()
        Intersection(AbstractSet(x, x > 0), AbstractSet(x, x < 0))
        >>> AbstractSet((x,y), (x>0)>>(y>1))
        AbstractSet((x, y), Implies(x > 0, y > 1))
        >>> _.expand()
        AbstractSet((x, y), x <= 0) U AbstractSet((x, y), y > 1)
        """
        def expand0(var, expr, dp):
            if dp == 0:
                return AbstractSet(var, expr)
            if isinstance(expr, Or):
                return Union(*[expand0(var, arg, dp-1) for arg in expr.args],
                             evaluate=False)
            elif isinstance(expr, And):
                return Intersection(*[expand0(var, arg, dp-1) for arg in expr.args],
                                    evaluate=False)
            else:
                return AbstractSet(var, expr)
        return expand0(self.variable, to_nnf(self.expr), depth)

    def __mul__(self, other):
        prod = self._eval_product(other)
        if prod is None:
            return ProductSet(self, other)
        else:
            return prod

    def _eval_product(self, other):
        """
        >>> from sympy import *
        >>> x, y = symbols('x y')
        >>> AbstractSet(x, abs(x)>1)._eval_product(AbstractSet(y, y<x))
        AbstractSet((x, y), And(Abs(x) > 1, y < x))
        >>> AbstractSet(x, abs(x)>1)._eval_product(AbstractSet((x,y), abs(x-y)>1))
        AbstractSet((x, x_, y), And(Abs(x) > 1, Abs(x_ - y) > 1))
        """
        if isinstance(other, AbstractSet):
            vars1 = self.variables
            expr1 = self.expr
            vars2 = other.variables
            expr2 = other.expr
            vars2_ = rename_variables_in(vars2, self.free_symbols|set(vars1))
            expr2_ = expr2.xreplace(dict(zip(vars2, vars2_)))
            return AbstractSet(tuple(vars1)+tuple(vars2_), And(expr1, expr2_))
        else:
            return None


class SetBuilder:
    def __getitem__(self, asets):
        """
        >>> from sympy import *
        >>> x, y = symbols('x y')
        >>> St[x : abs(x)>1]
        AbstractSet(x, Abs(x) > 1)
        >>> St[(x, y) : abs(x-y)>1]
        AbstractSet((x, y), Abs(x - y) > 1)
        >>> St[x : x-y>1, x : x<1]
        AbstractSet(x, And(x - y > 1, x < 1))
        >>> St[S.Reals, x : x<1]
        AbstractSet(x, And(x < 1, x < oo, x > -oo))
        """
        asets = asets if isinstance(asets, tuple) else (asets,)
        sts = []
        for aset in asets:
            if isinstance(aset, slice):
                if aset.start is None or aset.stop is None:
                    raise SyntaxError
                sts.append(AbstractSet(aset.start, aset.stop))
            elif isinstance(aset, Set):
                sts.append(aset)
            else:
                raise SyntaxError

        if len(sts) == 0:
            return S.UniversalSet
        if len(sts) == 1:
            return sts[0]
        else:
            return Intersection(*sts)

    def __call__(self, *asets, evaluate=True):
        """
        >>> from sympy import *
        >>> x, y = symbols('x y')
        >>> St({x : abs(x)>1})
        AbstractSet(x, Abs(x) > 1)
        >>> St({(x, y) : abs(x-y)>1})
        AbstractSet((x, y), Abs(x - y) > 1)
        >>> St({x : x-y>1}, {x : x<1})
        AbstractSet(x, And(x - y > 1, x < 1))
        >>> St(S.Reals, {x : x<1})
        AbstractSet(x, And(x < 1, x < oo, x > -oo))
        """
        sts = []
        for aset in asets:
            if isinstance(aset, dict):
                if len(aset) != 1:
                    raise SyntaxError
                sts.append(AbstractSet(*list(aset.items())[0]))
            elif isinstance(aset, Set):
                sts.append(aset)
            else:
                raise SyntaxError

        if len(sts) == 0:
            return S.UniversalSet
        if len(sts) == 1:
            return sts[0]
        else:
            return Intersection(*sts, evaluate=evaluate)

St = SetBuilder()


def as_abstract(aset):
    if isinstance(aset, ProductSet):
        args = tuple(as_abstract(arg) for arg in aset.args)
        if all(isinstance(arg, AbstractSet) for arg in args):
            return reduce(operator.mul, args)
        else:
            return aset
    else:
        narg = len(aset.variables) if isinstance(aset, (AbstractSet, Image)) else 1
        x = Symbol('x:%d'%narg, real=True)
        expr = aset.contains(x)
        if expr.has(Contains):
            return aset
        else:
            return AbstractSet(x, expr)


class Topology(Basic):
    def __new__(cls, space):
        if not isinstance(space, Set):
            raise TypeError
        return Basic.__new__(cls, space)

    @property
    def space(self):
        return self.args[0]

    def contains(self, other):
        return self.space.is_superset(other) & other.is_open()

    def __contains__(self, other):
        symb = self.contains(other)
        if symb not in (true, false):
            raise TypeError('contains did not evaluate to a bool: %r' % symb)
        return bool(symb)

