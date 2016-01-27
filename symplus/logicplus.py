from sympy.core import sympify
from sympy.logic import true, false
from sympy.logic.boolalg import BooleanFunction
from sympy.logic.inference import valid, satisfiable
from symplus.util import *


class Forall(BooleanFunction):
    def __new__(cls, variable, expr, **kwargs):
        variable = sympify(unpack_if_can(variable))

        for v in tuple_if_not(variable):
            if not is_Symbol(v):
                raise TypeError('variable is not a symbol or matrix symbol: %s' % v)
        if not is_Boolean(expr):
            raise TypeError('expression is not boolean or relational: %r' % expr)

        return BooleanFunction.__new__(cls, variable, expr, **kwargs)

    @classmethod
    def eval(cls, var, expr):
        if valid(expr) == True:
            return true
        return None

    @property
    def variable(self):
        return self._args[0]

    @property
    def variables(self):
        return tuple_if_not(self._args[0])

    @property
    def expr(self):
        return self._args[1]

    @property
    def free_symbols(self):
        return self.expr.free_symbols - set(self.variables)

    def _hashable_content(self):
        return (self.expr.xreplace(self.canonical_variables),)

class Exist(BooleanFunction):
    def __new__(cls, variable, expr, **kwargs):
        variable = sympify(unpack_if_can(variable))

        for v in tuple_if_not(variable):
            if not is_Symbol(v):
                raise TypeError('variable is not a symbol or matrix symbol: %s' % v)
        if not is_Boolean(expr):
            raise TypeError('expression is not boolean or relational: %r' % expr)

        return BooleanFunction.__new__(cls, variable, expr, **kwargs)

    @classmethod
    def eval(cls, variables, expr):
        if satisfiable(expr) == False:
            return false
        return None

    @property
    def variable(self):
        return self._args[0]

    @property
    def variables(self):
        return tuple_if_not(self._args[0])

    @property
    def expr(self):
        return self._args[1]

    @property
    def free_symbols(self):
        return self.expr.free_symbols - set(self.variables)

    def _hashable_content(self):
        return (self.expr.xreplace(self.canonical_variables),)

