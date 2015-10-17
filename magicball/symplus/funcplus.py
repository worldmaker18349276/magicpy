from functools import reduce
from sympy.core import FunctionClass, Function, Lambda, Tuple, symbols, cacheit
from sympy.core.evaluate import global_evaluate
from sympy.solvers import solve
from sympy.functions import Id
from sympy.sets import Set
from magicball.symplus.util import is_Tuple, rename_variables_in


def is_function(func):
    return isinstance(func, (FunctionClass, Lambda))

def free_symbols(func):
    if isinstance(func, Lambda):
        return func.free_symbols
    elif isinstance(func, FunctionClass):
        return getattr(func, 'func_free_symbols', set())
    else:
        raise TypeError

def narg(func):
    if isinstance(func, Lambda):
        return len(func.variables)
    elif isinstance(func, FunctionClass):
        return next(iter(func.nargs))
    else:
        raise TypeError

def as_lambda(func):
    if isinstance(func, Lambda):
        return func
    elif hasattr(func, 'as_lambda'):
        return func.as_lambda()
    else:
        var = symbols('a:%s'%narg(func))
        var = rename_variables_in(var, free_symbols(func))
        return Lambda(var, func(*var))

def nres(func):
    if isinstance(func, Lambda):
        if is_Tuple(func.expr):
            return len(func.expr)
        else:
            return 1
    elif isinstance(func, FunctionClass):
        return getattr(func, 'nres', 1)
    else:
        raise TypeError


class VariableFunctionClass(FunctionClass):
    def __new__(mcl, name, nargs, nres, fields):
        fields['__new__'] = lambda cls, *args: cls.call(*args)
        fields['nargs'] = (narg,)
        fields['nres'] = nres
        return FunctionClass.__new__(mcl, name, (Function,), fields)

    def __init__(cls, *args, **kwargs):
        pass

    def call(cls, *args):
        return None

    @property
    def func_free_symbols(cls):
        return set()

class FunctionCompose(VariableFunctionClass):
    """
    >>> from sympy import *
    >>> FunctionCompose(exp, sin)
    (exp o sin)
    >>> FunctionCompose(exp, sin)(pi/3)
    exp(sqrt(3)/2)
    """
    def __new__(mcl, *functions, **kwargs):
        evaluate = kwargs.pop('evaluate', global_evaluate[0])

        for function in functions:
            if not isinstance(function, (FunctionClass, Lambda)):
                raise TypeError('function is not a FunctionClass or Lambda: %s'%function)

        if evaluate:
            functions = FunctionCompose.reduce(functions)

        if len(functions) == 0:
            return Id
        elif len(functions) == 1:
            return functions[0]
        else:
            return FunctionCompose.new_cached(mcl, tuple(functions))

    def __init__(cls, *args, **kwargs):
        pass

    @staticmethod
    @cacheit
    def new_cached(mcl, functions):
        name = '(' + ' o '.join(map(str, functions)) + ')'
        fnarg, fnres = narg(functions[-1]), nres(functions[0])
        fields = {'functions': functions}
        return VariableFunctionClass.__new__(mcl, name, fnarg, fnres, fields)

    @staticmethod
    def reduce(funcs):
        funcs = list(funcs)
        i = 0
        while i < len(funcs)-1:
            if funcs[i] == Id:
                funcs = funcs[:i] + funcs[i+1:]
                i = max(i-1, 0)
            elif funcs[i+1] == Id:
                funcs = funcs[:i+1] + funcs[i+2:]
            elif (isinstance(funcs[i+1], FunctionInverse) and
                  funcs[i] == funcs[i+1].function or
                  isinstance(funcs[i], FunctionInverse) and
                  funcs[i+1] == funcs[i].function):
                funcs = funcs[:i] + funcs[i+2:]
                i = max(i-1, 0)
            elif isinstance(funcs[i], FunctionCompose):
                funcs = funcs[:i] + funcs[i].functions + funcs[i+1:]
                i = max(i-1, 0)
            elif hasattr(funcs[i], '_compose'):
                comp_funcs = funcs[i]._compose(funcs[i+1])
                if comp_funcs is not None:
                    funcs = funcs[:i] + [comp_funcs] + funcs[i+2:]
                i = max(i-1, 0)
            else:
                i = i + 1

        return funcs

    def call(cls, *args):
        tuple_if_not = lambda a: a if is_Tuple(a) else (a,)
        apply_multivar = lambda a, f: f(*tuple_if_not(a))
        return reduce(apply_multivar, cls.functions[::-1], args)

    @property
    def func_free_symbols(cls):
        return {sym for sym in func.func_free_symbols for func in cls.functions}

    def __eq__(self, other):
        return (isinstance(self, FunctionCompose) and
                isinstance(other, FunctionCompose) and
                self.functions == other.functions)

    def __hash__(self):
        return hash((type(self).__name__,) + self.functions)

