from sympy.core import Symbol, Basic
from sympy.core.core import BasicMeta
from sympy.matrices import MatrixSymbol


def free_symbols(func):
    if isinstance(func, BasicMeta):
        return set()
    elif isinstance(func, Basic):
        return func.free_symbols
    else:
        return set()

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

