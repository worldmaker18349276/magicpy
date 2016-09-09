from sympy.core import Symbol, Basic
from sympy.core.core import BasicMeta
from sympy.matrices import MatrixSymbol
from symplus.typlus import is_Tuple


def free_symbols(func):
    if isinstance(func, BasicMeta):
        return set()
    elif isinstance(func, Basic):
        return func.free_symbols
    else:
        return set()

def rename_variables_in(variables, varspace):
    if not is_Tuple(variables):
        return rename_variables_in((variables,), varspace)[0]
    names = [v.name for v in variables]
    namespace = {v.name for v in varspace}
    for i in range(len(names)):
        while names[i] in namespace:
            names[i] += '_'
        namespace.add(names[i])
    return list(Symbol(n, **v.assumptions0)
                if isinstance(v, Symbol) else MatrixSymbol(n, v.rows, v.cols)
                for n, v in zip(names, variables))

