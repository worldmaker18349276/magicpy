from itertools import combinations
from collections import defaultdict
from sympy.core import S, Ge, Le, symbols, nan, oo, zoo
from sympy.functions import sqrt
from sympy.logic import And
from sympy.sets import Intersection
from sympy.utilities import lambdify
from sympy.polys import Poly
from sympy.solvers import solve_linear_system
from sympy.simplify import simplify
from sympy.matrices import Matrix
from sympy.matrices.immutable import ImmutableMatrix as Mat
from magicball.model.euclid import halfspace
from symplus.matplus import x, y, z, dot, cross
from symplus.setplus import AbstractSet
from symplus.simplus import is_polynomial, with_sqrtsimp


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
        vertex = tuple(with_sqrtsimp(simplify)(v) for v in vertex)
        if any(v.has(nan, oo, zoo) for v in vertex):
            return None
        return vertex

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

class ConvexPolyhedron:
    def __init__(self, v, f, e=None, vf=None, fv=None, vv=None, ff=None):
        self.vertices = v
        self.faces = f
        self.edges = e
        self.vertices_faces = vf
        self.faces_vertices = fv
        self.vertices_vertices = vv
        self.faces_faces = ff

    @classmethod
    def from_hrepr(cls, hrepr):
        """
        >>> from sympy import *
        >>> from magicball.model.euclid import *
        >>> p1 = halfspace([-1,-1, 0],-1, closed=True)
        >>> p2 = halfspace([-1, 0,-1],-1, closed=True)
        >>> p3 = halfspace([ 0,-1,-1],-1, closed=True)
        >>> p4 = halfspace([ 1, 1, 1], 0, closed=True)
        >>> poly1 = ConvexPolyhedron.from_hrepr(p1 & p2 & p3 & p4)
        >>> tuple(sorted(poly1.vertices))
        ((-sqrt(2), -sqrt(2), 2*sqrt(2)), (-sqrt(2), 2*sqrt(2), -sqrt(2)), (sqrt(2)/2, sqrt(2)/2, sqrt(2)/2), (2*sqrt(2), -sqrt(2), -sqrt(2)))
        """
        variables = hrepr.variables
        faces = []
        for h in hrepr.expr.args:
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
        edges_f = set()
        for finds in combinations(range(len(faces)), 3):
            if any(set(finds) <= vfaces for vfaces in vertices_faces.values()):
                continue
            if any(efaces < set(finds) for efaces in edges_f):
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
                efaces = frozenset(vertices_faces[vind] & vertices_faces[vind2])
                if efaces in edges_f:
                    continue
                if len(efaces) == 2:
                    # print('find edge '+str(tuple(efaces)))
                    edges_f.add(efaces)

        # print('commpute direction of edges...')
        directed_edges = set()
        for f1, f2 in map(tuple, edges_f):
            v1, v2 = sorted(faces_vertices[f1] & faces_vertices[f2])
            v12 = (Mat(vertices[v2])-Mat(vertices[v1])).evalf()
            n1 = Mat(faces_coeff[f1][0:3]).evalf()
            n2 = Mat(faces_coeff[f2][0:3]).evalf()
            if dot(cross(n1, n2), v12) < 0:
                f1, f2 = f2, f1
            directed_edges.add((v1,v2,f1,f2))

        # print('commpute direction of vertices...')
        directed_vertices_faces = dict()
        directed_vertices_vertices = dict()
        for v, fs in vertices_faces.items():
            f0 = min(fs)
            directed_vertices_faces[v] = [f0]
            directed_vertices_vertices[v] = []
            f1 = f0
            while True:
                for vb, vf, fl, fr in directed_edges:
                    if vb == v and fr == f1:
                        directed_vertices_faces[v].append(fl)
                        directed_vertices_vertices[v].append(vf)
                        f1 = fl
                        break
                    elif vf == v and fl == f1:
                        directed_vertices_faces[v].append(fr)
                        directed_vertices_vertices[v].append(vb)
                        f1 = fr
                        break
                if f1 == f0:
                    directed_vertices_faces[v].pop()
                    vs = directed_vertices_vertices[v]
                    v0 = min(vs)
                    ind = vs.index(v0)
                    directed_vertices_vertices[v] = vs[ind:]+vs[:ind]
                    break

        # print('commpute direction of faces...')
        directed_faces_vertices = dict()
        directed_faces_faces = dict()
        for f, vs in faces_vertices.items():
            v0 = min(vs)
            directed_faces_vertices[f] = [v0]
            directed_faces_faces[f] = []
            v1 = v0
            while True:
                for vb, vf, fl, fr in directed_edges:
                    if vb == v1 and fl == f:
                        directed_faces_vertices[f].append(vf)
                        directed_faces_faces[f].append(fr)
                        v1 = vf
                        break
                    elif vf == v1 and fr == f:
                        directed_faces_vertices[f].append(vb)
                        directed_faces_faces[f].append(fl)
                        v1 = vb
                        break
                if v1 == v0:
                    directed_faces_vertices[f].pop()
                    fs = directed_faces_faces[f]
                    f0 = min(fs)
                    ind = fs.index(f0)
                    directed_faces_faces[f] = fs[ind:]+fs[:ind]
                    break

        return cls(vertices, faces,
                   e=directed_edges,
                   vf=directed_vertices_faces,
                   fv=directed_faces_vertices,
                   vv=directed_vertices_vertices,
                   ff=directed_faces_faces)

    def as_hrepr(self):
        return AbstractSet((x,y,z), And(*[face(x,y,z)>=0 for face in self.faces]))

