from sympy.core import sympify
from sympy.core.evaluate import global_evaluate
from sympy.logic import true, false
from sympy.logic.boolalg import BooleanFunction
from sympy.logic.inference import valid, satisfiable
from symplus.util import *


class Forall(BooleanFunction):
    def __new__(cls, variable, expr, **kwargs):
        evaluate = kwargs.pop('evaluate', global_evaluate[0])
        variable = repack_if_can(sympify(unpack_if_can(variable)))

        for v in pack_if_not(variable):
            if not is_Symbol(v):
                raise TypeError('variable is not a symbol or matrix symbol: %s' % v)
        if not is_Boolean(expr):
            raise TypeError('expression is not boolean or relational: %r' % expr)

        if evaluate:
            return Forall.eval(variable, expr)
        return BooleanFunction.__new__(cls, variable, expr, evaluate=False, **kwargs)

    @staticmethod
    def eval(variable, expr):
        if valid(expr) == True:
            return true
        return Forall(variable, expr, evaluate=False)

    @property
    def variable(self):
        return self._args[0]

    @property
    def variables(self):
        return pack_if_not(self._args[0])

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
        evaluate = kwargs.pop('evaluate', global_evaluate[0])
        variable = repack_if_can(sympify(unpack_if_can(variable)))

        for v in pack_if_not(variable):
            if not is_Symbol(v):
                raise TypeError('variable is not a symbol or matrix symbol: %s' % v)
        if not is_Boolean(expr):
            raise TypeError('expression is not boolean or relational: %r' % expr)

        if evaluate:
            return Exist.eval(variable, expr)
        return BooleanFunction.__new__(cls, variable, expr, **kwargs)

    @staticmethod
    def eval(variable, expr):
        if satisfiable(expr) == False:
            return false
        return Exist(variable, expr, evaluate=False)

    @property
    def variable(self):
        return self._args[0]

    @property
    def variables(self):
        return pack_if_not(self._args[0])

    @property
    def expr(self):
        return self._args[1]

    @property
    def free_symbols(self):
        return self.expr.free_symbols - set(self.variables)

    def _hashable_content(self):
        return (self.expr.xreplace(self.canonical_variables),)

