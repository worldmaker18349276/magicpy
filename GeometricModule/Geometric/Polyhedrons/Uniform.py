from math import sqrt, pow
from Geometric.Basic import *
from Geometric.Polyhedrons.Utilities import *


# "4.4.4"
# l = 2.
# ri = 1.
# ru = sqrt(3)
cube = make_polyhedron(
    map_by(
        [[Vec(1,1,1), Vec(-1,1,1), Vec(-1,-1,1), Vec(1,-1,1)]],
        (e, iz), (e, xyz, zyx)
    ))
poly["4.4.4"] = cube

# "3.3.3"
# l = 2*sqrt(2)
# ri = 1/sqrt(3)
# ru = sqrt(3)
tetrahedron = make_polyhedron(
    map_by(
        [[Vec(-1,1,1), Vec(1,-1,1), Vec(1,1,-1)]],
        (e, ixy), (e, izx)
    ))
poly["3.3.3"] = tetrahedron

# "3.3.3.3"
# l = 2*sqrt(2)
# ri = 2/sqrt(3)
# ru = 2.
octahedron = make_polyhedron(
    map_by(
        [[Vec(2,0,0), Vec(0,2,0), Vec(0,0,2)]],
        (e, ix), (e, iy), (e, iz)
    ))
poly["3.3.3.3"] = octahedron


# "3.3.3.3.3"
# l = 2
# ri = phi**2/sqrt(3)
# ru = sqrt(2+phi)
icosahedron = make_polyhedron(
    map_by(
        [[Vec(1,0,phi), Vec(0,phi,1), Vec(-1,0,phi)]],
        (e, ixy), (e, iyz), (e, xyz, zyx)
    )+map_by(
        [[Vec(1,0,phi), Vec(phi,1,0), Vec(0,phi,1)]],
        (e, ix), (e, iy), (e, iz)
    ))
poly["3.3.3.3.3"] = icosahedron

# "5.5.5"
# l = 2/phi
# ri = phi/sqrt(3-phi)
# ru = sqrt(3)
dodecahedron = make_polyhedron(
    map_by(
        [[Vec(0,1/phi,phi), Vec(0,-1/phi,phi), Vec(1,-1,1), Vec(phi,0,1/phi), Vec(1,1,1)]],
        (e, ixy), (e, izx), (e, xyz, zyx)
    ))
poly["5.5.5"] = dodecahedron


# "V3.4.3.4"
# l = sqrt(3)
# ri = sqrt(2)
# ru = 2
rhombicDodecahedron = make_polyhedron(
    map_by(
        [[Vec(0,0,2), Vec(1,1,1), Vec(0,2,0), Vec(-1,1,1)]],
        (e, ixy), (e, iyz), (e, xyz, zyx)
    ))
poly["V3.4.3.4"] = rhombicDodecahedron

# "V3.5.3.5"
# l = sqrt(3-phi)
# ri = sqrt(1+phi)
# ru = sqrt(2+phi)
rhombicTriacontahedron = make_polyhedron(
    map_by(
        [[Vec(1,0,phi), Vec(0,1/phi,phi), Vec(-1,0,phi), Vec(0,-1/phi,phi)]],
        (e, izx), (e, xyz, zyx)
    )+map_by(
        [[Vec(1,0,phi), Vec(1,1,1), Vec(0,phi,1), Vec(0,1/phi,phi)]],
        (e, ix), (e, ixy), (e, iyz), (e, xyz, zyx)
    ))
poly["V3.5.3.5"] = rhombicTriacontahedron


# "3.4.3.4"
# l = sqrt(2)
# ri = 1
# ru = sqrt(2)
cuboctahedron = make_polyhedron(
    map_by(
        [[Vec(1,0,1), Vec(0,1,1), Vec(-1,0,1), Vec(0,-1,1)]],
        (e, iz), (e, xyz, zyx)
    )+map_by(
        [[Vec(1,0,1), Vec(1,1,0), Vec(0,1,1)]],
        (e, ix), (e, iy), (e, iz)
    ))
poly["3.4.3.4"] = cuboctahedron

