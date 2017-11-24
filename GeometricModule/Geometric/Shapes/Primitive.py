import math
import FreeCAD, Part
from Geometric.Basic import fuzzyCompare, k2d, o, k, bb


def makeSphere(radius=1., center=o, bb=bb):
    return Part.makeSphere(radius, center)

def makeConicalFrustum(radius1=0., radius2=1., center=o, axis=k, bb=bb):
    height = axis.Length
    if fuzzyCompare(radius1, radius2):
        return Part.makeCylinder(abs(radius1), height, center, axis)

    elif radius1*radius2 >= 0:
        return Part.makeCone(abs(radius1), abs(radius2), height, center, axis)

    else:
        axis1 = axis*abs(float(radius1)/(radius1-radius2))*(-1)
        axis2 = axis*abs(float(radius2)/(radius1-radius2))
        center0 = center - axis1
        shape1 = Part.makeCone(0, abs(radius1), axis1.Length, center0, axis1)
        shape2 = Part.makeCone(0, abs(radius2), axis2.Length, center0, axis2)
        return shape1.fuse(shape2)

def makeEmptySpace(bb=bb):
    return Part.Shape()

def makeWholeSpace(bb=bb):
    return Part.makeSphere(bb.DiagonalLength/2, bb.Center)

def makeHalfspace(direction=k, offset=0., bb=bb):
    bb_ = bb.transformed(k2d(direction).inverse().toMatrix())
    height = max(bb_.ZMax - offset, 0.01)
    xm = max(abs(bb_.XMax), abs(bb_.XMin))
    ym = max(abs(bb_.YMax), abs(bb_.YMin))
    radius = math.sqrt(xm**2 + ym**2)
    return Part.makeCylinder(radius, height, direction*offset, direction)

def makeInfiniteCylinder(radius=1., direction=k, center=o, bb=bb):
    bb_ = bb.transformed(k2d(direction).inverse().toMatrix())
    offset = center.dot(direction)*(1./direction.Length)
    height = bb_.ZLength
    bottom = center - direction*((offset+height/2.)/direction.Length)
    return Part.makeCylinder(abs(radius), height, bottom, direction)

def makeSemiInfiniteCone(slope=1., direction=k, center=o, bb=bb):
    bb_ = bb.transformed(k2d(direction).inverse().toMatrix())
    offset = center.dot(direction)*(1./direction.Length)
    height = max(bb_.ZMax - offset, 0.01)
    return Part.makeCone(0., abs(slope*height), height, center, direction)
