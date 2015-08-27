from sympy.core.containers import Tuple
from sympy.core.symbol import Symbol
from sympy.matrices.expressions.matexpr import MatrixSymbol
from sympy.logic.boolalg import true, false


def is_Tuple(t):
    return isinstance(t, (list, tuple, Tuple))

def is_Matrix(m):
    return getattr(m, 'is_Matrix', False)

def is_Symbol(s):
    return isinstance(s, (Symbol, MatrixSymbol))

def is_Boolean(b):
    return getattr(b, 'is_Boolean', False) or getattr(b, 'is_Relational', False) or b in (true, false)
