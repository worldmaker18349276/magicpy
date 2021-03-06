from sympy.core import Symbol, Tuple, FunctionClass, Lambda, Expr, Basic
from sympy.core.core import BasicMeta
from sympy.matrices import MatrixSymbol
from sympy.logic import true, false


class FunctionObject(Basic):
    def __call__(self, *args):
        return self.call(*args)

    # def call(self, *args):
    #     return None

    # @property
    # def narg(self):
    #     return 1

    # @property
    # def nres(self):
    #     return 1

    # def _compose(self, other):
    #     return None

    # def _inv(self):
    #     return None

    # def as_lambda(self):
    #     ...


def is_Tuple(obj):
    return (isinstance(obj, Tuple) or
            isinstance(obj, (list, tuple)))

def is_Symbol(obj):
    return isinstance(obj, (Symbol, MatrixSymbol))

def is_Number(obj):
    return (getattr(obj, 'is_number', False) or
            getattr(obj, 'is_Number', False) or
            isinstance(obj, Expr) or
            isinstance(obj, (int, float, complex)))

def is_Boolean(obj):
    return (getattr(obj, 'is_Boolean', False) or
            getattr(obj, 'is_Relational', False) or
            obj in (true, false) or
            isinstance(obj, Symbol) or
            isinstance(obj, bool))

def is_Matrix(obj):
    return getattr(obj, 'is_Matrix', False)

def is_Function(obj):
    return isinstance(obj, (FunctionClass, FunctionObject, Lambda))

def type_match(obj1, obj2):
    if is_Tuple(obj1):
        if not is_Tuple(obj2):       return false
        if len(obj1) != len(obj2):   return false
        return all(map(type_match, obj1, obj2))
    elif is_Matrix(obj1):
        if not is_Matrix(obj2):      return false
        if obj1.shape != obj2.shape: return false
    elif is_Function(obj1):
        if not is_Function(obj2):    return false
        if narg(obj1) != narg(obj2): return false
        if nres(obj1) != nres(obj2): return false
    elif is_Number(obj1):
        if not is_Number(obj2):      return false
    elif is_Boolean(obj1):
        if not is_Boolean(obj2):     return false
    else:                            return false
    return true


def pack_if_not(a):
    return Tuple(a) if not is_Tuple(a) else a

def unpack_if_can(a):
    return a[0] if is_Tuple(a) and len(a) == 1 else a

def repack_if_can(a):
    return Tuple(*a) if is_Tuple(a) else a


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

