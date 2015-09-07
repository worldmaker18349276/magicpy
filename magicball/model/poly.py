from itertools import combinations
from collections import defaultdict
from sympy.core import S, Ge, Le, symbols, nan, oo, zoo
from sympy.functions import sqrt
from sympy.sets import Intersection
from sympy.matrices.immutable import ImmutableMatrix as Mat
from sympy.logic import And
from sympy.polys import Poly
from sympy.matrices import Matrix
from sympy.utilities import lambdify
from sympy.solvers import solve_linear_system
from magicball.model.euclid import halfspace
from magicball.symplus.relplus import is_polynomial
from magicball.symplus.setplus import AbstractSet
from magicball.symplus.util import simplify_with_sqrt


phi = (sqrt(5)+1)/2
vertices_tetra = {
    Mat([ 1, 1, 1]),
    Mat([ 1,-1,-1]),
    Mat([-1, 1,-1]),
    Mat([-1,-1, 1])}
vertices_octa = {
    Mat([ 0, 0, 1]),
    Mat([ 0, 0,-1]),
    Mat([ 0, 1, 0]),
    Mat([ 0,-1, 0]),
    Mat([ 1, 0, 0]),
    Mat([-1, 0, 0])}
vertices_cube = {
    Mat([ 1, 1, 1]),
    Mat([ 1, 1,-1]),
    Mat([ 1,-1, 1]),
    Mat([ 1,-1,-1]),
    Mat([-1, 1, 1]),
    Mat([-1, 1,-1]),
    Mat([-1,-1, 1]),
    Mat([-1,-1,-1])}
vertices_icosa = {
    Mat([ 0, 1, phi]),
    Mat([ 0, 1,-phi]),
    Mat([ 0,-1, phi]),
    Mat([ 0,-1,-phi]),
    Mat([ phi, 0, 1]),
    Mat([-phi, 0, 1]),
    Mat([ phi, 0,-1]),
    Mat([-phi, 0,-1]),
    Mat([ 1, phi, 0]),
    Mat([ 1,-phi, 0]),
    Mat([-1, phi, 0]),
    Mat([-1,-phi, 0])}
vertices_dodeca = {
    Mat([ 1, 1, 1]),
    Mat([ 1, 1,-1]),
    Mat([ 1,-1, 1]),
    Mat([ 1,-1,-1]),
    Mat([-1, 1, 1]),
    Mat([-1, 1,-1]),
    Mat([-1,-1, 1]),
    Mat([-1,-1,-1]),
    Mat([ 0, phi,-1/phi]),
    Mat([ 0, phi, 1/phi]),
    Mat([ 0,-phi,-1/phi]),
    Mat([ 0,-phi, 1/phi]),
    Mat([-1/phi, 0, phi]),
    Mat([ 1/phi, 0, phi]),
    Mat([-1/phi, 0,-phi]),
    Mat([ 1/phi, 0,-phi]),
    Mat([ phi,-1/phi, 0]),
    Mat([ phi, 1/phi, 0]),
    Mat([-phi,-1/phi, 0]),
    Mat([-phi, 1/phi, 0])}

ru_tetra = sqrt(3)
ru_octa = S.One
ru_cube = sqrt(3)
ru_icosa = sqrt(phi+2)
ru_dodeca = sqrt(3)

ri_tetra = 1/sqrt(3)
ri_octa = 1/sqrt(3)
ri_cube = S.One
ri_icosa = (phi+1)/sqrt(3)
ri_dodeca = sqrt(4*phi+3)/sqrt(5)

tetrahedron = Intersection(*[halfspace(v, -ri_tetra, True) for v in vertices_tetra])
octahedron = Intersection(*[halfspace(v, -ri_octa, True) for v in vertices_cube])
cube = Intersection(*[halfspace(v, -ri_cube, True) for v in vertices_octa])
icosahedron = Intersection(*[halfspace(v, -ri_icosa, True) for v in vertices_dodeca])
dodecahedron = Intersection(*[halfspace(v, -ri_dodeca, True) for v in vertices_icosa])


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


