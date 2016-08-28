from sympy.core import Tuple
from symplus.typlus import is_Tuple


def pack_if_not(a):
    return Tuple(a) if not is_Tuple(a) else a

def unpack_if_can(a):
    return a[0] if is_Tuple(a) and len(a) == 1 else a

def repack_if_can(a):
    return Tuple(*a) if is_Tuple(a) else a

