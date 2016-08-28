from sympy.matrices.immutable import ImmutableMatrix
from sympy.functions import sqrt, acos
from sympy.core import pi, Symbol


Mat = ImmutableMatrix

i, j, k = e = Mat([1,0,0]), Mat([0,1,0]), Mat([0,0,1])
x, y, z = Symbol('x', real=True), Symbol('y', real=True), Symbol('z', real=True)
r = Mat([x, y, z])

def norm(vec):
    return sqrt(sum(v**2 for v in vec))

def normalize(vec):
    return vec/norm(vec)

def dot(vec1, vec2):
    return (vec1.T*vec2)[0]

def cross(vec1, vec2=None):
    if vec2 is None:
        x, y, z = vec1
        return Mat([[ 0,-z, y],
                    [ z, 0,-x],
                    [-y, x, 0]])
    else:
        return cross(vec1)*vec2

def angle(vec1, vec2, vec3=None):
    if vec3 is None:
        return acos(dot(normalize(vec1), normalize(vec2)))
    else:
        if dot(cross(vec1, vec2), vec3) > 0:
            return angle(cross(vec1, vec3), cross(vec2, vec3))
        else:
            return 2*pi-angle(cross(vec1, vec3), cross(vec2, vec3))

def project(vec1, vec2):
    vec2 = normalize(vec2)
    return dot(vec1, vec2)*vec2