_arguments = Matrix(3,4, symbols('a(:3)(:4)'))
_formula = solve_linear_system(_arguments, 0,1,2)
_formula_ = tuple(lambdify(_arguments, _formula[var]) for var in (0,1,2))
def _solve_linsys_(mat):
    try:
        args = tuple(arg.evalf() for arg in mat)
        vertex = tuple(f(*args) for f in _formula_)
    except ZeroDivisionError:
        return None
    else:
        if any(v.has(nan, oo, zoo) for v in vertex):
            return None
        return vertex

def _solve_linsys(mat):
    try:
        vertex = tuple(f(*mat) for f in _formula_)
    except ZeroDivisionError:
        return None
    else:
        vertex = tuple(simplify_with_sqrt(v) for v in vertex)
        if any(v.has(nan, oo, zoo) for v in vertex):
            return None
        return vertex

def to_mesh(convex_polyhedron):
    """
    >>> from sympy import *
    >>> from magicball.model.euclid import *

    >>> p1 = halfspace([-1,-1, 0],-1, closed=True)
    >>> p2 = halfspace([-1, 0,-1],-1, closed=True)
    >>> p3 = halfspace([ 0,-1,-1],-1, closed=True)
    >>> p4 = halfspace([ 1, 1, 1], 0, closed=True)
    >>> vf = to_mesh(p1 & p2 & p3 & p4)
    >>> tuple(sorted(vf[0]))
    ((-sqrt(2), -sqrt(2), 2*sqrt(2)), (-sqrt(2), 2*sqrt(2), -sqrt(2)), \
(sqrt(2)/2, sqrt(2)/2, sqrt(2)/2), (2*sqrt(2), -sqrt(2), -sqrt(2)))
    >>> vf_octa = to_mesh(octahedron)
    >>> set(map(ImmutableMatrix, vf_octa[0])) == vertices_octa
    True
    """
    variables = convex_polyhedron.variables
    faces = []
    for h in convex_polyhedron.expr.args:
        if isinstance(h, Ge):
            faces.append(Poly(h.args[0]-h.args[1], variables))
        else:
            faces.append(Poly(h.args[1]-h.args[0], variables))
    faces_coeff = tuple([f.nth(1,0,0), f.nth(0,1,0), f.nth(0,0,1), -f.nth(0,0,0)]
                        for f in faces)
    faces_func = tuple(lambdify(variables, f.args[0]) for f in faces)
    vertices = []
    vertices_faces = defaultdict(set)
    faces_vertices = defaultdict(set)
    edges_faces = dict()
    for finds in combinations(range(len(faces)), 3):
        if any(set(finds) <= vfaces for vfaces in vertices_faces.values()):
            continue
        if any(efaces < set(finds) for efaces in edges_faces.values()):
            continue

        linsys = Matrix([faces_coeff[find] for find in finds])
        vertexf = _solve_linsys_(linsys)
        if vertexf is None:
            continue
        if not all(faces_func[find](*vertexf) >= -1e-6 for find in range(len(faces))):
            continue
        vertex = _solve_linsys(linsys)
        # print('find vertex '+str(vertex))

        vind = len(vertices)
        vertices.append(vertex)
        for find in range(len(faces)):
            if abs(faces_func[find](*vertexf)) <= 1e-6:
                # print('    lies on face '+str(find))
                vertices_faces[vind].add(find)
                faces_vertices[find].add(vind)

        for vind2 in range(len(vertices)):
            if vind == vind2:
                continue
            edge = frozenset({vind, vind2})
            if edge in edges_faces.keys():
                continue
            efaces = vertices_faces[vind] & vertices_faces[vind2]
            if len(efaces) == 2:
                # print('find edge '+str(tuple(edge)))
                # for find in efaces:
                #     print('    lies on face '+str(find))
                edges_faces[edge] = efaces

    return (vertices, faces, vertices_faces, faces_vertices, edges_faces)

