from sympy.core import Lambda, Expr
from sympy.core.operations import AssocOp
from sympy.sets import Set
from sympy.functions import Id
from magicball.symplus.util import is_Tuple
from functools import reduce


class Compose(Lambda, AssocOp):
    identity = Id

    def __new__(cls, *functions):
        for function in functions:
            if not isinstance(function, Lambda):
                raise TypeError('function is not a Lambda: %s' % function)
        return AssocOp.__new__(cls, *functions)

    @property
    def functions(self):
        return self._args[0]

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

    def doit(self):
        return Lambda(self.variables, self(*self.variables))

    def _hashable_content(self):
        return self._args

    @property
    def is_identity(self):
        return None


class Apply(Expr):
    def __new__(cls, function, *arguments):
        if not isinstance(function, Lambda):
            raise TypeError('function is not a Lambda: %s' % function)
        return Expr.__new__(cls, function, *arguments)

    @property
    def function(self):
        return self._args[0]

    @property
    def arguments(self):
        return self._args[1:]

    def doit(self):
        return self.function(*self.arguments)


class Image(Set):
    def __new__(cls, function, set):
        if not isinstance(function, Lambda):
            raise TypeError('function is not a Lambda: %s' % function)
        if not isinstance(set, Set):
            raise TypeError('set is not a Set: %s' % set)
        return Set.__new__(cls, function, set)

    @property
    def function(self):
        return self._args[0]

    @property
    def set(self):
        return self._args[1]

