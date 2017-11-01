from functools import reduce
from sympy.core import (S, FunctionClass, Function, Expr, Basic,
                        Lambda, Tuple, symbols, Dummy, cacheit, sympify)
from sympy.core.evaluate import global_evaluate
from sympy.solvers import solve
from sympy.functions import (Id, exp, log, cos, acos, sin, asin, tan, atan,
                             cot, acot, sec, asec, csc, acsc)
from sympy.sets import Set, Intersection, Union, Complement
from symplus.typlus import FunctionObject, is_Function
from symplus.tuplus import pack_if_not, unpack_if_can, repack_if_can
from symplus.symbplus import free_symbols, rename_variables_in


FunctionClass_inverse_table = {
    cos: acos,
    sin: asin,
}

dummy = Dummy()

def narg(func):
    if isinstance(func, Lambda):
        return len(func.variables)
    elif isinstance(func, FunctionObject):
        return func.narg
    elif isinstance(func, FunctionClass):
        return next(iter(func.nargs))
    else:
        raise TypeError

def nres(func):
    if isinstance(func, Lambda):
        return len(pack_if_not(func.expr))
    elif isinstance(func, FunctionObject):
        return func.nres
    elif isinstance(func, FunctionClass):
        return 1
    else:
        raise TypeError

def FunctionClass_inverse(func):
    if func in FunctionClass_inverse_table:
        return FunctionClass_inverse_table[func]
    else:
        return func(dummy).inverse()

def is_inverse_of(func1, func2):
    if isinstance(func1, FunctionInverse) and func1.function == func2:
        return True
    elif isinstance(func2, FunctionInverse) and func2.function == func1:
        return True
    elif isinstance(func1, FunctionClass) and FunctionClass_inverse(func1) == func2:
        return True
    else:
        return False


class FunctionCompose(FunctionObject):
    """
    >>> from sympy import *
    >>> from symplus.strplus import init_mprinting
    >>> init_mprinting()
    >>> FunctionCompose(exp, sin)
    (exp o sin)
    >>> x, y = symbols('x y')
    >>> FunctionCompose(exp, Lambda(x, x+1))
    (exp o (x |-> x + 1))
    >>> FunctionCompose(Lambda(x, x/2), Lambda(x, x+1))
    (x |-> x/2 + 1/2)
    >>> FunctionCompose(exp, Id)
    exp
    >>> FunctionCompose(exp, FunctionInverse(exp))
    (_x |-> _x)
    >>> FunctionCompose(exp, FunctionCompose(sin, log))
    (exp o sin o log)
    >>> FunctionCompose(exp, sin)(pi/3)
    exp(sqrt(3)/2)
    >>> FunctionCompose(Lambda((x,y), x+y), Lambda(x, (x, x-2)))(3)
    4
    """
    def __new__(cls, *functions, **kwargs):
        evaluate = kwargs.pop('evaluate', global_evaluate[0])

        for function in functions:
            if not is_Function(function):
                raise TypeError('function is not a FunctionClass, FunctionObject or Lambda: %s'%function)

        if evaluate:
            functions = FunctionCompose.reduce(functions)

        if len(functions) == 0:
            return Id
        elif len(functions) == 1:
            return functions[0]
        else:
            return FunctionObject.__new__(cls, *functions)

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
                    variables = rename_variables_in(funcs[i].variables, free_symbols(funcs[i-1]))
                    expr = funcs[i].expr
                    comp_funcs = Lambda(variables, funcs[i-1](*pack_if_not(expr)))
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
        return {sym for func in self.functions for sym in free_symbols(func)}

    def _mathstr(self, printer):
        return '(' + ' o '.join(map(printer._print, self.functions)) + ')'

