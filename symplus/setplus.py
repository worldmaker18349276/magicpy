import operator
from functools import reduce
from sympy.core import S, Basic, Symbol, sympify, Ne, Eq, Gt, Ge, Lt, Le, oo, symbols, Dummy
from sympy.core.function import Application
from sympy.core.evaluate import global_evaluate
from sympy.logic import true, false, And, Or, Not, Nand, Implies, Equivalent, to_dnf
from sympy.logic.boolalg import Boolean, simplify_logic
from sympy.functions import Id
from sympy.sets import Set, Interval, FiniteSet, Intersection, Union, Complement, ProductSet
from symplus.typlus import is_Symbol, is_Function, is_Boolean, type_match
from symplus.tuplus import pack_if_not, unpack_if_can, repack_if_can
from symplus.symbplus import free_symbols, rename_variables_in
from symplus.funcplus import FunctionCompose, FunctionInverse, as_lambda, nres
from symplus.logicplus import Forall


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
        AbstractSet(m, Eq(m[0, 0] + m[1, 1], 0))
        >>> AbstractSet((m, x), Eq(det(m),x))
        AbstractSet((m, x), Eq(Determinant(m), x))
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
        return pack_if_not(self._args[0])

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
        return free_symbols(self.expr) - set(self.variables)

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
        AbstractSet(m, And(Eq(Determinant(m), 0), Eq(m[0, 0] + m[1, 1], 0)))
        >>> AbstractSet(m, Eq(m[0,0]+m[1,1],0))._intersect(AbstractSet(x, abs(x)>1))
        EmptySet()
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
        AbstractSet(m, Or(Eq(Determinant(m), 0), Eq(m[0, 0] + m[1, 1], 0)))
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
        >>> x, y = symbols('x y')
        >>> AbstractSet(y, abs(y)<=3)._complement(AbstractSet(x, abs(x)>1))
        AbstractSet(y, And(Abs(y) > 1, Abs(y) > 3))
        >>> AbstractSet((x,y), abs(x-y)>1)._complement(AbstractSet(x, abs(x)>1))
        AbstractSet(x, Abs(x) > 1)
        >>> AbstractSet(y, y<=x)._complement(AbstractSet(x, abs(x)>1))
        AbstractSet(y, And(Abs(y) > 1, y > x))
        >>> x2 = symbols('x2', positive=True)
        >>> AbstractSet(x, abs(x)>1)._complement(AbstractSet(x2, x2<=y))
        AbstractSet(x, And(Abs(x) <= 1, x <= y))
        >>> m, n = MatrixSymbol('m', 2, 2), MatrixSymbol('n', 2, 2)
        >>> AbstractSet(n, Eq(det(n),0))._complement(AbstractSet(m, Eq(m[0,0]+m[1,1],0)))
        AbstractSet(n, And(Eq(n[0, 0] + n[1, 1], 0), Ne(Determinant(n), 0)))
        >>> AbstractSet(x, abs(x)>1)._complement(AbstractSet(m, Eq(m[0,0]+m[1,1],0)))
        AbstractSet(m, Eq(m[0, 0] + m[1, 1], 0))
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
            vars2_ = rename_variables_in(vars2, free_symbols(self)|set(vars1))
            expr2_ = expr2.xreplace(dict(zip(vars2, vars2_)))
            return AbstractSet(tuple(vars1)+tuple(vars2_), And(expr1, expr2_))
        else:
            return None

    def _eval_Eq(self, other):
        return self.is_equivalent(other)


class SetBuilder:
    def __getitem__(self, zets):
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
        Intersection((-oo, oo), AbstractSet(x, x < 1))
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
        >>> x, y = symbols('x y')
        >>> St({x : abs(x)>1})
        AbstractSet(x, Abs(x) > 1)
        >>> St({(x, y) : abs(x-y)>1})
        AbstractSet((x, y), Abs(x - y) > 1)
        >>> St({x : x-y>1}, {x : x<1})
        AbstractSet(x, And(x - y > 1, x < 1))
        >>> St(S.Reals, {x : x<1})
        Intersection((-oo, oo), AbstractSet(x, x < 1))
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

    elif isinstance(zet, (Intersection, Union, Complement)):
        return zet.func(*[as_abstract(e) for e in zet.args])

    else:
        x = Symbol('x', real=True)
        x, = rename_variables_in((x,), free_symbols(zet))
        expr = zet.contains(x)
        return AbstractSet(x, expr)


