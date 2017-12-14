from math import sqrt
from Geometric.Basic import *
import Part


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
ie   = istar(lambda v: v)
xy   = istar(lambda v: Vec( v.y, v.x, v.z))
yz   = istar(lambda v: Vec( v.x, v.z, v.y))
zx   = istar(lambda v: Vec( v.z, v.y, v.x))
xyz  =  star(lambda v: Vec( v.y, v.z, v.x))
zyx  =  star(lambda v: Vec( v.z, v.x, v.y))
ix   = istar(lambda v: Vec(-v.x, v.y, v.z))
iy   = istar(lambda v: Vec( v.x,-v.y, v.z))
iz   = istar(lambda v: Vec( v.x, v.y,-v.z))
ixy  =  star(lambda v: Vec(-v.x,-v.y, v.z))
izx  =  star(lambda v: Vec(-v.x, v.y,-v.z))
iyz  =  star(lambda v: Vec( v.x,-v.y,-v.z))
ixyz = istar(lambda v: Vec(-v.x,-v.y,-v.z))
xiy  =  star(lambda v: Vec(-v.y, v.x, v.z))
yiz  =  star(lambda v: Vec( v.x,-v.z, v.y))
zix  =  star(lambda v: Vec( v.z, v.y,-v.x))
yix  =  star(lambda v: Vec( v.y,-v.x, v.z))
ziy  =  star(lambda v: Vec( v.x, v.z,-v.y))
xiz  =  star(lambda v: Vec(-v.z, v.y, v.x))

class polybuilder(list):
    def face(self, *vs):
        self.append([Vec(*v) for v in vs])
        return self

    def dup(self, *ops):
        self[:] = [op(*f) for op in ops for f in self]
        return self

    def __add__(self, builder):
        obj = polybuilder()
        obj[:] = list.__add__(self, builder)
        return obj

    def make(self):
        faces = []
        for vs in self:
            faces.append(Part.Face(Part.makePolygon(vs+vs[:1])))
        return Part.makeSolid(Part.makeShell(faces))

phi = (sqrt(5)+1)/2

poly = {}


def inradius(shp):
    return shp.Shells[0].distToShape(Part.Vertex(FreeCAD.Vector()))[0]

def circumradius(shp):
    return max(v.Point.Length for v in shp.Vertexes)

def edge_length(shp):
    ls = []
    for e in shp.Edges:
        if all(not fuzzyCompare(l, e.Length) for l in ls):
            ls.append(e.Length)
    return ls

