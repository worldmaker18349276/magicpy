from itertools import combinations
from collections import defaultdict
from sympy.core import Ge, Le, Rel
from sympy.polys import Poly
from sympy.logic import And
from sympy.matrices import Matrix
from sympy.simplify import simplify
from sympy.solvers import solve_linear_system
from magicball.symplus.relplus import is_polynomial
from magicball.symplus.setplus import AbstractSet
from magicball.symplus.util import sqrtsimp


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
    >>> p1 = halfspace([-1,-1, 0],-1, closed=True)
    >>> p2 = halfspace([-1, 0,-1],-1, closed=True)
    >>> p3 = halfspace([ 0,-1,-1],-1, closed=True)
    >>> p4 = halfspace([ 1, 1, 1], 0, closed=True)
    >>> v = vertices_of(p1 & p2 & p3 & p4)
    >>> tuple(sorted(v.keys()))
    ((-sqrt(2), -sqrt(2), 2*sqrt(2)), (-sqrt(2), 2*sqrt(2), -sqrt(2)), \
(sqrt(2)/2, sqrt(2)/2, sqrt(2)/2), (2*sqrt(2), -sqrt(2), -sqrt(2)))
    >>> v_octa = vertices_of(octahedron)
    >>> set(map(ImmutableMatrix, v_octa.keys())) == vertices_octa
    True

    # too slow!
    # >>> v_dodeca = vertices_of(dodecahedron)
    # >>> set(map(ImmutableMatrix, v_dodeca.keys())) == vertices_dodeca
    # True
    """
    halfspaces = convex_polyhedron.expr.args
    variables = convex_polyhedron.variables
    rels = tuple(h.func for h in halfspaces)
    planes = tuple(Poly(h.args[0]-h.args[1], variables) for h in halfspaces)
    planes_coeff = tuple([p.nth(1,0,0), p.nth(0,1,0), p.nth(0,0,1), -p.nth(0,0,0)]
                           for p in planes)
    vertices_indices = defaultdict(set)
    for inds in combinations(range(len(planes)), len(variables)):
        if any(set(inds) <= faces for faces in vertices_indices.values()):
            continue

        res = solve_linear_system(
            Matrix([planes_coeff[ind] for ind in inds]),
            *variables, simplify=False)
        if res is None or res == {}:
            continue
        if any(var not in res for var in variables):
            continue
        vertex = tuple(res[var] for var in variables)
        if any(not v.is_number for v in vertex):
            continue

        vertex = simplify(sqrtsimp(simplify(vertex)))
        if any(not r(p(*vertex), 0) for r, p in zip(rels, planes)):
            continue

        # vertexf = tuple(v.evalf() for v in vertex)
        # if any(not r(p(*vertexf), 0) for r, p in zip(rels, planes)):
        #     continue
        # vertex = simplify(sqrtsimp(simplify(vertex)))

        assert vertex not in vertices_indices
        for ind in range(len(planes)):
            if planes[ind](*vertex) == 0:
                vertices_indices[vertex].add(ind)

    vertices_faces = {}
    for v, inds in vertices_indices.items():
        vertices_faces[v] = set(halfspaces[ind] for ind in inds)
    return vertices_faces

