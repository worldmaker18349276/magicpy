import FreeCAD
from Geometric.Features.Utilities import *


def isTouched(obj):
    if obj is None:
        return False
    return "Touched" in obj.State or any(isTouched(outobj) for outobj in obj.OutList)

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
    if forced or isTouched(obj):
        if not isDerivedFrom(obj, ("Part::FeaturePython", "Mesh::FeaturePython")):
            return False
        if not all(weakRecomputable(outobj, forced=forced) for outobj in obj.OutList):
            return False
    return True

def weakRecompute(obj, forced=False):
    if forced or isTouched(obj):
        for outobj in obj.OutList:
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

