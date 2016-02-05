from functools import reduce
from sympy.core import (S, FunctionClass, Function, Expr, Basic,
                        Lambda, Tuple, symbols, cacheit, sympify)
from sympy.core.evaluate import global_evaluate
from sympy.solvers import solve
from sympy.functions import (Id, exp, log, cos, acos, sin, asin, tan, atan,
                             cot, acot, sec, asec, csc, acsc)
from sympy.sets import Set, Intersection, Union, Complement
from symplus.util import *
from symplus.setplus import AbstractSet


def func_free_symbols(func):
    if isinstance(func, (Lambda, Functor)):
        return func.free_symbols
    elif isinstance(func, FunctionClass):
        return set()
    else:
        raise TypeError

inv_table = {
    exp: log,
    cos: acos,
    sin: asin,
    tan: atan,
    cot: acot,
    sec: asec,
    csc: acsc,
    log: exp,
    acos: cos,
    asin: sin,
    atan: tan,
    acot: cot,
    asec: sec,
    acsc: csc,
}

def is_inverse_of(func1, func2):
    if isinstance(func1, FunctionInverse) and func1.function == func2:
        return True
    elif isinstance(func2, FunctionInverse) and func2.function == func1:
        return True
    elif func1 in inv_table and inv_table[func1] == func2:
        return True
    else:
        return False


class FunctionCompose(Functor):
    """
    >>> from sympy import *
    >>> FunctionCompose(exp, sin)
    FunctionCompose(exp, sin)
    >>> x, y = symbols('x y')
    >>> FunctionCompose(exp, Lambda(x, x+1))
    FunctionCompose(exp, Lambda(x, x + 1))
    >>> FunctionCompose(Lambda(x, x/2), Lambda(x, x+1))
    Lambda(x, x/2 + 1/2)
    >>> FunctionCompose(exp, Id)
    exp
    >>> FunctionCompose(exp, FunctionInverse(exp))
    Lambda(_x, _x)
    >>> FunctionCompose(exp, FunctionCompose(sin, log))
    FunctionCompose(exp, sin, log)
    >>> FunctionCompose(exp, sin)(pi/3)
    exp(sqrt(3)/2)
    >>> FunctionCompose(Lambda((x,y), x+y), Lambda(x, (x, x-2)))(3)
    4
    """
    def __new__(cls, *functions, **kwargs):
        evaluate = kwargs.pop('evaluate', global_evaluate[0])

        for function in functions:
            if not is_Function(function):
                raise TypeError('function is not a FunctionClass, Functor or Lambda: %s'%function)

        if evaluate:
            functions = FunctionCompose.reduce(functions)

        if len(functions) == 0:
            return Id
        elif len(functions) == 1:
            return functions[0]
        else:
            return Functor.__new__(cls, *functions)

    @staticmethod
    def reduce(funcs):
        i = 0
        while i < len(funcs):
            if funcs[i] == Id:
                funcs = funcs[:i] + funcs[i+1:]
            elif isinstance(funcs[i], FunctionCompose):
                funcs = funcs[:i] + funcs[i].functions + funcs[i+1:]
            elif i-1 >= 0:
                if is_inverse_of(funcs[i-1], funcs[i]):
                    funcs = funcs[:i-1] + funcs[i+1:]
                    i = i - 2
                elif hasattr(funcs[i-1], '_compose'):
                    comp_funcs = funcs[i-1]._compose(funcs[i])
                    if comp_funcs is not None:
                        funcs = funcs[:i-1] + (comp_funcs,) + funcs[i+1:]
                        i = i - 1
                elif isinstance(funcs[i-1], Lambda) and isinstance(funcs[i], Lambda):
                    comp_funcs = Lambda(funcs[i].variables, funcs[i-1](*pack_if_not(funcs[i].expr)))
                    funcs = funcs[:i-1] + (comp_funcs,) + funcs[i+1:]
                    i = i - 1
            i = i + 1
        return funcs

    @property
    def functions(self):
        return self.args

    @property
    def narg(self):
        return narg(self.functions[-1])

    @property
    def nres(self):
        return nres(self.functions[0])

    def call(self, *args):
        apply_multivar = lambda a, f: f(*pack_if_not(a))
        return reduce(apply_multivar, self.functions[::-1], args)

    @property
    def free_symbols(self):
        return {sym for func in self.functions for sym in func_free_symbols(func)}