class Image(Set):
    """
    >>> from sympy import *
    >>> from symplus.funcplus import *
    >>> Image(sin, Interval(0, pi/2))
    Image(sin, [0, pi/2])
    >>> Image(exp, Image(sin, Interval(0, pi/2)))
    Image(FunctionCompose(exp, sin), [0, pi/2])
    >>> Image(FunctionInverse(sin), Image(sin, Interval(0, pi/2)))
    [0, pi/2]
    >>> Image(cos, S.EmptySet)
    EmptySet()
    >>> x, y = symbols('x y')
    >>> Image(cos, AbstractSet(x, x > 0))
    AbstractSet(a0, acos(a0) > 0)
    >>> Image(cos, Intersection(AbstractSet(x, x > 0), AbstractSet(x, x < 0), evaluate=False))
    Intersection(AbstractSet(a0, acos(a0) > 0), AbstractSet(a0, acos(a0) < 0))
    >>> Image(Lambda(x, x+1), Interval(-1, 1)).contains(1)
    True
    >>> Image(Lambda(x, sin(x)+x), Interval(-1, 1)).contains(1)
    And(Apply(FunctionInverse(Lambda(x, x + sin(x))), 1) <= 1, Apply(FunctionInverse(Lambda(x, x + sin(x))), 1) >= -1)
    >>> f = Lambda((x, y), (x*cos(y), x*sin(y)))
    >>> f_inv = FunctionInverse(f, evaluate=False)
    >>> f_inv(*f(1, pi/4))
    (-1, -3*pi/4)
    >>> Image(f, ProductSet(Interval(0,1), Interval(-pi,pi))).contains(f(1, pi/4))
    True
    >>> Image(Lambda(x, x+1), Interval(-1, 1)).as_abstract()
    AbstractSet(x0, And(x0 - 1 <= 1, x0 - 1 >= -1))
    >>> g = Lambda((x, y), (x+exp(y), x+sin(y)))
    >>> Image(g, ProductSet(Interval(-1,1), Interval(-1,1))).contains(g(1,2))
    False
    >>> Image(g, AbstractSet((x,y), x<y)).contains(g(1,2))
    False
    """
    def __new__(cls, function, zet, **kwargs):
        evaluate = kwargs.pop('evaluate', global_evaluate[0])

        if not is_Function(function):
            raise TypeError('function is not a FunctionClass, Functor or Lambda: %s'%function)
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

            if isinstance(zet, (Intersection, Union, Complement)):
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

            elif hasattr(func, '_image'):
                res = func._image(zet)
                if res is not None:
                    if isinstance(res, Image):
                        return res.function, res.set
                    else:
                        return Id, res
                else:
                    return func, zet

            elif isinstance(zet, AbstractSet):
                inv_func = FunctionInverse(func, evaluate=True)
                if not isinstance(inv_func, FunctionInverse):
                    lambda_inv_func = as_lambda(inv_func)
                    return Id, AbstractSet(lambda_inv_func.variables, zet.contains(lambda_inv_func.expr))
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
        mem = pack_if_not(mem)
        inv_func = FunctionInverse(self.function)
        mem_ = unpack_if_can(inv_func(*mem))
        return self.set._contains(mem_)

    def as_abstract(self):
        narg = nres(self.function)
        x = symbols('x:%d'%narg, real=True)
        expr = self.contains(x)
        return AbstractSet(x, expr)

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

