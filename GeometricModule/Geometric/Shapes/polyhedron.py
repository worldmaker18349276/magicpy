from math import sqrt, pow
import Part
from Geometric.Basic import *


def star(func):
    def star_func(*vs):
        if len(vs) == 0:
            return None
        elif len(vs) == 1:
            return func(vs[0])
        else:
            return [func(v) for v in vs]
    return star_func

def istar(func):
    def star_func(*vs):
        if len(vs) == 0:
            return None
        elif len(vs) == 1:
            return func(vs[0])
        else:
            return [func(v) for v in vs[::-1]]
    return star_func

e    =  star(lambda v: v)
_e   = istar(lambda v: v)
xy   = istar(lambda v: Vec( v.y, v.x, v.z))
yz   = istar(lambda v: Vec( v.x, v.z, v.y))
zx   = istar(lambda v: Vec( v.z, v.y, v.x))
xyz  =  star(lambda v: Vec( v.y, v.z, v.x))
zyx  =  star(lambda v: Vec( v.z, v.x, v.y))
_x   = istar(lambda v: Vec(-v.x, v.y, v.z))
_y   = istar(lambda v: Vec( v.x,-v.y, v.z))
_z   = istar(lambda v: Vec( v.x, v.y,-v.z))
_xy  =  star(lambda v: Vec(-v.x,-v.y, v.z))
_zx  =  star(lambda v: Vec(-v.x, v.y,-v.z))
_yz  =  star(lambda v: Vec( v.x,-v.y,-v.z))
_xyz = istar(lambda v: Vec(-v.x,-v.y,-v.z))
x_y  =  star(lambda v: Vec(-v.y, v.x, v.z))
y_z  =  star(lambda v: Vec( v.x,-v.z, v.y))
z_x  =  star(lambda v: Vec( v.z, v.y,-v.x))
y_x  =  star(lambda v: Vec( v.y,-v.x, v.z))
z_y  =  star(lambda v: Vec( v.x, v.z,-v.y))
x_z  =  star(lambda v: Vec(-v.z, v.y, v.x))

def map_by(fs, *opss):
    for ops in opss:
        fs = [op(*f) for op in ops for f in fs]
    return fs

def make_polyhedron(vss):
    faces = []
    for vs in vss:
        faces.append(Part.Face(Part.makePolygon(vs+vs[:1])))
    return Part.makeSolid(Part.makeShell(faces))

phi = (sqrt(5)+1)/2

poly = {}


# "4.4.4"
# l = 2.
# ri = 1.
# ru = sqrt(3)
cube = make_polyhedron(
    map_by(
        [[Vec(1,1,1), Vec(-1,1,1), Vec(-1,-1,1), Vec(1,-1,1)]],
        (e, _z), (e, xyz, zyx)
    ))
poly["4.4.4"] = cube

# "3.3.3"
# l = 2*sqrt(2)
# ri = 1/sqrt(3)
# ru = sqrt(3)
tetrahedron = make_polyhedron(
    map_by(
        [[Vec(-1,1,1), Vec(1,-1,1), Vec(1,1,-1)]],
        (e, _xy), (e, _zx)
    ))
poly["3.3.3"] = tetrahedron

# "3.3.3.3"
# l = 2*sqrt(2)
# ri = 2/sqrt(3)
# ru = 2.
octahedron = make_polyhedron(
    map_by(
        [[Vec(2,0,0), Vec(0,2,0), Vec(0,0,2)]],
        (e, _x), (e, _y), (e, _z)
    ))
poly["3.3.3.3"] = octahedron


# "3.3.3.3.3"
# l = 2
# ri = phi**2/sqrt(3)
# ru = sqrt(2+phi)
icosahedron = make_polyhedron(
    map_by(
        [[Vec(1,0,phi), Vec(0,phi,1), Vec(-1,0,phi)]],
        (e, _xy), (e, _yz), (e, xyz, zyx)
    )+map_by(
        [[Vec(1,0,phi), Vec(phi,1,0), Vec(0,phi,1)]],
        (e, _x), (e, _y), (e, _z)
    ))
poly["3.3.3.3.3"] = icosahedron