class FunctionInverse(Functor):
    """
    >>> from sympy import *
    >>> x = symbols('x')
    >>> FunctionInverse(Lambda(x, x+1))
    FunctionInverse(Lambda(x, x + 1))
    >>> FunctionInverse(sin)
    asin
    >>> FunctionInverse(FunctionCompose(exp, Lambda(x, x+1)))
    FunctionCompose(FunctionInverse(Lambda(x, x + 1)), log)
    >>> FunctionInverse(FunctionInverse(Lambda(x, x+1)))
    Lambda(x, x + 1)
    >>> FunctionCompose(FunctionInverse(Lambda(x, x+1)), Lambda(x, x+1))
    Lambda(_x, _x)
    >>> FunctionInverse(Lambda(x, x+sin(x)))(3)
    Apply(FunctionInverse(Lambda(x, x + sin(x))), 3)
    """
    def __new__(cls, function, **kwargs):
        evaluate = kwargs.pop('evaluate', global_evaluate[0])

        if not is_Function(function):
            raise TypeError('function is not a FunctionClass, Functor or Lambda: %s'%function)

        if evaluate:
            eval_func = FunctionInverse.eval(function)
            if eval_func is not None:
                return eval_func

        return Functor.__new__(cls, function)

    @staticmethod
    def eval(func):
        if func == Id:
            return Id
        elif isinstance(func, FunctionInverse):
            return func.function
        elif isinstance(func, FunctionCompose):
            return FunctionCompose(
                *[FunctionInverse(f, evaluate=True)
                  for f in func.functions[::-1]],
                evaluate=False)

        if hasattr(func, '_inv'):
            inv_func = func._inv()
            if inv_func is not None:
                return inv_func

        if func in inv_table:
            return inv_table[func]

        return None

    @property
    def function(self):
        return self.args[0]

    @property
    def narg(self):
        return nres(self.function)

    @property
    def nres(self):
        return narg(self.function)

    def call(self, *args):
        vars = symbols('a:%s'%narg(self.function))
        vars = rename_variables_in(vars, func_free_symbols(self.function))
        exprs = pack_if_not(self.function(*vars))

        if len(args) != len(exprs):
            raise ValueError

        try:
            solns = solve([expr - val for val, expr in zip(args, exprs)], vars)
            if isinstance(solns, list):
                solns = dict(zip(vars, solns[0]))

            if len(vars) == 1:
                return solns[vars[0]]
            else:
                return tuple(solns[var] for var in vars)

        except NotImplementedError:
            return Apply(self, args)

    @property
    def free_symbols(self):
        return func_free_symbols(self.function)

class Apply(Function):
    """
    >>> from sympy import *
    >>> Apply(sin, pi)
    Apply(sin, pi)
    >>> Apply(exp, Apply(sin, pi))
    Apply(FunctionCompose(exp, sin), pi)
    >>> Apply(FunctionInverse(sin), Apply(sin, pi))
    pi
    >>> Apply(sin, pi).doit()
    0
    >>> x, y = symbols('x y')
    >>> Apply(Lambda((x,y), x+y), (1,2))
    Apply(Lambda((x, y), x + y), (1, 2))
    >>> _.doit()
    3
    """
    def __new__(cls, function, argument, **kwargs):
        evaluate = kwargs.pop('evaluate', global_evaluate[0])
        argument = repack_if_can(sympify(unpack_if_can(argument)))

        if not is_Function(function):
            raise TypeError('function is not a FunctionClass, Functor or Lambda: %s'%function)

        if evaluate:
            function, argument = Apply.reduce(function, argument)

        if function == Id:
            return argument
        else:
            return Expr.__new__(cls, function, argument, **kwargs)

    @classmethod
    def reduce(cls, func, arg):
        if isinstance(arg, Apply):
            return cls.reduce(FunctionCompose(func, arg.function), arg.argument)
        else:
            return func, arg

    @property
    def function(self):
        return self._args[0]

    @property
    def argument(self):
        return self._args[1]

    @property
    def arguments(self):
        return pack_if_not(self._args[1])

    def doit(self, **hints):
        self = Basic.doit(self, **hints)
        return self.function(*self.arguments)

