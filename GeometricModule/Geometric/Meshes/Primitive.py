import math
import FreeCAD, Mesh
from Geometric.Basic import fuzzyCompare, o, k, bb
from Geometric.Meshes.Operation import complement, common, fuse, transform


def i2d(c, d):
    return Plc(c, FreeCAD.Rotation(Vec(1,0,0),d))

def makeSphere(radius=1., center=o, bb=bb, fn=50):
    mesh = Mesh.createSphere(radius, int(fn))
    mesh.Placement = i2d(o, k)
    return mesh

def makeConicalFrustum(radius1=0., radius2=1., center=o, axis=k, bb=bb, fn=50):
    height = axis.Length
    if fuzzyCompare(radius1, radius2):
        mesh = Mesh.createCylinder(abs(radius1), height, 1, 0.5/fn, int(fn))
        mesh.transform(i2d(center,axis).toMatrix())
        return mesh

    elif radius1*radius2 >= 0:
        mesh = Mesh.createCone(abs(radius1), abs(radius2), height, 1, 0.5/fn, int(fn))
        mesh.transform(i2d(center,axis).toMatrix())
        return mesh

    else:
        axis1 = axis*abs(float(radius1)/(radius1-radius2))*(-1)
        axis2 = axis*abs(float(radius2)/(radius1-radius2))
        center0 = center - axis1
        mesh1 = Mesh.createCone(0, abs(radius1), height1, 1, 0.5/fn, int(fn))
        mesh1.transform(i2d(center,axis1).toMatrix())
        mesh2 = Mesh.createCone(0, abs(radius2), height2, 1, 0.5/fn, int(fn))
        mesh2.transform(i2d(center0,axis2).toMatrix())
        mesh = mesh1.unite(mesh2)
        return mesh

def makeEmptySpace(bb=bb, fn=50):
    return Mesh.Mesh()

def makeWholeSpace(bb=bb, fn=50):
    mesh = Mesh.createSphere(bb.DiagonalLength/2, int(fn))
    mesh.translate(*bb.Center)
    return mesh

def makeHalfspace(direction=k, offset=0., bb=bb, fn=50):
    bb_ = bb.transformed(k2d(direction).inverse().toMatrix())
    height = max(bb_.ZMax - offset, 0.01)
    xm = max(abs(bb_.XMax), abs(bb_.XMin))
    ym = max(abs(bb_.YMax), abs(bb_.YMin))
    radius = math.sqrt(xm**2 + ym**2)
    mesh = Mesh.createCylinder(radius, height, 1, 0.5/fn, int(fn))
    mesh.transform(i2d(direction*offset, direction).toMatrix())
    return mesh

def makeInfiniteCylinder(radius=1., direction=k, center=o, bb=bb, fn=50):
    bb_ = bb.transformed(k2d(direction).inverse().toMatrix())
    offset = center.dot(direction)*(1./direction.Length)
    height = bb_.ZLength
    bottom = center - direction*((offset+height/2.)/direction.Length)
    mesh = Mesh.createCylinder(abs(radius), height, 1, 0.5/fn, int(fn))
    mesh.transform(i2d(bottom, direction).toMatrix())
    return mesh

def makeSemiInfiniteCone(slope=1., direction=k, center=o, bb=bb, fn=50):
    bb_ = bb.transformed(k2d(direction).inverse().toMatrix())
    offset = center.dot(direction)*(1./direction.Length)
    height = max(bb_.ZMax - offset, 0.01)
    mesh = Mesh.createCone(0., abs(slope*height), height, 1, 0.5/fn, int(fn))
    mesh.transform(i2d(center, direction).toMatrix())
    return mesh
