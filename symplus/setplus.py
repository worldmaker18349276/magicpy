import operator
from functools import reduce
from sympy.core import S, Basic, Atom, Symbol, Dummy, sympify, Ne, Eq, Gt, Ge, Lt, Le, oo, symbols
from sympy.core.function import Application
from sympy.core.evaluate import global_evaluate
from sympy.logic import true, false, And, Or, Not, Nand, Implies, Equivalent, to_dnf
from sympy.logic.boolalg import Boolean, simplify_logic
from sympy.functions import Id
from sympy.sets import Set, Interval, FiniteSet, Intersection, Union, Complement, ProductSet
from symplus.typlus import (is_Symbol, is_Function, is_Boolean, type_match, FunctionObject, pack_if_not,
                            unpack_if_can, repack_if_can, free_symbols, rename_variables_in)
from symplus.funcplus import FunctionCompose, FunctionInverse, as_lambda, nres
from symplus.logicplus import Forall


class AbstractSet(Set):
    def __new__(cls, variable, expr, **kwargs):
        """create AbstractSet by variable and expression

        >>> from sympy import *
        >>> from symplus.strplus import init_mprinting
        >>> init_mprinting()
        >>> x, y = symbols('x y')
        >>> AbstractSet(x, abs(x)>1)
        {x | |x| > 1}
        >>> AbstractSet((x,), abs(x)>1)
        {x | |x| > 1}
        >>> AbstractSet((x, y), abs(x-y)>1)
        {(x, y) | |x - y| > 1}
        >>> AbstractSet([x, y], abs(x-y)>1)
        {(x, y) | |x - y| > 1}
        >>> m, n = MatrixSymbol('m', 2, 2), MatrixSymbol('n', 2, 2)
        >>> AbstractSet(m, Eq(m[0,0]+m[1,1],0))
        {m | 0 == m[0, 0] + m[1, 1]}
        >>> AbstractSet((m, x), Eq(det(m),x))
        {(m, x) | x == ||m||}
        >>> AbstractSet(x, (x>1)&(x<3))
        {x | (x < 3) /\ (x > 1)}
        >>> AbstractSet(x, x>y)
        {x | x > y}
        >>> AbstractSet(1, x>y)
        Traceback (most recent call last):
            ...
        TypeError: variable is not a symbol or matrix symbol: 1
        >>> AbstractSet(x, x+y)
        Traceback (most recent call last):
            ...
        TypeError: expression is not boolean or relational: x + y
        """
        variable = repack_if_can(sympify(unpack_if_can(variable)))
        for v in pack_if_not(variable):
            if not is_Symbol(v):
                raise TypeError('variable is not a symbol or matrix symbol: %s' % v)
        if not is_Boolean(expr):
            raise TypeError('expression is not boolean or relational: %r' % expr)

        return Set.__new__(cls, variable, expr, **kwargs)

    @property
    def variable(self):
        """get variable of set builder

        >>> from sympy import *
        >>> from symplus.strplus import init_mprinting
        >>> init_mprinting()
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
        >>> from symplus.strplus import init_mprinting
        >>> init_mprinting()
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
        return pack_if_not(self._args[0])

    @property
    def expr(self):
        """get expression of set builder

        >>> from sympy import *
        >>> from symplus.strplus import init_mprinting
        >>> init_mprinting()
        >>> x, y = symbols('x y')
        >>> AbstractSet(x, abs(x)>1).expr
        |x| > 1
        >>> AbstractSet((x,), abs(x)>1).expr
        |x| > 1
        >>> AbstractSet((x,y), abs(x-y)>1).expr
        |x - y| > 1
        >>> AbstractSet(x, x>y).expr
        x > y
        """
        return self._args[1]

    @property
    def free_symbols(self):
        """get free symbols of set builder

        >>> from sympy import *
        >>> from symplus.strplus import init_mprinting
        >>> init_mprinting()
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
        return free_symbols(self.expr) - set(self.variables)

    def _hashable_content(self):
        return (self.expr.xreplace(self.canonical_variables),)

    def _intersect(self, other):
        """intersect two set builder

        >>> from sympy import *
        >>> from symplus.strplus import init_mprinting
        >>> init_mprinting()
        >>> x, y = symbols('x y')
        >>> AbstractSet(x, abs(x)>1)._intersect(AbstractSet(y, abs(y)<3))
        {x | (|x| < 3) /\ (|x| > 1)}
        >>> AbstractSet(x, abs(x)>1)._intersect(AbstractSet((x,y), abs(x-y)>1))
        (/)
        >>> AbstractSet(x, abs(x)>1)._intersect(AbstractSet(y, y<x))
        {x_ | (x_ < x) /\ (|x_| > 1)}
        >>> x2 = symbols('x2', positive=True)
        >>> AbstractSet(x, abs(x)>1)._intersect(AbstractSet(x2, x2<y))
        {x | (x < y) /\ (|x| > 1)}
        >>> m, n = MatrixSymbol('m', 2, 2), MatrixSymbol('n', 2, 2)
        >>> AbstractSet(m, Eq(m[0,0]+m[1,1],0))._intersect(AbstractSet(n, Eq(det(n),0)))
        {m | (0 == m[0, 0] + m[1, 1]) /\ (0 == ||m||)}
        >>> AbstractSet(m, Eq(m[0,0]+m[1,1],0))._intersect(AbstractSet(x, abs(x)>1))
        (/)
        >>> AbstractSet(x, abs(x)>1)._intersect(Interval(1,2))
        """
        if isinstance(other, AbstractSet):
            vars1 = self.variables
            vars2 = other.variables
            if not type_match(vars1, vars2):
                return S.EmptySet

            vars12 = rename_variables_in(vars1, free_symbols(self) | free_symbols(other))
            expr12 = And(self.expr.xreplace(dict(zip(vars1, vars12))),
                         other.expr.xreplace(dict(zip(vars2, vars12))))
            return AbstractSet(vars12, expr12)

    def _union(self, other):
        """union two set builder

        >>> from sympy import *
        >>> from symplus.strplus import init_mprinting
        >>> init_mprinting()
        >>> x, y = symbols('x y')
        >>> AbstractSet(x, abs(x)>1)._union(AbstractSet(y, abs(y)<3))
        {x | (|x| < 3) \/ (|x| > 1)}
        >>> AbstractSet(x, abs(x)>1)._union(AbstractSet((x,y), abs(x-y)>1))
        >>> AbstractSet(x, abs(x)>1)._union(AbstractSet(y, y<x))
        {x_ | (x_ < x) \/ (|x_| > 1)}
        >>> x2 = symbols('x2', positive=True)
        >>> AbstractSet(x, abs(x)>1)._union(AbstractSet(x2, x2<y))
        {x | (x < y) \/ (|x| > 1)}
        >>> m, n = MatrixSymbol('m', 2, 2), MatrixSymbol('n', 2, 2)
        >>> AbstractSet(m, Eq(m[0,0]+m[1,1],0))._union(AbstractSet(n, Eq(det(n),0)))
        {m | (0 == m[0, 0] + m[1, 1]) \/ (0 == ||m||)}
        >>> AbstractSet(m, Eq(m[0,0]+m[1,1],0))._union(AbstractSet(x, abs(x)>1))
        >>> AbstractSet(x, abs(x)>1)._union(Interval(1,2))
        """
        if isinstance(other, AbstractSet):
            vars1 = self.variables
            vars2 = other.variables
            if not type_match(vars1, vars2):
                return None

            vars12 = rename_variables_in(vars1, free_symbols(self) | free_symbols(other))
            expr12 = Or(self.expr.xreplace(dict(zip(vars1, vars12))),
                        other.expr.xreplace(dict(zip(vars2, vars12))))
            return AbstractSet(vars12, expr12)

    def _complement(self, other):
        """complement two set builder

        >>> from sympy import *
        >>> from symplus.strplus import init_mprinting
        >>> init_mprinting()
        >>> x, y = symbols('x y')
        >>> AbstractSet(y, abs(y)<=3)._complement(AbstractSet(x, abs(x)>1))
        {y | (|y| > 1) /\ (|y| > 3)}
        >>> AbstractSet((x,y), abs(x-y)>1)._complement(AbstractSet(x, abs(x)>1))
        {x | |x| > 1}
        >>> AbstractSet(y, y<=x)._complement(AbstractSet(x, abs(x)>1))
        {y | (y > x) /\ (|y| > 1)}
        >>> x2 = symbols('x2', positive=True)
        >>> AbstractSet(x, abs(x)>1)._complement(AbstractSet(x2, x2<=y))
        {x | (x =< y) /\ (|x| =< 1)}
        >>> m, n = MatrixSymbol('m', 2, 2), MatrixSymbol('n', 2, 2)
        >>> AbstractSet(n, Eq(det(n),0))._complement(AbstractSet(m, Eq(m[0,0]+m[1,1],0)))
        {n | (0 =/= ||n||) /\ (0 == n[0, 0] + n[1, 1])}
        >>> AbstractSet(x, abs(x)>1)._complement(AbstractSet(m, Eq(m[0,0]+m[1,1],0)))
        {m | 0 == m[0, 0] + m[1, 1]}
        >>> AbstractSet(x, abs(x)>1)._complement(Interval(1,2))
        """
        if isinstance(other, AbstractSet):
            vars1 = self.variables
            vars2 = other.variables
            if not type_match(vars1, vars2):
                return other

            vars12 = rename_variables_in(vars1, free_symbols(self) | free_symbols(other))
            expr12 = And(other.expr.xreplace(dict(zip(vars2, vars12))),
                         Not(self.expr.xreplace(dict(zip(vars1, vars12)))))
            return AbstractSet(vars12, expr12)

    def _absolute_complement(self):
        return AbstractSet(self.variables, Not(self.expr))

    def contains(self, other):
        other = sympify(other, strict=True)
        ret = sympify(self._contains(other))
        if ret is None:
            ret = Contains(other, self, evaluate=False)
        return ret

    def _contains(self, other):
        """
        >>> from sympy import *
        >>> from symplus.strplus import init_mprinting
        >>> init_mprinting()
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
        val = pack_if_not(other)
        if not type_match(var, val):
            return false
        return self.expr.xreplace(dict(zip(var, val)))

    def _image(self, func):
        if getattr(func, "is_invertible", False):
            inv_func = FunctionInverse(func, evaluate=True)
            if not isinstance(inv_func, FunctionInverse):
                inv_func = as_lambda(inv_func)
                return AbstractSet(inv_func.variables,
                                   self.contains(inv_func.expr))
    
    def is_subset(self, other):
        """
        >>> from sympy import *
        >>> from symplus.strplus import init_mprinting
        >>> init_mprinting()
        >>> x, y = symbols('x y')
        >>> AbstractSet(x, x-y>1).is_subset(AbstractSet(x, (x-y>1)|(x+y>1)))
        True
        >>> AbstractSet((x,y), x-y>1).is_subset(AbstractSet((x,y), abs(x-y)>1))
        A. x, y st (x - y > 1) => (|x - y| > 1)
        >>> AbstractSet(x, abs(x)>1).is_subset(Interval(1,2))
        A. x st (|x| > 1) => (x =< 2) /\ (x >= 1)
        """
        if isinstance(other, AbstractSet):
            vars1 = self.variables
            vars2 = other.variables
            if not type_match(vars1, vars2):
                return false
            vars12 = rename_variables_in(vars1, free_symbols(self) | free_symbols(other))
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
        >>> from symplus.strplus import init_mprinting
        >>> init_mprinting()
        >>> x, y = symbols('x y')
        >>> AbstractSet(x, x-y>1).is_disjoint(AbstractSet(x, (x-y<=1)&(x+y>1)))
        True
        >>> AbstractSet((x,y), x-y>1).is_disjoint(AbstractSet((x,y), abs(x-y)<1))
        A. x, y st ~((x - y > 1) /\ (|x - y| < 1))
        >>> AbstractSet(x, abs(x)>1).is_disjoint(Interval(1,2))
        A. x st ~((x =< 2) /\ (x >= 1) /\ (|x| > 1))
        """
        if isinstance(other, AbstractSet):
            vars1 = self.variables
            vars2 = other.variables
            if not type_match(vars1, vars2):
                return true
            vars12 = rename_variables_in(vars1, free_symbols(self) | free_symbols(other))
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
        >>> from symplus.strplus import init_mprinting
        >>> init_mprinting()
        >>> x, y = symbols('x y')
        >>> AbstractSet(x, x-y>1).is_equivalent(AbstractSet(x, x-y>1))
        True
        >>> AbstractSet(x, x<1).is_equivalent(AbstractSet(x, x-1<0))
        A. x st (x - 1 < 0) <=> (x < 1)
        >>> AbstractSet(x, abs(x)>1).is_equivalent(Interval(1,2))
        A. x st (x =< 2) /\ (x >= 1) <=> (|x| > 1)
        """
        if isinstance(other, AbstractSet):
            vars1 = self.variables
            vars2 = other.variables
            if not type_match(vars1, vars2):
                return false
            vars12 = rename_variables_in(vars1, free_symbols(self) | free_symbols(other))
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
        >>> from symplus.strplus import init_mprinting
        >>> init_mprinting()
        >>> x, y = symbols('x y')
        >>> AbstractSet(x, x-y>1).is_proper_subset(AbstractSet(x, x-y>1))
        False
        >>> AbstractSet(x, x-y>1).is_proper_subset(AbstractSet(x, (x-y>1)|(x+y>1)))
        ~(A. x st (x + y > 1) \/ (x - y > 1) <=> (x - y > 1))
        """
        if isinstance(other, AbstractSet):
            return And(Not(self.is_equivalent(other)), self.is_subset(other))
        else:
            raise ValueError("Unknown argument '%s'" % other)

    def is_empty(self):
        """
        >>> from sympy import *
        >>> from symplus.strplus import init_mprinting
        >>> init_mprinting()
        >>> x, y = symbols('x y')
        >>> AbstractSet(x, false).is_empty()
        True
        >>> AbstractSet(x, (x>0)&(x<0))
        {x | (x < 0) /\ (x > 0)}
        >>> _.is_empty()
        A. x st ~((x < 0) /\ (x > 0))
        """
        return Forall(self.variables, Not(self.expr))

    @property
    def _boundary(self):
        if isinstance(self.expr, (Or, And)):
            return self.expand()._boundary
        elif isinstance(self.expr, Rel):
            return AbstractSet(self.variables, Eq(self.expr.args[0], self.expr.args[1]))
        else:
            raise NotImplementedError

    def expand(self, depth=-1):
        """
        >>> from sympy import *
        >>> from symplus.strplus import init_mprinting
        >>> init_mprinting()
        >>> x, y = symbols('x y')
        >>> AbstractSet(x, (x>0)&(x<0))
        {x | (x < 0) /\ (x > 0)}
        >>> _.expand()
        {x | x < 0} n {x | x > 0}
        >>> AbstractSet((x,y), (x>0)>>(y>1))
        {(x, y) | (x > 0) => (y > 1)}
        >>> _.expand()
        {(x, y) | x =< 0} u {(x, y) | y > 1}
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
        return expand0(self.variable, to_dnf(self.expr), depth)

    def __mul__(self, other):
        prod = self._eval_product(other)
        if prod is None:
            return ProductSet(self, other)
        else:
            return prod

    def _eval_product(self, other):
        """
        >>> from sympy import *
        >>> from symplus.strplus import init_mprinting
        >>> init_mprinting()
        >>> x, y = symbols('x y')
        >>> AbstractSet(x, abs(x)>1)._eval_product(AbstractSet(y, y<x))
        {(x, y) | (y < x) /\ (|x| > 1)}
        >>> AbstractSet(x, abs(x)>1)._eval_product(AbstractSet((x,y), abs(x-y)>1))
        {(x, x_, y) | (|x_ - y| > 1) /\ (|x| > 1)}
        """
        if isinstance(other, AbstractSet):
            vars1 = self.variables
            expr1 = self.expr
            vars2 = other.variables
            expr2 = other.expr
            vars2_ = rename_variables_in(vars2, free_symbols(self)|set(vars1))
            expr2_ = expr2.xreplace(dict(zip(vars2, vars2_)))
            return AbstractSet(tuple(vars1)+tuple(vars2_), And(expr1, expr2_))
        else:
            return None

    def _eval_Eq(self, other):
        return self.is_equivalent(other)

    def _mathstr(self, printer):
        return '{{{0} | {1}}}'.format(*map(printer._print, self.args))

class AbsoluteComplement(Set):
    def __new__(cls, set, **kwargs):
        evaluate = kwargs.pop('evaluate', global_evaluate[0])
        if evaluate:
            res = AbsoluteComplement.eval(set)
            if res is not None:
                return res
        return Set.__new__(cls, set, **kwargs)

    @staticmethod
    def eval(zet):
        """
        >>> from sympy import *
        >>> from symplus.strplus import init_mprinting
        >>> init_mprinting()
        >>> AbsoluteComplement(Interval(0,1, False, False))
        (-oo, 0) u (1, oo)
        >>> AbsoluteComplement(Interval(1,2, True, False))
        (-oo, 1] u (2, oo)
        >>> AbsoluteComplement(Interval(1,oo, False, False))
        (-oo, 1)
        >>> AbsoluteComplement(Interval(1,2, False, False) * Interval(0,1, False, False))
        -([1, 2] x [0, 1])
        >>> x,y = symbols('x y')
        >>> AbsoluteComplement(AbstractSet(x, x**2<1))
        {x | x**2 >= 1}
        >>> AbsoluteComplement(AbstractSet(x, (x<4)|(x>=6)))
        {x | ~((x < 4) \/ (x >= 6))}
        >>> AbsoluteComplement(AbstractSet((x,y), x<=y))
        {(x, y) | x > y}
        """
        if isinstance(zet, Interval):
            return zet.complement(S.Reals)

        elif isinstance(zet, Union):
            return Intersection(*[AbsoluteComplement(arg, evaluate=True)
                                  for arg in zet.args])

        elif isinstance(zet, Intersection):
            return Union(*[AbsoluteComplement(arg, evaluate=True)
                           for arg in zet.args])

        elif isinstance(zet, Complement):
            return Union(AbsoluteComplement(zet.args[0], evaluate=True),
                         zet.args[1])

        elif isinstance(zet, AbsoluteComplement):
            return zet.args[0]

        elif hasattr(zet, "_absolute_complement"):
            return zet._absolute_complement()

        else:
            return None

    @property
    def set(self):
        return self.args[0]

    @property
    def is_open(self):
        return Not(self.set.is_open)

    @property
    def is_closed(self):
        return Not(self.set.is_closed)

    def _absolute_complement(self):
        return self.set

    def _mathstr(self, printer):
        if isinstance(self.args[0], (Atom, AbsoluteComplement)):
            return '-'+printer._print(self.args[0])
        else:
            return '-({0})'.format(printer._print(self.args[0]))

class SetBuilder(object):
    def __getitem__(self, zets):
        """
        >>> from sympy import *
        >>> from symplus.strplus import init_mprinting
        >>> init_mprinting()
        >>> x, y = symbols('x y')
        >>> St[x : abs(x)>1]
        {x | |x| > 1}
        >>> St[(x, y) : abs(x-y)>1]
        {(x, y) | |x - y| > 1}
        >>> St[x : x-y>1, x : x<1]
        {x | (x - y > 1) /\ (x < 1)}
        >>> St[S.Reals, x : x<1]
        (-oo, oo) n {x | x < 1}
        """
        zets = zets if isinstance(zets, tuple) else (zets,)
        sts = []
        for zet in zets:
            if isinstance(zet, slice):
                if zet.start is None or zet.stop is None:
                    raise SyntaxError
                sts.append(AbstractSet(zet.start, zet.stop))
            elif isinstance(zet, Set):
                sts.append(zet)
            else:
                raise SyntaxError

        if len(sts) == 0:
            return S.UniversalSet
        if len(sts) == 1:
            return sts[0]
        else:
            return Intersection(*sts)

    def __call__(self, *zets, **kwargs):
        """
        >>> from sympy import *
        >>> from symplus.strplus import init_mprinting
        >>> init_mprinting()
        >>> x, y = symbols('x y')
        >>> St({x : abs(x)>1})
        {x | |x| > 1}
        >>> St({(x, y) : abs(x-y)>1})
        {(x, y) | |x - y| > 1}
        >>> St({x : x-y>1}, {x : x<1})
        {x | (x - y > 1) /\ (x < 1)}
        >>> St(S.Reals, {x : x<1})
        (-oo, oo) n {x | x < 1}
        """
        evaluate = kwargs.pop("evaluate", True)
        sts = []
        for zet in zets:
            if isinstance(zet, dict):
                if len(zet) != 1:
                    raise SyntaxError
                sts.append(AbstractSet(*list(zet.items())[0]))
            elif isinstance(zet, Set):
                sts.append(zet)
            else:
                raise SyntaxError

        if len(sts) == 0:
            return S.UniversalSet
        if len(sts) == 1:
            return sts[0]
        else:
            return Intersection(*sts, evaluate=evaluate)

St = SetBuilder()

def as_abstract(zet):
    if hasattr(zet, 'as_abstract'):
        return zet.as_abstract()

    elif isinstance(zet, ProductSet):
        args = tuple(as_abstract(arg) for arg in zet.args)
        if all(isinstance(arg, AbstractSet) for arg in args):
            return reduce(operator.mul, args)
        else:
            return zet

    elif isinstance(zet, (Intersection, Union, Complement, AbsoluteComplement)):
        return zet.func(*[as_abstract(e) for e in zet.args])

    else:
        x = Symbol('x', real=True)
        x = rename_variables_in(x, free_symbols(zet))
        expr = zet.contains(x)
        return AbstractSet(x, expr)


class Image(Set):
    """
    >>> from sympy import *
    >>> from symplus.strplus import init_mprinting
    >>> init_mprinting()
    >>> from symplus.funcplus import *
    >>> Image(sin, Interval(0, pi/2))
    {sin(a0) | a0 in [0, pi/2]}
    >>> Image(exp, Image(sin, Interval(0, pi/2)))
    {exp(sin(a0)) | a0 in [0, pi/2]}
    >>> Image(FunctionInverse(sin), Image(sin, Interval(0, pi/2)))
    [0, pi/2]
    >>> Image(cos, S.EmptySet)
    (/)
    >>> x, y = symbols('x y')
    >>> Image(cos, AbstractSet(x, x > 0))
    {cos(x) | x > 0}
    >>> Image(cos, Intersection(AbstractSet(x, x > 0), AbstractSet(x, x < 0), evaluate=False))
    {cos(x) | x < 0} n {cos(x) | x > 0}
    >>> Image(Lambda(x, sin(x)+x), Interval(-1, 1)).contains(1)
    1 in Image(Lambda(x, x + sin(x)), [-1, 1])
    >>> f = Lambda(x, x+1)
    >>> f.is_invertible = True
    >>> Image(f, Interval(-1, 1)).contains(1)
    True
    >>> Image(f, Interval(-1, 1)).as_abstract()
    {x0 | (x0 - 1 =< 1) /\ (x0 - 1 >= -1)}
    """
    def __new__(cls, function, zet, **kwargs):
        evaluate = kwargs.pop('evaluate', global_evaluate[0])

        if not is_Function(function):
            raise TypeError('function is not a FunctionClass, FunctionObject or Lambda: %s'%function)
        if not isinstance(zet, Set):
            raise TypeError('zet is not a Set: %s'%zet)

        if evaluate:
            function, zet = Image.reduce(function, zet)

        if function == Id:
            return zet
        else:
            return Set.__new__(cls, function, zet, **kwargs)

    @staticmethod
    def reduce(func, zet):
        def pre_reduce(func, zet):
            while isinstance(zet, Image):
                func = FunctionCompose(func, zet.function, evaluate=True)
                zet = zet.set

            if isinstance(zet, (Intersection, Union, Complement, AbsoluteComplement)):
                args = [Image(func, arg, evaluate=True) for arg in zet.args]
                return Id, zet.func(*args, evaluate=False)

            if zet == S.EmptySet:
                return Id, zet

            return func, zet

        def post_reduce(func, zet):
            if isinstance(func, FunctionCompose):
                funcs = func.functions
                while True:
                    func_, zet_ = post_reduce(funcs[-1], zet)
                    if (func_, zet_) == (funcs[-1], zet):
                        break
                    elif func_ != Id:
                        funcs = funcs[:-1] + (func_,)
                        zet = zet_
                        break
                    elif len(funcs) == 1:
                        funcs = ()
                        zet = zet_
                        break
                    else:
                        funcs = funcs[:-1]
                        zet = zet_
                return FunctionCompose(*funcs, evaluate=False), zet

            elif hasattr(zet, '_image'):
                res = zet._image(func)
                if res is not None:
                    if isinstance(res, Image):
                        return res.function, res.set
                    else:
                        return Id, res
                else:
                    return func, zet

            else:
                return func, zet

        return post_reduce(*pre_reduce(func, zet))

    @property
    def function(self):
        return self._args[0]

    @property
    def set(self):
        return self._args[1]

    def _contains(self, mem):
        if getattr(self.function, "is_invertible", False):
            mem_ = unpack_if_can(FunctionInverse(self.function)(*pack_if_not(mem)))
            return self.set._contains(mem_)

    def as_abstract(self):
        narg = nres(self.function)
        x = symbols('x:%d'%narg, real=True)
        expr = self.contains(x)
        return AbstractSet(x, expr)

    def _mathstr(self, printer):
        if isinstance(self.set, AbstractSet):
            varstr = printer._print(self.function(*self.set.variables))
            exprstr = printer._print(self.set.expr)
            return '{{{0} | {1}}}'.format(varstr, exprstr)
        else:
            func = as_lambda(self.function)
            if len(func.variables) == 1:
                varstr = printer._print(func.variables[0])
            else:
                varstr = printer._print(func.variables)
            elemstr = printer._print(func.expr)
            setstr = printer._print(self.set)
            return '{{{0} | {1} in {2}}}'.format(elemstr, varstr, setstr)

FunctionObject.image = lambda self, zet: Image(self, zet)

class Contains(Application, Boolean):
    @classmethod
    def eval(cls, x, zet):
        if not isinstance(x, Basic):
            raise TypeError
        if not isinstance(zet, Set):
            raise TypeError

        ret = zet.contains(x)
        if not isinstance(ret, Contains):
            return ret

def simplify_boolean(expr, form='dnf', op=(Union, Intersection, AbsoluteComplement, Complement)):
    """
    >>> from sympy import *
    >>> from symplus.strplus import init_mprinting
    >>> init_mprinting()
    >>> A = Set(symbols("A"))
    >>> B = Set(symbols("B"))
    >>> C = Set(symbols("C"))
    >>> simplify_boolean(B & (A | C))
    Set(A) n Set(B) u Set(B) n Set(C)
    >>> simplify_boolean((A & B) | (A - B) | (B & C) | (C - B))
    Set(A) u Set(C)
    >>> simplify_boolean(AbsoluteComplement(A+B+C) | (C-A-B))
    -(Set(A)) n -(Set(B))
    """
    exprs = {}

    def expr2bool(expr):
        if isinstance(expr, op[0]):
            return Or(*map(expr2bool, expr.args))
        elif isinstance(expr, op[1]):
            return And(*map(expr2bool, expr.args))
        elif isinstance(expr, op[2]):
            return Not(expr2bool(expr.args[0]))
        elif len(op) >= 4 and isinstance(expr, op[3]):
            return And(expr2bool(expr.args[0]), Not(expr2bool(expr.args[1])))
        else:
            for b, e in exprs.items():
                if e == expr:
                    return b
            else:
                b = Dummy("b")
                exprs[b] = expr
                return b

    def bool2expr(b):
        if isinstance(b, Or):
            return op[0](*map(bool2expr, b.args), evaluate=False)
        elif isinstance(b, And):
            return op[1](*map(bool2expr, b.args), evaluate=False)
        elif isinstance(b, Not):
            return op[2](bool2expr(b.args[0]), evaluate=False)
        else:
            return exprs[b]

    return bool2expr(simplify_logic(expr2bool(expr), form='dnf', deep=False))


def is_open(zet):
    """
    >>> from sympy import *
    >>> from symplus.strplus import init_mprinting
    >>> init_mprinting()
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
    """
    if isinstance(zet, Interval):
        return (zet.left_open | (zet.start==-oo)) & (zet.right_open | (zet.end==oo))

    elif isinstance(zet, ProductSet):
        return And(*map(is_open, zet.args))

    elif isinstance(zet, (Intersection, Union)):

        if And(*map(is_open, zet.args)) == true:
            return true

    elif isinstance(zet, Complement):
        if (is_open(zet.args[0]) & is_closed(zet.args[1])) == true:
            return true

    elif isinstance(zet, AbsoluteComplement):
        return is_closed(zet.args[0])

    res = zet.is_open
    if res in (true, false):
        return res
    raise NotImplementedError

def is_closed(zet):
    """
    >>> from sympy import *
    >>> from symplus.strplus import init_mprinting
    >>> init_mprinting()
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
    """
    if isinstance(zet, Interval):
        return ((~zet.left_open) | (zet.start==-oo)) & ((~zet.right_open) | (zet.end==oo))

    elif isinstance(zet, ProductSet):
        return And(*map(is_closed, zet.args))

    elif isinstance(zet, (Intersection, Union)):
        if And(*map(is_closed, zet.args)) == true:
            return true

    elif isinstance(zet, Complement):
        if (is_closed(zet.args[0]) & is_open(zet.args[1])) == true:
            return true

    elif isinstance(zet, AbsoluteComplement):
        return is_open(zet.args[0])

    res = zet.is_closed
    if res in (true, false):
        return res
    raise NotImplementedError

class Interior(Set):
    def __new__(cls, set, **kwargs):
        evaluate = kwargs.pop('evaluate', global_evaluate[0])
        if evaluate:
            res = Interior.eval(set)
            if res is not None:
                return res
        return Set.__new__(cls, set, **kwargs)

    @staticmethod
    def eval(zet):
        """
        >>> from sympy import *
        >>> from symplus.strplus import init_mprinting
        >>> init_mprinting()
        >>> Interior(Interval(0,1, False, False))
        (0, 1)
        >>> Interior(Interval(1,2, True, False))
        (1, 2)
        >>> Interior(Interval(1,oo, False, False))
        (1, oo)
        >>> Interior(Interval(1,2, False, False) * Interval(0,1, False, False))
        (1, 2) x (0, 1)
        """
        if isinstance(zet, Interior):
            return zet

        elif isinstance(zet, Interval):
            return Interval(zet.start, zet.end, left_open=True, right_open=True)

        elif isinstance(zet, ProductSet):
            return zet.func(*[Interior(arg, evaluate=True) for arg in zet.args])

        elif isinstance(zet, Intersection):
            return zet.func(*[Interior(arg, evaluate=True) for arg in zet.args])

        try:
            res = zet.interior
            if res is not None:
                return res
        except NotImplementedError:
            pass

        try:
            if is_open(zet):
                return zet
        except NotImplementedError:
            pass

        return None

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
        return Closure(AbsoluteComplement(self.set, evaluate=True), evaluate=True)

    def _image(self, func):
        if getattr(func, "is_bicontinuous", False):
            return self.func(Image(func, self.set, evaluate=True))

    def _mathstr(self, printer):
        return 'int({0})'.format(printer._print(self.args[0]))

class Closure(Set):
    def __new__(cls, set, **kwargs):
        evaluate = kwargs.pop('evaluate', global_evaluate[0])
        if evaluate:
            res = Closure.eval(set)
            if res is not None:
                return res
        return Set.__new__(cls, set, **kwargs)

    @staticmethod
    def eval(zet):
        """
        >>> from sympy import *
        >>> from symplus.strplus import init_mprinting
        >>> init_mprinting()
        >>> Closure(Interval(0,1, False, False))
        [0, 1]
        >>> Closure(Interval(1,2, True, False))
        [1, 2]
        >>> Closure(Interval(1,oo, False, False))
        [1, oo)
        >>> Closure(Interval(1,2, False, False) * Interval(0,1, False, False))
        [1, 2] x [0, 1]
        """
        if isinstance(zet, Closure):
            return zet

        elif isinstance(zet, Interval):
            return Interval(zet.start, zet.end, left_open=False, right_open=False)

        elif isinstance(zet, ProductSet):
            return zet.func(*[Closure(arg, evaluate=True) for arg in zet.args])

        elif isinstance(zet, Union):
            return zet.func(*[Closure(arg, evaluate=True) for arg in zet.args])

        try:
            res = zet.closure
            if res is not None:
                return res
        except NotImplementedError:
            pass

        try:
            if is_closed(zet):
                return zet
        except NotImplementedError:
            pass

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
        return Interior(AbsoluteComplement(self.set, evaluate=True), evaluate=True)

    def _image(self, func):
        if getattr(func, "is_bicontinuous", False):
            return self.func(Image(func, self.set, evaluate=True))

    def _mathstr(self, printer):
        return 'cl({0})'.format(printer._print(self.args[0]))

class Exterior(Set):
    def __new__(cls, set, **kwargs):
        evaluate = kwargs.pop('evaluate', global_evaluate[0])
        if evaluate:
            res = Exterior.eval(set)
            if res is not None:
                return res
        return Set.__new__(cls, set, **kwargs)

    @staticmethod
    def eval(zet):
        return Interior(AbsoluteComplement(zet, evaluate=True), evaluate=True)

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
        return Closure(self.set, evaluate=True)

    def _image(self, func):
        if getattr(func, "is_bicontinuous", False):
            return self.func(Image(func, self.set, evaluate=True))

    def _mathstr(self, printer):
        return 'ext({0})'.format(printer._print(self.args[0]))


def regularize(set, evaluate=False, closed=True):
    if closed:
        Regularization = ClosedRegularization
        RegularizedIntersection = ClosedRegularizedIntersection
        RegularizedUnion = ClosedRegularizedUnion
        RegularizedAbsoluteComplement = ClosedRegularizedAbsoluteComplement
    else:
        Regularization = OpenRegularization
        RegularizedIntersection = OpenRegularizedIntersection
        RegularizedUnion = OpenRegularizedUnion
        RegularizedAbsoluteComplement = OpenRegularizedAbsoluteComplement
    reg_table = {
        Intersection: RegularizedIntersection,
        RegularizedIntersection: RegularizedIntersection,
        Union: RegularizedUnion,
        RegularizedUnion: RegularizedUnion,
        AbsoluteComplement: RegularizedAbsoluteComplement,
        RegularizedAbsoluteComplement: RegularizedAbsoluteComplement}

    if isinstance(set, tuple(reg_table.keys())):
        func_ = reg_table[type(set)]
        args_ = [regularize(arg, evaluate=evaluate) for arg in set.args]
        return func_(*args_, evaluate=evaluate)

    elif isinstance(set, Complement):
        set_ = Intersection(
            set.args[0],
            AbsoluteComplement(set.args[1], evaluate=False),
            evaluate=False)
        return regularize(set_, evaluate=evaluate)

    elif isinstance(set, Regularization):
        return regularize(set.args[0], evaluate=evaluate)

    else:
        return Regularization(set, evaluate=evaluate)

class ClosedRegularization(Set):
    def __new__(cls, set, **kwargs):
        evaluate = kwargs.pop('evaluate', global_evaluate[0])

        if evaluate:
            res = ClosedRegularization.eval(set)
            if res is not None:
                return res
        return Set.__new__(cls, set, **kwargs)

    @staticmethod
    def eval(zet):
        zet_ = Interior.eval(zet)
        if zet_ is not None:
            return Closure.eval(zet_)

    def as_primary(self):
        return Closure(Interior(self.set))

    @property
    def set(self):
        return self.args[0]

    @property
    def is_open(self):
        return false

    @property
    def is_closed(self):
        return true

    def _image(self, func):
        if getattr(func, "is_bicontinuous", False):
            return self.func(Image(func, self.set, evaluate=True))

class ClosedRegularizedAbsoluteComplement(Set):
    def __new__(cls, set, **kwargs):
        evaluate = kwargs.pop('evaluate', global_evaluate[0])
        if evaluate:
            res = ClosedRegularizedAbsoluteComplement.eval(set)
            if res is not None:
                return res
        return Set.__new__(cls, set, **kwargs)

    @staticmethod
    def eval(zet):
        zet_ = AbsoluteComplement.eval(zet)
        if zet_ is not None:
            return ClosedRegularization.eval(zet_)

    def as_primary(self):
        return ClosedRegularization(AbsoluteComplement(self.set)).as_primary()

    @property
    def set(self):
        return self.args[0]

    @property
    def is_open(self):
        return false

    @property
    def is_closed(self):
        return true

    def _image(self, func):
        if getattr(func, "is_bicontinuous", False):
            return self.func(Image(func, self.set, evaluate=True))

    def _mathstr(self, printer):
        if isinstance(self.args[0], (Atom,
                                     ClosedRegularizedAbsoluteComplement)):
            return '-*'+printer.doprint(self.args[0])
        else:
            return '-*(%s)'%printer.doprint(self.args[0])

class ClosedRegularizedIntersection(Set):
    def __new__(cls, *args, **kwargs):
        evaluate = kwargs.pop('evaluate', global_evaluate[0])

        if evaluate:
            args = ClosedRegularizedIntersection.reduce(args)
        return Set.__new__(cls, *args, **kwargs)

    @classmethod
    def reduce(cls, args):
        def flatten(arg):
            if isinstance(arg, cls):
                return sum(map(flatten, arg.args), [])
            elif isinstance(arg, Set):
                return [arg]
            elif isinstance(arg, (tuple, list)):
                return sum(map(flatten, arg), [])
            else:
                raise TypeError("Input must be Sets or iterables of Sets")
        return list(set(flatten(args)))

    def as_primary(self):
        return ClosedRegularization(Intersection(*self.args))

    @property
    def is_open(self):
        return false

    @property
    def is_closed(self):
        return true

    def _image(self, func):
        if getattr(func, "is_bicontinuous", False):
            return self.func(*[Image(func, arg, evaluate=True)
                               for arg in self.args])

    def _mathstr(self, printer):
        argstr = []
        for a in self.args:
            if isinstance(a, (Atom,
                              ClosedRegularizedAbsoluteComplement,
                              ClosedRegularizedIntersection)):
                argstr.append(printer.doprint(a))
            else:
                argstr.append('(%s)'%printer.doprint(a))
        return ' n* '.join(sorted(argstr))

class ClosedRegularizedUnion(Set):
    def __new__(cls, *args, **kwargs):
        evaluate = kwargs.pop('evaluate', global_evaluate[0])

        if evaluate:
            args = ClosedRegularizedUnion.reduce(args)
        return Set.__new__(cls, *args, **kwargs)

    @classmethod
    def reduce(cls, args):
        def flatten(arg):
            if isinstance(arg, cls):
                return sum(map(flatten, arg.args), [])
            elif isinstance(arg, Set):
                return [arg]
            elif isinstance(arg, (tuple, list)):
                return sum(map(flatten, arg), [])
            else:
                raise TypeError("Input must be Sets or iterables of Sets")
        return list(set(flatten(args)))

    def as_primary(self):
        return ClosedRegularization(Union(*self.args))

    @property
    def is_open(self):
        return false

    @property
    def is_closed(self):
        return true

    def _image(self, func):
        if getattr(func, "is_bicontinuous", False):
            return self.func(*[Image(func, arg, evaluate=True)
                               for arg in self.args])

    def _mathstr(self, printer):
        argstr = []
        for a in self.args:
            if isinstance(a, (Atom,
                              ClosedRegularizedAbsoluteComplement,
                              ClosedRegularizedIntersection,
                              ClosedRegularizedUnion)):
                argstr.append(printer.doprint(a))
            else:
                argstr.append('(%s)'%printer.doprint(a))
        return ' u* '.join(sorted(argstr))

class OpenRegularization(Set):
    def __new__(cls, set, **kwargs):
        evaluate = kwargs.pop('evaluate', global_evaluate[0])

        if evaluate:
            res = OpenRegularization.eval(set)
            if res is not None:
                return res
        return Set.__new__(cls, set, **kwargs)

    @staticmethod
    def eval(zet):
        zet_ = Closure.eval(zet)
        if zet_ is not None:
            return Interior.eval(zet_)

    def as_primary(self):
        return Interior(Closure(self.set))

    @property
    def set(self):
        return self.args[0]

    @property
    def is_open(self):
        return true

    @property
    def is_closed(self):
        return false

    def _image(self, func):
        if getattr(func, "is_bicontinuous", False):
            return self.func(Image(func, self.set, evaluate=True))

class OpenRegularizedAbsoluteComplement(Set):
    def __new__(cls, set, **kwargs):
        evaluate = kwargs.pop('evaluate', global_evaluate[0])
        if evaluate:
            res = OpenRegularizedAbsoluteComplement.eval(set)
            if res is not None:
                return res
        return Set.__new__(cls, set, **kwargs)

    @staticmethod
    def eval(zet):
        zet_ = AbsoluteComplement.eval(zet)
        if zet_ is not None:
            return OpenRegularization.eval(zet_)

    def as_primary(self):
        return OpenRegularization(AbsoluteComplement(self.set)).as_primary()

    @property
    def set(self):
        return self.args[0]

    @property
    def is_open(self):
        return true

    @property
    def is_closed(self):
        return false

    def _image(self, func):
        if getattr(func, "is_bicontinuous", False):
            return self.func(Image(func, self.set, evaluate=True))

    def _mathstr(self, printer):
        if isinstance(self.args[0], (Atom,
                                     OpenRegularizedAbsoluteComplement)):
            return '-*'+printer.doprint(self.args[0])
        else:
            return '-*(%s)'%printer.doprint(self.args[0])

class OpenRegularizedIntersection(Set):
    def __new__(cls, *args, **kwargs):
        evaluate = kwargs.pop('evaluate', global_evaluate[0])

        if evaluate:
            args = OpenRegularizedIntersection.reduce(args)
        return Set.__new__(cls, *args, **kwargs)

    @classmethod
    def reduce(cls, args):
        def flatten(arg):
            if isinstance(arg, cls):
                return sum(map(flatten, arg.args), [])
            elif isinstance(arg, Set):
                return [arg]
            elif isinstance(arg, (tuple, list)):
                return sum(map(flatten, arg), [])
            else:
                raise TypeError("Input must be Sets or iterables of Sets")
        return list(set(flatten(args)))

    def as_primary(self):
        return OpenRegularization(Intersection(*self.args))

    @property
    def is_open(self):
        return true

    @property
    def is_closed(self):
        return false

    def _image(self, func):
        if getattr(func, "is_bicontinuous", False):
            return self.func(*[Image(func, arg, evaluate=True)
                               for arg in self.args])

    def _mathstr(self, printer):
        argstr = []
        for a in self.args:
            if isinstance(a, (Atom,
                              OpenRegularizedAbsoluteComplement,
                              OpenRegularizedIntersection)):
                argstr.append(printer.doprint(a))
            else:
                argstr.append('(%s)'%printer.doprint(a))
        return ' n* '.join(sorted(argstr))

class OpenRegularizedUnion(Set):
    def __new__(cls, *args, **kwargs):
        evaluate = kwargs.pop('evaluate', global_evaluate[0])

        if evaluate:
            args = OpenRegularizedUnion.reduce(args)
        return Set.__new__(cls, *args, **kwargs)

    @classmethod
    def reduce(cls, args):
        def flatten(arg):
            if isinstance(arg, cls):
                return sum(map(flatten, arg.args), [])
            elif isinstance(arg, Set):
                return [arg]
            elif isinstance(arg, (tuple, list)):
                return sum(map(flatten, arg), [])
            else:
                raise TypeError("Input must be Sets or iterables of Sets")
        return list(set(flatten(args)))

    def as_primary(self):
        return OpenRegularization(Union(*self.args))

    @property
    def is_open(self):
        return true

    @property
    def is_closed(self):
        return false

    def _image(self, func):
        if getattr(func, "is_bicontinuous", False):
            return self.func(*[Image(func, arg, evaluate=True)
                               for arg in self.args])

    def _mathstr(self, printer):
        argstr = []
        for a in self.args:
            if isinstance(a, (Atom,
                              OpenRegularizedAbsoluteComplement,
                              OpenRegularizedIntersection,
                              OpenRegularizedUnion)):
                argstr.append(printer.doprint(a))
            else:
                argstr.append('(%s)'%printer.doprint(a))
        return ' u* '.join(sorted(argstr))


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

    def is_regular_closed_set(self, zet):
        return Eq(zet, self.closure_of(self.interior_of(zet)))

class DiscreteTopology(Topology):
    """
    >>> from sympy import *
    >>> from symplus.strplus import init_mprinting
    >>> init_mprinting()
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
    >>> from symplus.strplus import init_mprinting
    >>> init_mprinting()
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

    def complement_of(self, zet):
        return AbsoluteComplement(zet)

    def exterior_of(self, zet):
        return Exterior(zet)

    def is_open_set(self, zet):
        return is_open(zet)

    def is_closed_set(self, zet):
        return is_closed(zet)


Reals = AbstractSet(symbols('x', real=True), true)

