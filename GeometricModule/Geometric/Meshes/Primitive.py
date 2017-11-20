import math
import FreeCAD, Mesh
from Geometric.Basic import fuzzyCompare, o, k, viewbox
from Geometric.Meshes.Operation import complement, common, fuse, transform

fn = 50

def i2d(c, d):
    return Plc(c, FreeCAD.Rotation(Vec(1,0,0),d))

def makeSphere(radius=1., center=o):
    mesh = Mesh.createSphere(radius, int(fn))
    mesh.Placement = i2d(o, k)
    return mesh

def makeConicalFrustum(radius1=0., radius2=1., pnt=o, axis=k):
    height = axis.Length
    if fuzzyCompare(radius1, radius2):
        mesh = Mesh.createCylinder(abs(radius1), height, 1, 0.5/fn, int(fn))
        mesh.transform(i2d(pnt,axis).toMatrix())
        return mesh

    elif radius1*radius2 >= 0:
        mesh = Mesh.createCone(abs(radius1), abs(radius2), height, 1, 0.5/fn, int(fn))
        mesh.transform(i2d(pnt,axis).toMatrix())
        return mesh

    else:
        axis1 = axis*abs(float(radius1)/(radius1-radius2))*(-1)
        axis2 = axis*abs(float(radius2)/(radius1-radius2))
        pnt0 = pnt - axis1
        mesh1 = Mesh.createCone(0, abs(radius1), height1, 1, 0.5/fn, int(fn))
        mesh1.transform(i2d(pnt,axis1).toMatrix())
        mesh2 = Mesh.createCone(0, abs(radius2), height2, 1, 0.5/fn, int(fn))
        mesh2.transform(i2d(pnt0,axis2).toMatrix())
        mesh = mesh1.unite(mesh2)
        return mesh

def makeEmptySpace():
    return Mesh.Mesh()

def makeWholeSpace():
    mesh = Mesh.createSphere(viewbox.mbb.DiagonalLength/2 + viewbox.margin, int(fn))
    mesh.translate(*viewbox.mbb.Center)
    return mesh

def makeHalfspace(direction=k, offset=0.):
    mbb_ = viewbox.mbb.transformed(k2d(direction).inverse().toMatrix())
    height = max(mbb_.ZMax - offset + viewbox.margin, viewbox.margin)
    xm = max(abs(mbb_.XMax), abs(mbb_.XMin))
    ym = max(abs(mbb_.YMax), abs(mbb_.YMin))
    radius = math.sqrt(xm**2 + ym**2) + viewbox.margin
    mesh = Mesh.createCylinder(radius, height, 1, 0.5/fn, int(fn))
    mesh.transform(i2d(direction*offset, direction).toMatrix())
    return mesh

def makeInfiniteCylinder(radius=1., direction=k, center=o):
    mbb_ = viewbox.mbb.transformed(k2d(direction).inverse().toMatrix())
    offset = center.dot(direction)*(1./direction.Length)
    height = mbb_.ZLength + 2*viewbox.margin
    bottom = center - direction*((offset+height/2.)/direction.Length)
    mesh = Mesh.createCylinder(abs(radius), height, 1, 0.5/fn, int(fn))
    mesh.transform(i2d(bottom, direction).toMatrix())
    return mesh

def makeSemiInfiniteCone(slope=1., direction=k, center=o):
    mbb_ = viewbox.mbb.transformed(k2d(direction).inverse().toMatrix())
    offset = center.dot(direction)*(1./direction.Length)
    height = max(mbb_.ZMax - offset + viewbox.margin, viewbox.margin)
    mesh = Mesh.createCone(0., abs(slope*height), height, 1, 0.5/fn, int(fn))
    mesh.transform(i2d(center, direction).toMatrix())
    return mesh
