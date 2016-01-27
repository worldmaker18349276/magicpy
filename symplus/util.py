from sympy.core import Symbol, Tuple, FunctionClass, Lambda
from sympy.matrices import MatrixSymbol
from sympy.logic import true, false


# type

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

def is_Function(func):
    return isinstance(func, (FunctionClass, Lambda))

def tuple_if_not(a):
    return a if is_Tuple(a) else Tuple(a)

def unpack_if_can(a):
    return a if not is_Tuple(a) or len(a) > 1 else a[0]


# variable

def rename_variables_in(variables, varspace):
    names = [v.name for v in variables]
    namespace = {v.name for v in varspace}
    for i in range(len(names)):
        while names[i] in namespace:
            names[i] += '_'
        namespace.add(names[i])
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