class Image(Set):
    """
    >>> from sympy import *
    >>> Image(sin, Interval(0, pi/2))
    Image(sin, [0, pi/2])
    >>> Image(exp, Image(sin, Interval(0, pi/2)))
    Image(FunctionCompose(exp, sin), [0, pi/2])
    >>> Image(FunctionInverse(sin), Image(sin, Interval(0, pi/2)))
    [0, pi/2]
    >>> Image(cos, S.EmptySet)
    EmptySet()
    >>> x, y = symbols('x y')
    >>> Image(cos, Intersection(AbstractSet(x, x > 0), AbstractSet(x, x < 0), evaluate=False))
    Intersection(Image(cos, AbstractSet(x, x > 0)), Image(cos, AbstractSet(x, x < 0)))
    >>> Image(Lambda(x, x+1), Interval(-1, 1)).contains(1)
    True
    >>> Image(Lambda(x, sin(x)+x), Interval(-1, 1)).contains(1)
    And(Apply(FunctionInverse(Lambda(x, x + sin(x))), 1) <= 1, Apply(FunctionInverse(Lambda(x, x + sin(x))), 1) >= -1)
    >>> f = Lambda((x, y), (x*cos(y), x*sin(y)))
    >>> f_inv = FunctionInverse(f)
    >>> f_inv(*f(1, pi/4))
    (-1, -3*pi/4)
    >>> Image(f, ProductSet(Interval(0,1), Interval(-pi,pi))).contains(f(1, pi/4))
    False
    >>> Image(Lambda(x, x+1), Interval(-1, 1)).as_abstract()
    AbstractSet(x0, And(x0 - 1 <= 1, x0 - 1 >= -1))
    >>> g = Lambda((x, y), (x+exp(y), x+sin(y)))
    >>> Image(g, ProductSet(Interval(-1,1), Interval(-1,1))).contains(g(1,2))
    False
    >>> Image(g, AbstractSet((x,y), x<y)).contains(g(1,2))
    False
    """
    def __new__(cls, function, set, **kwargs):
        evaluate = kwargs.pop('evaluate', global_evaluate[0])

        if not is_Function(function):
            raise TypeError('function is not a FunctionClass, Functor or Lambda: %s'%function)
        if not isinstance(set, Set):
            raise TypeError('set is not a Set: %s'%set)

        if evaluate:
            function, set = Image.reduce(function, set)

        if function == Id:
            return set
        else:
            return Set.__new__(cls, function, set, **kwargs)

    @staticmethod
    def reduce(func, set):
        def pre_reduce(func, set):
            while isinstance(set, Image):
                func = FunctionCompose(func, set.function, evaluate=True)
                set = set.set

            if isinstance(set, (Intersection, Union, Complement)):
                args = [Image(func, arg, evaluate=True) for arg in set.args]
                return Id, set.func(*args, evaluate=False)

            if set == S.EmptySet:
                return Id, set

            return func, set

        def post_reduce(func, set):
            if isinstance(func, FunctionCompose):
                funcs = func.functions
                while True:
                    func_, set_ = post_reduce(funcs[-1], set)
                    if (func_, set_) == (funcs[-1], set):
                        break
                    elif func_ != Id:
                        funcs = funcs[:-1] + (func_,)
                        set = set_
                        break
                    else:
                        funcs = funcs[:-1]
                        set = set_
                return FunctionCompose(*funcs, evaluate=False), set

            if hasattr(func, '_image'):
                res = func._image(set)
                if res is not None:
                    if isinstance(res, Image):
                        return res.function, res.set
                    else:
                        return Id, res

            return func, set

        return post_reduce(*pre_reduce(func, set))

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

compose = FunctionCompose
inverse = FunctionInverse


def as_lambda(func):
    """
    >>> from sympy import *
    >>> as_lambda(exp)
    Lambda(a0, exp(a0))
    >>> as_lambda(FunctionCompose(exp, sin))
    Lambda(a0, exp(sin(a0)))
    >>> x = symbols('x')
    >>> as_lambda(FunctionInverse(Lambda(x, sin(x)+exp(x))))
    Lambda(a0, Apply(FunctionInverse(Lambda(x, exp(x) + sin(x))), a0))
    """
    if isinstance(func, Lambda):
        return func
    elif hasattr(func, 'as_lambda'):
        return func.as_lambda()
    else:
        var = symbols('a:%s'%narg(func))
        var = rename_variables_in(var, func_free_symbols(func))
        return Lambda(var, func(*var))

