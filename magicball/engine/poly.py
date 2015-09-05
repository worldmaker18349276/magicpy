from itertools import combinations
from collections import defaultdict
from sympy.core import Ge, Le
from sympy.polys import Poly
from sympy.logic import And
from sympy.solvers import solve
from magicball.symplus.relplus import is_polynomial
from magicball.symplus.setplus import AbstractSet


def is_convex_polyhedron(aset):
    if not isinstance(aset, AbstractSet):
        return False
    if not isinstance(aset.expr, And):
        return False
    if any(not isinstance(h, (Ge, Le)) for h in aset.expr.args):
        return False
    planes = tuple(h.args[0]-h.args[1] for h in aset.expr.args)
    if any(not is_polynomial(p) or not Poly(p, aset.variables).is_linear for p in planes):
        return False

def vertices_of(convex_polyhedron):
    """
    >>> from sympy import *
    >>> from magicball.model.euclid import *
    >>> p1 = halfspace([1,1,0], -1, closed=True)
    >>> p2 = halfspace([1,0,1], -1, closed=True)
    >>> p3 = halfspace([0,1,1], -1, closed=True)
    >>> p4 = halfspace([-1,-1,-1], 0, closed=True)
    >>> v = vertices_of(p1 & p2 & p3 & p4)
    >>> tuple(sorted(v.keys()))
    ((-2*sqrt(2), sqrt(2), sqrt(2)), (-sqrt(2)/2, -sqrt(2)/2, -sqrt(2)/2), \
(sqrt(2), -2*sqrt(2), sqrt(2)), (sqrt(2), sqrt(2), -2*sqrt(2)))
    """
    halfspaces = convex_polyhedron.expr.args
    variables = convex_polyhedron.variables
    planes = tuple(h.args[0]-h.args[1] for h in halfspaces)
    halfspaces_planes = dict(zip(halfspaces, planes))
    vertices_faces = defaultdict(set)
    for hps in combinations(halfspaces_planes.items(), len(variables)):
        ps = dict(hps).values()
        hs = dict(hps).keys()
        if any(hs <= faces for faces in vertices_faces.values()):
            continue

        res = solve(ps, variables)
        if not res:
            continue
        vertex = tuple(res[var] for var in variables)
        if any(not v.is_number for v in vertex):
            continue
        if not convex_polyhedron.contains(vertex):
            continue

        for h, p in halfspaces_planes.items():
            if p.xreplace(dict(zip(variables, vertex))) == 0:
                vertices_faces[vertex].add(h)

    return vertices_faces

