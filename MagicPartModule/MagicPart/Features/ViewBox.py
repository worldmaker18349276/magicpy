import FreeCAD
from MagicPart.Features.Utilities import *


def getViewBox(doc=None, init_if_absent=True):
    if doc is None:
        doc = FreeCAD.ActiveDocument
    vb = doc.getObject("ViewBox")
    if init_if_absent and vb is None:
        vb = initViewBox(doc=doc)
    return vb

def initViewBox(doc=None):
    vb = addObject("Part::Box", "ViewBox", parent=doc, cached=False)
    vb.ViewObject.Visibility = False
    vb.ViewObject.Selectable = False
    vb.ViewObject.DisplayMode = "Wireframe"
    vb.ViewObject.DrawStyle = "Dashed"
    vb.ViewObject.DiffuseColor = [(1., 1., 1., 1.)]*6
    vb.ViewObject.LineColor = (1., 0., 0.)

    return fitBounded(vb)

def setViewBox(vb, mbb):
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


def fitBounded(vb, ftrs=None, R=1., margin=0.5):
    if ftrs is None:
        ftrs = vb.Document.Objects
    mbb = FreeCAD.BoundBox(FreeCAD.Vector(-R,-R,-R), FreeCAD.Vector(R,R,R))
    for ftr in ftrs:
        if isBounded(ftr):
            mbb.add(boundBoxOf(ftr))
    mbb.enlarge(margin)
    return setViewBox(vb, mbb)


def hideAllUnbounded():
    for obj in FreeCAD.ActiveDocument.Objects:
        if not isBounded(obj):
            obj.ViewObject.hide()

def viewAllBounded():
    import FreeCADGui
    unbounded = set()
    for obj in FreeCAD.ActiveDocument.Objects:
        if obj.ViewObject.Visibility and not isBounded(obj):
            unbounded.add(obj)

    for obj in unbounded:
        obj.ViewObject.hide()
    FreeCADGui.SendMsgToActiveView("ViewFit")
    for obj in unbounded:
        obj.ViewObject.show()

def viewBoundedSelections():
    import FreeCADGui
    unbounded = set()
    for obj in set(FreeCADGui.Selection.getSelection()):
        if obj.ViewObject.Visibility and not isBounded(obj):
            unbounded.add(obj)

    for obj in unbounded:
        obj.ViewObject.hide()
    FreeCADGui.SendMsgToActiveView("ViewSelection")
    for obj in unbounded:
        obj.ViewObject.show()

