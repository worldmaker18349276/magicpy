import math
import FreeCAD, Part
from Geometric.Basic import fuzzyCompare, k2d, k, o


viewbox = {
    # maximum bound box
    mbb:    FreeCAD.BoundBox(-1.5,-1.5,-1.5, 1.5, 1.5, 1.5),
    margin: 1e-03
}

makeBox = Part.makeBox
makeCone = Part.makeCone
makeCylinder = Part.makeCylinder
makeSphere = Part.makeSphere

def makeConicalFrustum(radius1=0., radius2=1., pnt=o, axis=k):
    height = axis.Length
    if fuzzyCompare(radius1, radius2):
        return Part.makeCylinder(abs(radius1), height, pnt, axis)

    elif radius1*radius2 >= 0:
        return Part.makeCone(abs(radius1), abs(radius2), height, pnt, axis)

    else:
        axis1 = axis*abs(float(radius1)/(radius1-radius2))*(-1)
        axis2 = axis*abs(float(radius2)/(radius1-radius2))
        pnt0 = pnt - axis1
        shape1 = Part.makeCone(0, abs(radius1), axis1.Length, pnt0, axis1)
        shape2 = Part.makeCone(0, abs(radius2), axis2.Length, pnt0, axis2)
        return shape1.fuse(shape2)

def makeEmptySpace():
    return Part.Shape()

def makeWholeSpace():
    return Part.makeSphere(viewbox.mbb.DiagonalLength/2 + viewbox.margin, viewbox.mbb.Center)

def makeHalfspace(direction=k, offset=0.):
    mbb_ = viewbox.mbb.transformed(k2d(direction).inverse().toMatrix())
    height = max(mbb_.ZMax - offset + viewbox.margin, viewbox.margin)
    xm = max(abs(mbb_.XMax), abs(mbb_.XMin))
    ym = max(abs(mbb_.YMax), abs(mbb_.YMin))
    radius = math.sqrt(xm**2 + ym**2) + viewbox.margin
    return Part.makeCylinder(radius, height, direction*offset, direction)

def makeInfiniteCylinder(radius=1., direction=k, center=o):
    mbb_ = viewbox.mbb.transformed(k2d(direction).inverse().toMatrix())
    offset = center.dot(direction)*(1./direction.Length)
    height = mbb_.ZLength + 2*viewbox.margin
    bottom = center - direction*((offset+height/2.)/direction.Length)
    return makeCylinder(abs(radius), height, bottom, direction)

def makeSemiInfiniteCone(slope=1., direction=k, center=o):
    mbb_ = viewbox.mbb.transformed(k2d(direction).inverse().toMatrix())
    offset = center.dot(direction)*(1./direction.Length)
    height = max(mbb_.ZMax - offset + viewbox.margin, viewbox.margin)
    return makeCone(0., abs(slope*height), height, center, direction)
