from math import sqrt, pow
from Geometric.Basic import *
from Geometric.Polyhedrons.Utilities import *


# "3.3.3"
# l = 2*sqrt(2)
# ri = 1/sqrt(3)
# ru = sqrt(3)
# rm = 1.
poly["3.3.3"] = tetrahedron = \
    polybuilder().face((-1,1,1), (1,-1,1), (1,1,-1)) \
    .dup(e, ixy).dup(e, izx).make()


# "4.4.4"
# l = 2.
# ri = 1.
# ru = sqrt(3)
# rm = sqrt(2)
poly["4.4.4"] = cube = \
    polybuilder().face((1,1,1), (-1,1,1), (-1,-1,1), (1,-1,1)) \
    .dup(e, iz).dup(e, xyz, zyx).make()

# "3.3.3.3"
# l = 2*sqrt(2)
# ri = 2/sqrt(3)
# ru = 2.
# rm = sqrt(2)
poly["3.3.3.3"] = octahedron = \
    polybuilder().face((2,0,0), (0,2,0), (0,0,2)) \
    .dup(e, ix).dup(e, iy).dup(e, iz).make()

# "3.4.3.4"
# l = sqrt(2)
# ri = 1
# ru = sqrt(2)
poly["3.4.3.4"] = cuboctahedron = \
    (
        polybuilder().face((1,0,1), (0,1,1), (-1,0,1), (0,-1,1)) \
        .dup(e, iz).dup(e, xyz, zyx) \
        + polybuilder().face((1,0,1), (1,1,0), (0,1,1)) \
        .dup(e, ix).dup(e, iy).dup(e, iz)
    ).make()

# "V3.4.3.4"
# l = sqrt(3)
# ri = sqrt(2)
# ru = 2.
poly["V3.4.3.4"] = rhombicDodecahedron = \
    polybuilder().face((0,0,2), (1,1,1), (0,2,0), (-1,1,1)) \
    .dup(e, ixy).dup(e, iyz).dup(e, xyz, zyx).make()


# "5.5.5"
# l = 2/phi
# ri = phi/sqrt(3-phi)
# ru = sqrt(3)
# rm = phi
poly["5.5.5"] = dodecahedron = \
    polybuilder().face((0,1/phi,phi), (0,-1/phi,phi), (1,-1,1), (phi,0,1/phi), (1,1,1)) \
    .dup(e, ixy).dup(e, izx).dup(e, xyz, zyx).make()

# "3.3.3.3.3"
# l = 2.
# ri = phi**2/sqrt(3)
# ru = sqrt(2+phi)
# rm = phi
poly["3.3.3.3.3"] = icosahedron = \
    (
        polybuilder().face((1,0,phi), (0,phi,1), (-1,0,phi)) \
        .dup(e, ixy).dup(e, iyz).dup(e, xyz, zyx) \
        + polybuilder().face((1,0,phi), (phi,1,0), (0,phi,1)) \
        .dup(e, ix).dup(e, iy).dup(e, iz)
    ).make()

# "3.5.3.5"
# l = 1
# ri = sqrt(4*phi+3)/sqrt(5)
# ru = phi
poly["3.5.3.5"] = icosidodecahedron = \
    (
        polybuilder().face((0,0,phi), (0.5,-phi/2,(1+phi)/2), ((1+phi)/2,-0.5,phi/2), ((1+phi)/2,0.5,phi/2), (0.5,phi/2,(1+phi)/2)) \
        .dup(e, ixy).dup(e, izx).dup(e, xyz, zyx) \
        + polybuilder().face((0,0,phi), (0.5,phi/2,(1+phi)/2), (-0.5,phi/2,(1+phi)/2)) \
        .dup(e, ixy).dup(e, izx).dup(e, xyz, zyx) \
        + polybuilder().face((0.5,phi/2,(1+phi)/2), ((1+phi)/2,0.5,phi/2), (phi/2,(1+phi)/2,0.5)) \
        .dup(e, ix).dup(e, iy).dup(e, iz)
    ).make()

