from sympy.core import S
from sympy.sets import Intersection, Union, Set
from magicball.sympy.setplus import AbstractSet


def is_empty(aset):
    if isinstance(aset, Intersection):
        return any(is_empty(arg) == True for arg in aset.args) or None
    elif isinstance(aset, Union):
        res = True
        for arg in aset.args:
            val = is_empty(arg)
            if val == False:
                return False
            elif val == None:
                res = None
        return res
    elif isinstance(aset, AbstractSet):
        return aset.is_empty()
    elif isinstance(aset, Set):
        return aset == S.EmptySet or None
    else:
        raise TypeError('aset is not set: %r' % aset)

def is_open(aset):
    if isinstance(aset, (Union, Intersection)):
        for arg in aset.args:
            if is_open(arg) in (False, None):
                return None
        return True
    elif isinstance(aset, Set):
        try:
            return arg.is_open()
        except NotImplementedError:
            return None
    else:
        raise TypeError('aset is not set: %r' % aset)

def is_closed(aset):
    if isinstance(aset, (Union, Intersection)):
        for arg in aset.args:
            if is_closed(arg) in (False, None):
                return None
        return True
    elif isinstance(aset, Set):
        try:
            return arg.is_closed()
        except NotImplementedError:
            return None
    else:
        raise TypeError('aset is not set: %r' % aset)

def closure(aset):
    if isinstance(aset, Intersection): # need to prove
        if all(is_open(arg) or is_closed(arg) for arg in aset.args):
            return Intersection(*[closure(arg) for arg in aset.args])
        else:
            raise NotImplementedError
    elif isinstance(aset, Union):
        return Union(*[closure(arg) for arg in aset.args])
    elif isinstance(aset, Set):
        return arg.closure()
    else:
        raise TypeError('aset is not set: %r' % aset)

def interior(aset):
    if isinstance(aset, Intersection):
        return Intersection(*[interior(arg) for arg in aset.args])
    elif isinstance(aset, Union): # need to prove
        if all(is_open(arg) or is_closed(arg) for arg in aset.args):
            return Union(*[interior(arg) for arg in aset.args])
        else:
            raise NotImplementedError
    elif isinstance(aset, Set):
        return arg.closure()
    else:
        raise TypeError('aset is not set: %r' % aset)

def boundarys(aset): # need to prove
    if isinstance(aset, Intersection):
        bds = []
        cl = closure(aset)
        for arg in aset.args:
            bds.append([bd & cl for bd in boundarys(arg)])
        return bds
    elif isinstance(aset, Union):
        bds = []
        it = interior(aset)
        for arg in aset.args:
            bds.append([bd - it for bd in boundarys(arg)])
        return bds
    elif isinstance(aset, Set):
        return [arg.boundary()]
    else:
        raise TypeError('aset is not set: %r' % aset)

def boundary(aset):
    return sum(boundarys(aset))


def bdsetsimp(aset, bds=None): # need to prove
    from magicball.sympy.util import deep_iter

    if bds is None:
        bds = boundarys(aset)

    if isinstance(aset, Intersection):
        args = []
        for arg, bd in zip(aset.args, bds):
            if is_empty(sum(deep_iter(bd))) != True:
                args.append(bdsetsimp(arg, bd))
        return Intersection(*args)
    elif isinstance(aset, Union):
        args = []
        for arg, bd in zip(aset.args, bds):
            if is_empty(sum(deep_iter(bd))) != True:
                args.append(bdsetsimp(arg, bd))
        return Union(*args)
    elif isinstance(aset, Set):
        return aset
    else:
        raise TypeError('aset is not set: %r' % aset)

def is_disjoint(*asets): # need to prove
    if all(is_open(aset) for aset in asets):
        bds = tuple(boundary(aset) for aset in asets)
        for bd, aset in zip(bds, asets):
            if bd.is_disjoint(aset) == False:
                return False
        return True
    else:
        return None