def simplify_set(zet, form='dnf', deep=True):
    """
    >>> from sympy import *
    >>> A = Set("A")
    >>> B = Set("B")
    >>> C = Set("C")
    >>> simplify_set(B & (A | C), deep=False)
    Intersection(Set(A), Set(B)) U Intersection(Set(B), Set(C))
    >>> simplify_set((A & B) | (A - B) | (B & C) | (C - B), deep=False)
    Set(A) U Set(C)
    >>> simplify_set(AbsoluteComplement(A+B+C) | (C-A-B), deep=False)
    Intersection(AbsoluteComplement(Set(A)), AbsoluteComplement(Set(B)))
    """
    x = Dummy()
    def containx(zet):
        if isinstance(zet, Union):
            return Or(*map(containx, zet.args))
        elif isinstance(zet, Intersection):
            return And(*map(containx, zet.args))
        elif isinstance(zet, Complement):
            return And(containx(zet.args[0]), Not(containx(zet.args[1])))
        elif isinstance(zet, AbsoluteComplement):
            return Not(containx(zet.args[0]))
        else:
            return Contains(x, zet, evaluate=False)

    def collectx(expr):
        if isinstance(expr, Or):
            return Union(*map(collectx, expr.args), evaluate=False)
        elif isinstance(expr, And):
            return Intersection(*map(collectx, expr.args), evaluate=False)
        elif isinstance(expr, Not):
            return AbsoluteComplement(collectx(expr.args[0]), evaluate=False)
        elif isinstance(expr, Contains) and expr.args[0] == x:
            return expr.args[1]
        else:
            return AbstractSet(x, expr)

    return collectx(simplify_logic(containx(zet), form='dnf', deep=deep))


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
        >>> from symplus.setplus import *
        >>> AbsoluteComplement(Interval(0,1, False, False))
        (-oo, 0) U (1, oo)
        >>> AbsoluteComplement(Interval(1,2, True, False))
        (-oo, 1] U (2, oo)
        >>> AbsoluteComplement(Interval(1,oo, False, False))
        (-oo, 1)
        >>> AbsoluteComplement(Interval(1,2, False, False) * Interval(0,1, False, False))
        AbsoluteComplement([1, 2] x [0, 1])
        >>> x,y = symbols('x y')
        >>> AbsoluteComplement(AbstractSet(x, x**2<1))
        AbstractSet(x, x**2 >= 1)
        >>> AbsoluteComplement(AbstractSet(x, (x<4)|(x>=6)))
        AbstractSet(x, Not(Or(x < 4, x >= 6)))
        >>> AbsoluteComplement(AbstractSet((x,y), x<=y))
        AbstractSet((x, y), x > y)
        """
        if isinstance(zet, Interval):
            return zet.complement(S.Reals)

        elif isinstance(zet, Union):
            return Intersection(*[AbsoluteComplement(arg, evaluate=True)
                                  for arg in zet.args])

        elif isinstance(zet, Intersection):
            return Union(*[AbsoluteComplement(arg, evaluate=True)
                           for arg in zet.args])

        else:
            if hasattr(zet, "_absolute_complement"):
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
                return Interior(zet.expand(), evaluate=True)
            elif isinstance(zet.expr, Ne):
                return zet
            elif isinstance(zet.expr, Eq):
                return AbstractSet(zet.variables, false)
            elif isinstance(zet.expr, (Gt, Ge)):
                return AbstractSet(zet.variables, Gt(*zet.expr.args))
            elif isinstance(zet.expr, (Lt, Le)):
                return AbstractSet(zet.variables, Lt(*zet.expr.args))

        elif isinstance(zet, Intersection):
            return zet.func(*[Interior(arg, evaluate=True) for arg in zet.args])

        elif isinstance(zet, Complement):
            return zet.func(Interior(zet.args[0], evaluate=True),
                            Closure(zet.args[1], evaluate=True))

        elif isinstance(zet, ProductSet):
            return zet.func(*[Interior(arg, evaluate=True) for arg in zet.args])

        try:
            res = zet.interior
            if res is not None:
                return res
            else:
                return zet - zet.boundary
        except NotImplementedError:
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
        return Closure(AbsoluteComplement(self.set))

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
                return Closure(zet.expand(), evaluate=True)
            elif isinstance(zet.expr, Eq):
                return zet
            elif isinstance(zet.expr, Ne):
                return AbstractSet(zet.variables, true)
            elif isinstance(zet.expr, (Ge, Gt)):
                return AbstractSet(zet.variables, Ge(*zet.expr.args))
            elif isinstance(zet.expr, (Le, Lt)):
                return AbstractSet(zet.variables, Le(*zet.expr.args))

        elif isinstance(zet, Union):
            return zet.func(*[Closure(arg, evaluate=True) for arg in zet.args])

        elif isinstance(zet, ProductSet):
            return zet.func(*[Closure(arg, evaluate=True) for arg in zet.args])

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
        return Closure(self.set)

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

