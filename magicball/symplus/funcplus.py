from functools import reduce
from sympy.core import FunctionClass, Function, Lambda, Tuple
from sympy.core.evaluate import global_evaluate
from sympy.solvers import solve
from sympy.functions import Id
from sympy.sets import Set
from magicball.symplus.util import is_Tuple, rename_variables_in


def is_function(func):
    return isinstance(func, (FunctionClass, Lambda))

def free_symbols(func):
    if isinstance(func, (FunctionClass, Lambda)):
        return getattr(func, 'free_symbols', set())
    else:
        raise TypeError

def nargs(func):
    if isinstance(func, FunctionClass):
        return func.nargs
    elif isinstance(func, Lambda):
        return {len(func.variables)}
    else:
        raise TypeError

def narg(func):
    if isinstance(func, FunctionClass):
        return min(func.nargs)
    elif isinstance(func, Lambda):
        return len(func.variables)
    else:
        raise TypeError

def as_lambda(func):
    if isinstance(func, Lambda):
        return func
    elif hasattr(func, 'as_lambda'):
        return func.as_lambda()
    else:
        var = symbols('a:%s'%narg(cls))
        var = rename_variables_in(var, free_symbols(cls))
        return Lambda(var, cls(*var))

def nres(func):
    if isinstance(func, Lambda):
        if is_Tuple(func.expr):
            return len(func.expr)
        else:
            return 1
    elif isinstance(func, FunctionClass):
        return getattr(func, 'nres', nres(as_lambda(func)))
    else:
        raise TypeError


class FunctionCompose(FunctionClass):
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
            return FunctionCompose.new(mcl, *functions, **kwargs)

    @staticmethod
    def new(mcl, *functions, **kwargs):
        name = ' o '.join(map(str, functions))
        kwargs.__new__ = lambda cls, *args: cls.call(*args)
        kwargs.functions = tuple(functions)
        kwargs.nargs = nargs(functions[-1])
        kwargs.nres = nres(functions[0])
        return FunctionClass.__new__(mcl, name, (Function,), kwargs)

    @staticmethod
    def reduce(funcs):
        funcs = list(funcs)
        i = 0
        while i < len(funcs)-1:
            if funcs[i] == Id:
                funcs = funcs[:i] + funcs[i+1:]
                i = max(i-1, 0)
            elif funcs[i] == FunctionInverse(funcs[i+1]):
                funcs = funcs[:i] + funcs[i+2:]
                i = max(i-1, 0)
            elif FunctionInverse(funcs[i]) == funcs[i+1]:
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
        return reduce(apply_multivar, cls.functions, args)

    @property
    def free_symbols(cls):
        return {sym for sym in func.free_symbols for func in cls.functions}

    def __eq__(self, other):
        return (isinstance(self, FunctionCompose) and
                isinstance(other, FunctionCompose) and
                self.functions == other.functions)

class FunctionInverse(FunctionClass):
    def __new__(mcl, function, **kwargs):
        evaluate = kwargs.pop('evaluate', global_evaluate[0])

        if not isinstance(function, (FunctionClass, Lambda)):
            raise TypeError('function is not a FunctionClass: %s'%function)

        if evaluate:
            function = FunctionCompose.reduce(function)
            eval_cls = FunctionInverse.eval(function)
            if eval_cls is not None:
                return eval_cls

        return FunctionInverse.new(mcl, function, **kwargs)

    @staticmethod
    def new(mcl, function, **kwargs):
        name = '(%s).inv'%(str(function),)
        kwargs.__new__ = lambda cls, *args: cls.call(*args)
        kwargs.function = function
        kwargs.nargs = {nres(function)}
        kwargs.nres = narg(function)
        return FunctionClass.__new__(mcl, name, (Function,), kwargs)

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
    def free_symbols(cls):
        return cls.function.free_symbols

    def __eq__(self, other):
        return (isinstance(self, FunctionInverse) and
                isinstance(other, FunctionInverse) and
                self.function == other.function)


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

