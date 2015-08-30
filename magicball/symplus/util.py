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


class DummyMatrixSymbol(MatrixSymbol):
    _count = 0
    __slots__ = ['dummy_index']
    is_Dummy = True
    def __new__(cls, name, n, m):
        obj = MatrixSymbol.__new__(cls, name, n, m)
        cls._count += 1
        obj.dummy_index = cls._count
        return obj
    def _hashable_content(self):
        return self.name, self.shape, self.dummy_index

def as_dummy(var):
    if isinstance(var, Symbol):
        return var.as_dummy()
    elif isinstance(var, MatrixSymbol):
        return DummyMatrixSymbol('_'+var.name, var.shape[0], var.shape[1])
    else:
        raise TypeError('variable is not a symbol or matrix symbol: %s' % var)

def rename_variables_in(variables, varspace):
    names = [v.name for v in variables]
    namespace = [v.name for v in varspace]
    for i in range(len(names)):
        while names[i] in namespace or names[i] in names[:i]:
            names[i] += '_'
    return list(Symbol(n, **v.assumptions0)
                if isinstance(v, Symbol) else MatrixSymbol(n, v.rows, v.cols)
                for n, v in zip(names, variables))

def var_type_match(vars1, vars2):
    if len(vars1) != len(vars2):
        return false
    for v1, v2 in zip(vars1, vars2):
        if isinstance(v1, Symbol):
            if is_Matrix(v2): # TODO: real/complex test
                return false
        elif isinstance(v1, MatrixSymbol):
            if not is_Matrix(v2) or v1.shape != v2.shape:
                return false
        else:
            raise TypeError('variable is not a symbol or matrix symbol: %s' % v1)
    return true


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