class FunctionInverse(FunctionObject):
    """
    >>> from sympy import *
    >>> from symplus.strplus import init_mprinting
    >>> init_mprinting()
    >>> x = symbols('x')
    >>> FunctionInverse(Lambda(x, x+1))
    (a0 |-> a0 - 1)
    >>> FunctionInverse(sin)
    asin
    >>> FunctionInverse(FunctionCompose(exp, Lambda(x, x+1)))
    ((a0 |-> a0 - 1) o log)
    >>> FunctionInverse(FunctionInverse(Lambda(x, exp(x)+sin(x))))
    (x |-> exp(x) + sin(x))
    >>> FunctionCompose(FunctionInverse(Lambda(x, x+1)), Lambda(x, x+1))
    (_x |-> _x)
    >>> FunctionInverse(Lambda(x, x+sin(x)))(3)
    (x |-> x + sin(x))`\'(3)
    """
    def __new__(cls, function, **kwargs):
        evaluate = kwargs.pop('evaluate', global_evaluate[0])

        if not is_Function(function):
            raise TypeError('function is not a FunctionClass, FunctionObject or Lambda: %s'%function)

        if evaluate:
            return FunctionInverse.eval(function)

        return FunctionObject.__new__(cls, function)

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

        elif isinstance(func, Lambda):
            var = symbols('a:%s'%nres(func))
            var = rename_variables_in(var, free_symbols(func))
            res = solve_inv(func, *var)
            if res is not None:
                return Lambda(var, res)

        elif isinstance(func, FunctionClass):
            return FunctionClass_inverse(func)

        return FunctionInverse(func, evaluate=False)

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
        res = solve_inv(self.function, *args)
        if res is None:
            return Apply(self, args)
        else:
            return res

    @property
    def free_symbols(self):
        return free_symbols(self.function)

    def _mathstr(self, printer):
        return '{0}`\''.format(printer._print(self.function))

class Apply(Function):
    """
    >>> from sympy import *
    >>> from symplus.strplus import init_mprinting
    >>> init_mprinting()
    >>> Apply(sin, pi)
    sin(pi)
    >>> Apply(exp, Apply(sin, pi))
    (exp o sin)(pi)
    >>> Apply(FunctionInverse(sin), Apply(sin, pi))
    pi
    >>> Apply(sin, pi).doit()
    0
    >>> x, y = symbols('x y')
    >>> Apply(Lambda((x,y), x+y), (1,2))
    (x, y |-> x + y)(1, 2)
    >>> _.doit()
    3
    """
    def __new__(cls, function, argument, **kwargs):
        evaluate = kwargs.pop('evaluate', global_evaluate[0])
        argument = repack_if_can(sympify(unpack_if_can(argument)))

        if not is_Function(function):
            raise TypeError('function is not a FunctionClass, FunctionObject or Lambda: %s'%function)

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

    def _mathstr(self, printer):
        funcstr = printer._print(self.function)
        if len(self.arguments) == 1:
            varstr = '({0})'.format(printer._print(self.arguments[0]))
        else:
            varstr = printer._print(self.arguments)
        return funcstr+varstr

compose = FunctionCompose
inverse = FunctionInverse


def solve_inv(func, *args):
    vars = symbols('a:%s'%narg(func))
    vars = rename_variables_in(vars, free_symbols(func) | free_symbols(Tuple(*args)))
    exprs = pack_if_not(func(*vars))

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
        return None

def as_lambda(func):
    """
    >>> from sympy import *
    >>> from symplus.strplus import init_mprinting
    >>> init_mprinting()
    >>> as_lambda(exp)
    (a0 |-> exp(a0))
    >>> as_lambda(FunctionCompose(exp, sin))
    (a0 |-> exp(sin(a0)))
    >>> x = symbols('x')
    >>> as_lambda(FunctionInverse(Lambda(x, sin(x)+exp(x))))
    (a0 |-> Apply(FunctionInverse(Lambda(x, exp(x) + sin(x))), a0))
    """
    if isinstance(func, Lambda):
        return func
    elif hasattr(func, 'as_lambda'):
        return func.as_lambda()
    else:
        var = symbols('a:%s'%narg(func))
        var = rename_variables_in(var, free_symbols(func))
        return Lambda(var, func(*var))