class FunctionInverse(FunctionClass):
    """
    >>> from sympy import *
    >>> FunctionInverse(sin)
    sin.inv
    >>> FunctionInverse(FunctionCompose(exp, sin))
    (sin.inv o exp.inv)
    >>> FunctionInverse(FunctionInverse(exp))
    exp
    >>> FunctionCompose(FunctionInverse(exp), exp)
    Lambda(_x, _x)
    """
    def __new__(mcl, function, **kwargs):
        evaluate = kwargs.pop('evaluate', global_evaluate[0])

        if not isinstance(function, (FunctionClass, Lambda)):
            raise TypeError('function is not a FunctionClass or: %s'%function)

        if evaluate:
            eval_func = FunctionInverse.eval(function)
            if eval_func is not None:
                return eval_func

        return FunctionInverse.new_cached(mcl, function)

    def __init__(cls, *args, **kwargs):
        pass

    @staticmethod
    @cacheit
    def new_cached(mcl, function):
        name = '%s.inv'%(str(function),)
        fnarg, fnres = nres(function), narg(function)
        fields = {'function': function}
        return VariableFunctionClass.__new__(mcl, name, fnarg, fnres, fields)

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

        return None

    def call(cls, *args):
        func = as_lambda(cls.function)
        exprs = func.expr if nres(func) > 1 else Tuple(func.expr)
        vars = func.variables
        if len(args) != len(exprs):
            raise ValueError
        solns = solve([expr - val for val, expr in zip(args, exprs)], vars)
        if isinstance(solns, dict):
            return tuple(soln[var] for var, soln in zip(vars, solns))
        else:
            raise ValueError

    @property
    def func_free_symbols(cls):
        return cls.function.func_free_symbols

    def __eq__(self, other):
        return (isinstance(self, FunctionInverse) and
                isinstance(other, FunctionInverse) and
                self.function == other.function)

    def __hash__(self):
        return hash((type(self).__name__, self.function))

class Apply(Function):
    def __new__(cls, function, arguments, **kwargs):
        evaluate = kwargs.pop('evaluate', global_evaluate[0])

        if not isinstance(function, (FunctionClass, Lambda)):
            raise TypeError('function is not a FunctionClass or Lambda: %s'%function)

        if evaluate:
            function, arguments = Apply.reduce(function, arguments)

        if function == Id:
            return arguments
        else:
            return Expr.__new__(cls, function, arguments, **kwargs)

    @classmethod
    def reduce(cls, func, args):
        if isinstance(args, Apply):
            return cls.reduce(FunctionCompose(func, args.function), args.arguments)
        else:
            return func, args

    @property
    def function(self):
        return self._args[0]

    @property
    def arguments(self):
        return self._args[1]

    def doit(self, **hints):
        self = Basic.doit(self, **hints)
        return self.function(*self.arguments)

class Image(Set):
    def __new__(cls, function, set, **kwargs):
        evaluate = kwargs.pop('evaluate', global_evaluate[0])

        if not isinstance(function, (FunctionClass, Lambda)):
            raise TypeError('function is not a FunctionClass or Lambda: %s'%function)
        if not isinstance(set, Set):
            raise TypeError('set is not a Set: %s'%set)

        if evaluate:
            function, set = Image.reduce(function, set)

        if function == Id:
            return set
        else:
            return Set.__new__(cls, function, set, **kwargs)

    @classmethod
    def reduce(cls, func, set):
        if isinstance(set, Image):
            return cls.reduce(FunctionCompose(func, set.function), set.set)
        else:
            return func, set

    @property
    def function(self):
        return self._args[0]

    @property
    def set(self):
        return self._args[1]

    def _contains(self, mem):
        mem = mem if is_Tuple(mem) else (mem,)
        return self.set._contains(FunctionInverse(self.function)(*mem))

