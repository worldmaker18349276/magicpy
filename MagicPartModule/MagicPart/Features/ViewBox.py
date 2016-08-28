import FreeCAD, Part
from MagicPart.Features.Utilities import *


def getViewBox(doc=None, init_if_absent=True):
    if doc is None:
        doc = FreeCAD.ActiveDocument
    vb = doc.getObject("ViewBox")
    if init_if_absent and vb is None:
        vb = initViewBox(doc=doc)
    return vb

def initViewBox(doc=None):
    vb = addObject("Part::Box", "ViewBox", doc=doc, cached=False)
    vb.ViewObject.Visibility = False
    vb.ViewObject.Selectable = False
    vb.ViewObject.DisplayMode = "Wireframe"
    vb.ViewObject.DrawStyle = "Dashed"
    vb.ViewObject.DiffuseColor = [(1., 1., 1., 1.)]*6
    vb.ViewObject.LineColor = (1., 0., 0.)

    R = 10.
    mbb = FreeCAD.BoundBox(FreeCAD.Vector(-R,-R,-R), FreeCAD.Vector(R,R,R))
    return setMaxBoundBox(vb, mbb)

def setMaxBoundBox(vb, mbb, enlarged=True):
    mbb = FreeCAD.BoundBox(mbb)

    if enlarged:
        mbb.add(boundBoxOf(vb))

    vb.Length = mbb.XLength
    vb.Width = mbb.YLength
    vb.Height = mbb.ZLength
    vb.Placement = FreeCAD.Placement(mbb.getPoint(4), FreeCAD.Rotation())
    return vb


def isBounded(obj):
    if not isDerivedFrom(obj, "App::GeoFeature"):
        return True
    vb = getViewBox(doc=obj.Document, init_if_absent=False)
    if vb is None:
        return True
    if obj == vb:
        return False
    if not isDependOn(obj, vb):
        return True

    return boundBoxOf(vb).isInside(boundBoxOf(obj))



def fitBounded(vb, enlarged=True, margin=1e-03):
    bb = FreeCAD.BoundBox()
    for ftr in vb.Document.Objects:
        if isBounded(ftr):
            bb.add(boundBoxOf(ftr))
    bb.enlarge(margin)
    return setMaxBoundBox(vb, bb, enlarged=enlarged)

def fitFeatures(vb, ftrs, enlarged=True, margin=1e-03):
    bb = FreeCAD.BoundBox()
    for ftr in ftrs:
        bb.add(boundBoxOf(ftr))
    bb.enlarge(margin)
    return setMaxBoundBox(vb, bb, enlarged=enlarged)