# "5.5.5"
# l = 2/phi
# ri = phi/sqrt(3-phi)
# ru = sqrt(3)
dodecahedron = make_polyhedron(
    map_by(
        [[Vec(0,1/phi,phi), Vec(0,-1/phi,phi), Vec(1,-1,1), Vec(phi,0,1/phi), Vec(1,1,1)]],
        (e, _xy), (e, _zx), (e, xyz, zyx)
    ))
poly["5.5.5"] = dodecahedron


# "V3.4.3.4"
# l = sqrt(3)
# ri = sqrt(2)
# ru = 2
rhombicDodecahedron = make_polyhedron(
    map_by(
        [[Vec(0,0,2), Vec(1,1,1), Vec(0,2,0), Vec(-1,1,1)]],
        (e, _xy), (e, _yz), (e, xyz, zyx)
    ))
poly["V3.4.3.4"] = rhombicDodecahedron

# "V3.5.3.5"
# l = sqrt(3-phi)
# ri = sqrt(1+phi)
# ru = sqrt(2+phi)
rhombicTriacontahedron = make_polyhedron(
    map_by(
        [[Vec(1,0,phi), Vec(0,1/phi,phi), Vec(-1,0,phi), Vec(0,-1/phi,phi)]],
        (e, _zx), (e, xyz, zyx)
    )+map_by(
        [[Vec(1,0,phi), Vec(1,1,1), Vec(0,phi,1), Vec(0,1/phi,phi)]],
        (e, _x), (e, _xy), (e, _yz), (e, xyz, zyx)
    ))
poly["V3.5.3.5"] = rhombicTriacontahedron


# "3.4.3.4"
# l = sqrt(2)
# ri = 1
# ru = sqrt(2)
cuboctahedron = make_polyhedron(
    map_by(
        [[Vec(1,0,1), Vec(0,1,1), Vec(-1,0,1), Vec(0,-1,1)]],
        (e, _z), (e, xyz, zyx)
    )+map_by(
        [[Vec(1,0,1), Vec(1,1,0), Vec(0,1,1)]],
        (e, _x), (e, _y), (e, _z)
    ))
poly["3.4.3.4"] = cuboctahedron

# "3.5.3.5"
# l = 1
# ri = sqrt(4*phi+3)/sqrt(5)
# ru = phi
icosidodecahedron = make_polyhedron(
    map_by(
        [[Vec(0,0,phi), Vec(0.5,-phi/2,(1+phi)/2), Vec((1+phi)/2,-0.5,phi/2), Vec((1+phi)/2,0.5,phi/2), Vec(0.5,phi/2,(1+phi)/2)]],
        (e, _xy), (e, _zx), (e, xyz, zyx)
    )+map_by(
        [[Vec(0,0,phi), Vec(0.5,phi/2,(1+phi)/2), Vec(-0.5,phi/2,(1+phi)/2)]],
        (e, _xy), (e, _zx), (e, xyz, zyx)
    )+map_by(
        [[Vec(0.5,phi/2,(1+phi)/2), Vec((1+phi)/2,0.5,phi/2), Vec(phi/2,(1+phi)/2,0.5)]],
        (e, _x), (e, _y), (e, _z)
    ))
poly["3.5.3.5"] = icosidodecahedron


c = 1+sqrt(2)
# "3.4.4.4"
# l = 2
# ri = c
# ru = sqrt(3+2*c)
rhombicuboctahedron = make_polyhedron(
    map_by(
        [[Vec(1,1,c), Vec(-1,1,c), Vec(-1,-1,c), Vec(1,-1,c)]],
        (e, _z), (e, xyz, zyx)
    )+map_by(
        [[Vec(1,1,c), Vec(1,c,1), Vec(-1,c,1), Vec(-1,1,c)]],
        (e, _y), (e, _z), (e, xyz, zyx)
    )+map_by(
        [[Vec(1,1,c), Vec(c,1,1), Vec(1,c,1)]],
        (e, _x), (e, _y), (e, _z)
    ))
poly["3.4.4.4"] = rhombicuboctahedron

