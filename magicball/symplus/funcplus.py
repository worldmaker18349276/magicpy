from functools import reduce
from sympy.core import Lambda, Expr, Tuple
from sympy.core.operations import AssocOp
from sympy.solvers import solve
from sympy.sets import Set
from sympy.functions import Id
from magicball.symplus.util import is_Tuple, rename_variables_in


class Inverse(Lambda):
    identity = Id

    def __new__(cls, function, **kwargs):
        if not isinstance(function, Lambda):
            raise TypeError('function is not a Lambda: %s' % function)
        return Expr.__new__(cls, function, **kwargs)

    @classmethod
    def eval(cls, func):
        if func == identity:
            return identity
        elif isinstance(func, Inverse):
            return func.function
        elif isinstance(func, Compose):
            return Compose(*[Inverse(f) for f in func.functions[::-1]])

        if hasattr(func, '_inv'):
            inv_func = func._inv()
            if inv_func is not None:
                return inv_func

        return None

    @property
    def function(self):
        return self._args[0]

    @property
    def variables(self):
        expr = self.function.expr
        return expr if is_Tuple(expr) else Tuple(expr)

    @property
    def expr(self):
        var = self.function.variables
        return var if len(var) > 1 else var[0]

    @property
    def free_symbols(self):
        return self.function.free_symbols

    def __call__(self, *args):
        if len(args) != len(self.variables):
            raise ValueError
        solns = solve([expr - val for val, expr in zip(args, self.variables)],
                      self.expr)
        if isinstance(solns, dict):
            return tuple(soln[var] for var, soln in zip(self.function.variables, solns))
        else:
            raise ValueError

    def as_lambda(self):
        var = symbols('a:%s' % len(self.variables))
        var = rename_variables_in(var, self.free_symbols)
        return Lambda(var, self(*var))

    def _hashable_content(self):
        return self._args

    @property
    def is_identity(self):
        return self.function.is_identity


class Compose(Lambda, AssocOp):
    identity = Id

    def __new__(cls, *functions, **kwargs):
        for function in functions:
            if not isinstance(function, Lambda):
                raise TypeError('function is not a Lambda: %s' % function)
        obj = AssocOp.__new__(cls, *functions, **kwargs)

        if kwargs.get('evaluate', global_evaluate[0]):
            if isinstance(obj, Compose):
                eval_obj = Compose.eval(*obj.args)
                if eval_obj is not None:
                    return eval_obj

        return obj

    @classmethod
    def eval(cls, *args):
        funcs = list(args)
        i = 0
        while i < len(funcs)-1:
            if funcs[i] == Inverse(funcs[i+1]) or Inverse(funcs[i]) == funcs[i+1]:
                funcs = funcs[:i] + funcs[i+2:]
                i = max(i-1, 0)
            elif hasattr(funcs[i], '_compose'):
                comp_funcs = funcs[i]._compose(funcs[i+1])
                if comp_funcs is not None:
                    if comp_funcs == cls.identity:
                        funcs = funcs[:i] + funcs[i+2:]
                    else:
                        funcs = funcs[:i] + [comp_funcs] + funcs[i+2:]
                i = max(i-1, 0)
            else:
                i = i + 1

        if funcs == args:
            return False
        else:
            return Compose(*funcs, evaluate=False)


    @property
    def functions(self):
        return self._args

    @property
    def variables(self):
        return self.functions[-1].variables

    @property
    def expr(self):
        return Apply(self, *self.variables)

    @property
    def free_symbols(self):
        return {sym for sym in func.free_symbols for func in self.functions}

    def __call__(self, *args):
        tuple_if_not = lambda a: a if is_Tuple(a) else tuple(a)
        apply_multivar = lambda a, f: f(*tuple_if_not(a))
        return reduce(apply_multivar, self.functions, args)

    def as_lambda(self):
        return Lambda(self.variables, self(*self.variables))

    def _hashable_content(self):
        return self._args

    @property
    def is_identity(self):
        return None


class Apply(Expr):
    def __new__(cls, function, *arguments, **kwargs):
        if not isinstance(function, Lambda):
            raise TypeError('function is not a Lambda: %s' % function)
        return Expr.__new__(cls, function, *arguments, **kwargs)

    @property
    def function(self):
        return self._args[0]

    @property
    def arguments(self):
        return self._args[1:]

    def doit(self, **hints):
        self = Basic.doit(self, **hints)
        return self.function(*self.arguments)


class Image(Set):
    def __new__(cls, function, set, **kwargs):
        if not isinstance(function, Lambda):
            raise TypeError('function is not a Lambda: %s' % function)
        if not isinstance(set, Set):
            raise TypeError('set is not a Set: %s' % set)
        return Set.__new__(cls, function, set, **kwargs)

    @property
    def function(self):
        return self._args[0]

    @property
    def set(self):
        return self._args[1]