# "3.5.3.5"
# l = 1
# ri = sqrt(4*phi+3)/sqrt(5)
# ru = phi
icosidodecahedron = make_polyhedron(
    map_by(
        [[Vec(0,0,phi), Vec(0.5,-phi/2,(1+phi)/2), Vec((1+phi)/2,-0.5,phi/2), Vec((1+phi)/2,0.5,phi/2), Vec(0.5,phi/2,(1+phi)/2)]],
        (e, ixy), (e, izx), (e, xyz, zyx)
    )+map_by(
        [[Vec(0,0,phi), Vec(0.5,phi/2,(1+phi)/2), Vec(-0.5,phi/2,(1+phi)/2)]],
        (e, ixy), (e, izx), (e, xyz, zyx)
    )+map_by(
        [[Vec(0.5,phi/2,(1+phi)/2), Vec((1+phi)/2,0.5,phi/2), Vec(phi/2,(1+phi)/2,0.5)]],
        (e, ix), (e, iy), (e, iz)
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
        (e, iz), (e, xyz, zyx)
    )+map_by(
        [[Vec(1,1,c), Vec(1,c,1), Vec(-1,c,1), Vec(-1,1,c)]],
        (e, iy), (e, iz), (e, xyz, zyx)
    )+map_by(
        [[Vec(1,1,c), Vec(c,1,1), Vec(1,c,1)]],
        (e, ix), (e, iy), (e, iz)
    ))
poly["3.4.4.4"] = rhombicuboctahedron

# "3.4.5.4"
# l = 2
# ri = 3*sqrt((4*phi+3)/5)
# ru = sqrt(8*phi+7)
rhombicosidodecahedron = make_polyhedron(
    map_by(
        [[Vec(1,1,phi**3), Vec(1,-1,phi**3), Vec(phi**2,-phi,phi*2), Vec(2+phi,0,phi**2), Vec(phi**2,phi,phi*2)]],
        (e, ix), (e, iz), (e, xyz, zyx)
    )+map_by(
        [[Vec(phi,phi*2,phi**2), Vec(phi*2,phi**2,phi), Vec(phi**2,phi,phi*2)]],
        (e, ix), (e, iy), (e, iz)
    )+map_by(
        [[Vec(1,1,phi**3), Vec(-1,1,phi**3), Vec(-1,-1,phi**3), Vec(1,-1,phi**3)]],
        (e, iz), (e, xyz, zyx)
    )+map_by(
        [[Vec(1,1,phi**3), Vec(0,phi**2,2+phi), Vec(-1,1,phi**3)]],
        (e, iy), (e, iz), (e, xyz, zyx)
    )+map_by(
        [[Vec(1,1,phi**3), Vec(phi**2,phi,phi*2), Vec(phi,phi*2,phi**2), Vec(0,phi**2,2+phi)]],
        (e, ix), (e, iy), (e, iz), (e, xyz, zyx)
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
        (e, iyz), (e, xyz, zyx)
    )+map_by(
        [[Vec(1,1/t,t), Vec(t,1,1/t), Vec(1/t,t,1)]],
        (e, iyz), (e, xiy, ixy, yix)
    )+map_by(
        [[Vec(1,1/t,t), Vec(1/t,t,1), Vec(-1/t,1,t)]],
        (e, iyz), (e, xiy, ixy, yix), (e, xyz, zyx)
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
        (e, ixy), (e, izx), (e, xyz, zyx)
    )+map_by(
        [[v1, ixy(v1), v2]],
        (e, ixy), (e, izx), (e, xyz, zyx)
    )+map_by(
        [[v1, xyz(v4), ixy(v2)]],
        (e, ixy), (e, izx), (e, xyz, zyx)
    )+map_by(
        [[v1, v5, xyz(v4)]],
        (e, ixy), (e, izx), (e, xyz, zyx)
    )+map_by(
        [[v5, xyz(v5), xyz(v4)]],
        (e, ixy), (e, izx), (e, xyz, zyx)
    )+map_by(
        [[v5, zyx(v5), xyz(v5)]],
        (e, ixy), (e, izx)
    )+map_by(
        [[ixy(v2), xyz(v4), xyz(v3)]],
        (e, ixy), (e, izx), (e, xyz, zyx)
    )+map_by(
        [[ixy(v2), xyz(v3), ixy(v3)]],
        (e, ixy), (e, izx), (e, xyz, zyx)
    )+map_by(
        [[ixy(v3), xyz(v3), zyx(iyz(v3))]],
        (e, ixy), (e, izx)
    ))
poly["3.3.3.3.5"] = snubDodecahedron