# "3.4.5.4"
# l = 2
# ri = 3*sqrt((4*phi+3)/5)
# ru = sqrt(8*phi+7)
rhombicosidodecahedron = make_polyhedron(
    map_by(
        [[Vec(1,1,phi**3), Vec(1,-1,phi**3), Vec(phi**2,-phi,phi*2), Vec(2+phi,0,phi**2), Vec(phi**2,phi,phi*2)]],
        (e, _x), (e, _z), (e, xyz, zyx)
    )+map_by(
        [[Vec(phi,phi*2,phi**2), Vec(phi*2,phi**2,phi), Vec(phi**2,phi,phi*2)]],
        (e, _x), (e, _y), (e, _z)
    )+map_by(
        [[Vec(1,1,phi**3), Vec(-1,1,phi**3), Vec(-1,-1,phi**3), Vec(1,-1,phi**3)]],
        (e, _z), (e, xyz, zyx)
    )+map_by(
        [[Vec(1,1,phi**3), Vec(0,phi**2,2+phi), Vec(-1,1,phi**3)]],
        (e, _y), (e, _z), (e, xyz, zyx)
    )+map_by(
        [[Vec(1,1,phi**3), Vec(phi**2,phi,phi*2), Vec(phi,phi*2,phi**2), Vec(0,phi**2,2+phi)]],
        (e, _x), (e, _y), (e, _z), (e, xyz, zyx)
    ))
poly["3.4.5.4"] = rhombicosidodecahedron


t = (1+pow(19+3*sqrt(33), 1/3.)+pow(19-3*sqrt(33), 1/3.))/3
# "3.3.3.3.4"
# l = sqrt(2/t**2+2)
# ri = t
# ru = sqrt(1+2*t)
snubCube = make_polyhedron(
    map_by(
        [[Vec(1,1/t,t), Vec(-1/t,1,t), Vec(-1,-1/t,t), Vec(1/t,-1,t)]],
        (e, _yz), (e, xyz, zyx)
    )+map_by(
        [[Vec(1,1/t,t), Vec(t,1,1/t), Vec(1/t,t,1)]],
        (e, _yz), (e, x_y, _xy, y_x)
    )+map_by(
        [[Vec(1,1/t,t), Vec(1/t,t,1), Vec(-1/t,1,t)]],
        (e, _yz), (e, x_y, _xy, y_x), (e, xyz, zyx)
    ))
poly["3.3.3.3.4"] = snubCube

xi = pow(phi/2+sqrt(phi-5./27)/2, 1./3) + pow(phi/2-sqrt(phi-5./27)/2, 1./3)
a = xi-1/xi
b = xi*phi+phi**2+phi/xi
v1 = Vec(2*a,2,2*b)
v2 = Vec(a+b/phi-phi, a*phi-b+1/phi,a/phi+b*phi+1)
v3 = Vec(-a/phi+b*phi-1, a-b/phi-phi,a*phi+b+1/phi)
v4 = Vec(-a/phi+b*phi+1,-a+b/phi-phi,a*phi+b-1/phi)
v5 = Vec(a+b/phi+phi,-a*phi+b+1/phi,a/phi+b*phi-1)
# "3.3.3.3.5"
# l = 4
# ri = 2*sqrt((a**2*(3-phi)+b**2*(phi+2)+2*a*b*(2*phi-1))/5)
# ru = 2*sqrt(a**2+b**2+1)
snubDodecahedron = make_polyhedron(
    map_by(
        [[v1,v2,v3,v4,v5]],
        (e, _xy), (e, _zx), (e, xyz, zyx)
    )+map_by(
        [[v1, _xy(v1), v2]],
        (e, _xy), (e, _zx), (e, xyz, zyx)
    )+map_by(
        [[v1, xyz(v4), _xy(v2)]],
        (e, _xy), (e, _zx), (e, xyz, zyx)
    )+map_by(
        [[v1, v5, xyz(v4)]],
        (e, _xy), (e, _zx), (e, xyz, zyx)
    )+map_by(
        [[v5, xyz(v5), xyz(v4)]],
        (e, _xy), (e, _zx), (e, xyz, zyx)
    )+map_by(
        [[v5, zyx(v5), xyz(v5)]],
        (e, _xy), (e, _zx)
    )+map_by(
        [[_xy(v2), xyz(v4), xyz(v3)]],
        (e, _xy), (e, _zx), (e, xyz, zyx)
    )+map_by(
        [[_xy(v2), xyz(v3), _xy(v3)]],
        (e, _xy), (e, _zx), (e, xyz, zyx)
    )+map_by(
        [[_xy(v3), xyz(v3), zyx(_yz(v3))]],
        (e, _xy), (e, _zx)
    ))
poly["3.3.3.3.5"] = snubDodecahedron