# "V3.5.3.5"
# l = sqrt(3-phi)
# ri = phi
# ru = sqrt(2+phi)
poly["V3.5.3.5"] = rhombicTriacontahedron = \
    (
        polybuilder().face((1,0,phi), (0,1/phi,phi), (-1,0,phi), (0,-1/phi,phi)) \
        .dup(e, izx).dup(e, xyz, zyx) \
        + polybuilder().face((1,0,phi), (1,1,1), (0,phi,1), (0,1/phi,phi)) \
        .dup(e, ix).dup(e, ixy).dup(e, iyz).dup(e, xyz, zyx)
    ).make()



c = 1+sqrt(2)
# "3.4.4.4"
# l = 2
# ri = c
# ru = sqrt(3+2*c)
poly["3.4.4.4"] = rhombicuboctahedron = \
    (
        polybuilder().face((1,1,c), (-1,1,c), (-1,-1,c), (1,-1,c)) \
        .dup(e, iz).dup(e, xyz, zyx) \
        + polybuilder().face((1,1,c), (1,c,1), (-1,c,1), (-1,1,c)) \
        .dup(e, iy).dup(e, iz).dup(e, xyz, zyx) \
        + polybuilder().face((1,1,c), (c,1,1), (1,c,1)) \
        .dup(e, ix).dup(e, iy).dup(e, iz)
    ).make()

# "3.4.5.4"
# l = 2
# ri = 3*sqrt((4*phi+3)/5)
# ru = sqrt(8*phi+7)
poly["3.4.5.4"] = rhombicosidodecahedron = \
    (
        polybuilder().face((1,1,phi**3), (1,-1,phi**3), (phi**2,-phi,phi*2), (2+phi,0,phi**2), (phi**2,phi,phi*2)) \
        .dup(e, ix).dup(e, iz).dup(e, xyz, zyx) \
        + polybuilder().face((phi,phi*2,phi**2), (phi*2,phi**2,phi), (phi**2,phi,phi*2)) \
        .dup(e, ix).dup(e, iy).dup(e, iz) \
        + polybuilder().face((1,1,phi**3), (-1,1,phi**3), (-1,-1,phi**3), (1,-1,phi**3)) \
        .dup(e, iz).dup(e, xyz, zyx) \
        + polybuilder().face((1,1,phi**3), (0,phi**2,2+phi), (-1,1,phi**3)) \
        .dup(e, iy).dup(e, iz).dup(e, xyz, zyx) \
        + polybuilder().face((1,1,phi**3), (phi**2,phi,phi*2), (phi,phi*2,phi**2), (0,phi**2,2+phi)) \
        .dup(e, ix).dup(e, iy).dup(e, iz).dup(e, xyz, zyx)
    ).make()


t = (1+pow(19+3*sqrt(33), 1/3.)+pow(19-3*sqrt(33), 1/3.))/3
# "3.3.3.3.4"
# l = sqrt(2/t**2+2)
# ri = t
# ru = sqrt(1+2*t)
poly["3.3.3.3.4"] = snubCube = \
    (
        polybuilder().face((1,1/t,t), (-1/t,1,t), (-1,-1/t,t), (1/t,-1,t)) \
        .dup(e, iyz).dup(e, xyz, zyx) \
        + polybuilder().face((1,1/t,t), (t,1,1/t), (1/t,t,1)) \
        .dup(e, iyz).dup(e, xiy, ixy, yix) \
        + polybuilder().face((1,1/t,t), (1/t,t,1), (-1/t,1,t)) \
        .dup(e, iyz).dup(e, xiy, ixy, yix).dup(e, xyz, zyx)
    ).make()

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
poly["3.3.3.3.5"] = snubDodecahedron = \
    (
        polybuilder() \
        .face(v1,v2,v3,v4,v5) \
        .face(v1, ixy(v1), v2) \
        .face(v1, xyz(v4), ixy(v2)) \
        .face(v1, v5, xyz(v4)) \
        .face(v5, xyz(v5), xyz(v4)) \
        .face(ixy(v2), xyz(v4), xyz(v3)) \
        .face(ixy(v2), xyz(v3), ixy(v3)) \
        .dup(e, ixy).dup(e, izx).dup(e, xyz, zyx) \
        + polybuilder() \
        .face(v5, zyx(v5), xyz(v5)) \
        .face(ixy(v3), xyz(v3), zyx(iyz(v3))) \
        .dup(e, ixy).dup(e, izx)
    ).make()

