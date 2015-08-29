from sympy.core import Symbol, Tuple
from sympy.matrices import MatrixSymbol
from sympy.logic import true, false


def is_Tuple(t):
    return isinstance(t, (list, tuple, Tuple))

def is_Matrix(m):
    return getattr(m, 'is_Matrix', False)

def is_Symbol(s):
    return isinstance(s, (Symbol, MatrixSymbol))

def is_Boolean(b):
    return (getattr(b, 'is_Boolean', False) or
            getattr(b, 'is_Relational', False) or
            b is true or
            b is false)


def deep_iter(sequence, depth=-1, types=(list, tuple), iter=iter):
    if not isinstance(sequence, types) or depth == 0:
        return sequence
    for elem in iter(sequence):
        for e in deep_enum(elem, depth-1, types, iter):
            yield e

def deep_enum(sequence, depth=-1, types=(list, tuple), iter=iter):
    if not isinstance(sequence, types) or depth == 0:
        return (), sequence
    n = 0
    for elem in iter(sequence):
        for k, e in deep_enum(elem, depth-1, types, iter):
            yield (n,)+k, e
        n += 1

import operator
def deep_get(sequence, key, getter=operator.getitem):
    if key is ():
        return sequence
    deep_get(getter(sequence, key[0]), key[1:], getter)

