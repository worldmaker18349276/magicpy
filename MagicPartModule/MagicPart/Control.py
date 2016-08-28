import FreeCAD, FreeCADGui
from MagicPart.Features.Utilities import *
from MagicPart.Features.ViewBox import isBounded
from MagicPart.Features.BooleanTracing import outOf, outFaceLinksOf


def hideAllUnbounded():
    for obj in FreeCAD.ActiveDocument.Objects:
        if not isBounded(obj):
            obj.ViewObject.hide()

def viewAllBounded():
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
    unbounded = set()
    for obj in set(FreeCADGui.Selection.getSelection()):
        if obj.ViewObject.Visibility and not isBounded(obj):
            unbounded.add(obj)

    for obj in unbounded:
        obj.ViewObject.hide()
    FreeCADGui.SendMsgToActiveView("ViewSelection")
    for obj in unbounded:
        obj.ViewObject.show()


def forceTouch(obj):
    bop = ("Part::Fuse", "Part::Common", "Part::Cut", "Part::MultiFuse", "Part::MultiCommon")
    plink = ["App::PropertyLink", "App::PropertyLinkList"]
    if isDerivedFrom(obj, bop):
        for p in obj.PropertiesList:
            if obj.getTypeIdOfProperty(p) in plink:
                setattr(obj, p, getattr(obj, p))
                break
        else:
            raise RuntimeError("can't touch %s"%obj.Name)
    else:
        obj.touch()

def retouch(objs):
    for obj in objs:
        if isTouched(obj):
            forceTouch(obj)


def weakRecomputable(obj, forced=False):
    if isTouched(obj) or forced:
        if not isDerivedFrom(obj, ("Part::FeaturePython", "Mesh::FeaturePython")):
            return False
        if not all(weakRecomputable(outobj, forced=forced) for outobj in ftrlist(obj.OutList)):
            return False
    return True

def weakRecompute(obj, forced=False):
    if isTouched(obj) or forced:
        for outobj in ftrlist(obj.OutList):
            weakRecompute(outobj, forced=forced)
        obj.Proxy.execute(obj)
        obj.purgeTouched()

def recompute(targets, forced=False):
    targets = list(targets)
    if len(targets) == 0:
        return

    elif all(weakRecomputable(target, forced=forced) for target in targets):
        retouch(targets[0].Document.Objects)
        for target in targets:
            weakRecompute(target, forced=forced)

    else:
        untouched = []
        for obj in FreeCAD.ActiveDocument.Objects:
            if "Touched" in obj.State:
                if not any(isDependOn(target, obj) for target in targets):
                    untouched.append(obj)
                    obj.purgeTouched()
                elif forced:
                    obj.touch()

        FreeCAD.ActiveDocument.recompute()

        for obj in untouched:
            obj.touch()


def getSubSelection():
    sobjs = FreeCADGui.Selection.getSelectionEx()
    subsel = []
    for sobj in sobjs:
        if sobj.HasSubObjects:
            for field in sobj.SubElementNames:
                subsel.append((sobj.Object, field))

        else:
            subsel.append((sobj.Object, "Shape"))
    return subsel

def shiftToChildren():
    sobjs = FreeCADGui.Selection.getSelectionEx()
    FreeCADGui.Selection.clearSelection()
    for sobj in sobjs:
        if sobj.HasSubObjects:
            no_children = True
            for field, v in zip(sobj.SubElementNames, sobj.PickedPoints):
                outlink = outOf((sobj.Object, field))
                if outlink is not None:
                    no_children = False
                    FreeCADGui.Selection.addSelection(outlink[0], outlink[1], v.x, v.y, v.z)
            if no_children:
                FreeCADGui.Selection.addSelection(sobj.Object)

        else:
            if len(sobj.Object.OutList) == 0:
                FreeCADGui.Selection.addSelection(sobj.Object)
            for outobj in sobj.Object.OutList:
                FreeCADGui.Selection.addSelection(outobj)

