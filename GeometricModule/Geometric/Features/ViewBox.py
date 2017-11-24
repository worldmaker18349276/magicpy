import FreeCAD, Part
from Geometric.Basic import *
from Geometric.Features.Utilities import *


class ViewBoxProxy(ScriptedObjectProxy):
    def __init__(self, obj):
        obj.Proxy = self
        if "Min" not in obj.PropertiesList:
            obj.addProperty("App::PropertyVector", "Min")
            obj.Min = Vec(-1.5,-1.5,-1.5)
        if "Max" not in obj.PropertiesList:
            obj.addProperty("App::PropertyVector", "Max")
            obj.Max = Vec( 1.5, 1.5, 1.5)
        if "Margin" not in obj.PropertiesList:
            obj.addProperty("App::PropertyFloat", "Margin")
            obj.Margin = 0.01
        obj.setEditorMode("Placement", 2)

        if FreeCAD.GuiUp:
            ViewBoxViewProxy(obj.ViewObject)

    def execute(self, obj):
        V = obj.Max - obj.Min
        if V.x <= 0 or V.y <= 0 or V.z <= 0:
            setGeometry(obj, Part.Shape())
        else:
            setGeometry(obj, Part.makeBox(V.x, V.y, V.z, obj.Min))

    def getBoundBox(self, obj):
        return FreeCAD.BoundBox(obj.Min, obj.Max)

    def setBoundBox(self, obj, bb):
        obj.Min = bb.getPoint(4)
        obj.Max = bb.getPoint(2)

    def fit(self, obj, ftrs=[]):
        bb = self.getBoundBox(obj)
        for ftr in ftrs:
            bb.add(boundBoxOf(ftr))
        bb.enlarge(obj.Margin)
        self.setBoundBox(obj, bb)

class ViewBoxViewProxy(object):
    def getIcon(self):
        return ""

    def __init__(self, view):
        view.Proxy = self
        view.Visibility = False
        view.Selectable = False
        view.DisplayMode = "Wireframe"
        view.DrawStyle = "Dashed"
        view.DiffuseColor = [(1., 1., 1., 1.)]*6
        view.LineColor = (1., 0., 0.)

ViewBox = ViewBoxProxy


def getViewBox(doc=None, init_if_absent=True):
    if doc is None:
        doc = FreeCAD.ActiveDocument
    vb = doc.getObject("ViewBox")
    if init_if_absent and vb is None:
        vb = doc.addObject("Part::FeaturePython", "ViewBox")
        ViewBox(vb)
    return vb

def isBounded(obj):
    vb = getViewBox(doc=obj.Document, init_if_absent=False)
    return obj == vb or len(obj.getPathsByOutList(vb)) > 0
    # return boundBoxOf(vb).isInside(boundBoxOf(obj))


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

