from itertools import product, imap, starmap, islice
from functools import wraps
import FreeCAD
from Geometric.Basic import *
from Geometric.Features.Utilities import *
from Geometric import Shapes, Meshes


class DerivedFeatureProxy(ScriptedObjectProxy):
    pass

class DerivedFeatureViewProxy(object):
    def __init__(self, view, icon=""):
        view.Proxy = self
        self.icon = icon
        self.children = []

    def getIcon(self):
        return self.icon

    def claimChildren(self):
        return self.children

    def updateData(self, obj, p):
        if obj.getTypeIdOfProperty(p) in ["App::PropertyLink", "App::PropertyLinkList"]:
            outlist = distinct_list(obj.OutList)
            for ftr in outlist:
                if ftr not in self.children:
                    ftr.ViewObject.hide()
            self.children = outlist

    def onDelete(self, obj, subelems):
        for ftr in self.children:
            ftr.ViewObject.show()
        return True

class ComplementProxy(DerivedFeatureProxy):
    def __init__(self, obj):
        obj.Proxy = self
        if "Source" not in obj.PropertiesList:
            obj.addProperty("App::PropertyLink", "Source")
        obj.setEditorMode("Placement", 2)
        if FreeCAD.GuiUp:
            DerivedFeatureViewProxy(obj.ViewObject, "Geometric_complement.png")

    def execute(self, obj):
        if isDerivedFrom(obj, "Part::FeaturePython"):
            setGeometry(obj, Shapes.complement(obj.Source.Shape))
            obj.ViewObject.DiffuseColor = obj.Source.ViewObject.DiffuseColor

        elif isDerivedFrom(obj, "Mesh::FeaturePython"):
            setGeometry(obj, Meshes.complement(meshOf(obj.Source)))

        else:
            raise TypeError

class TransformProxy(DerivedFeatureProxy):
    def __init__(self, obj):
        obj.Proxy = self
        if "Source" not in obj.PropertiesList:
            obj.addProperty("App::PropertyLink", "Source")
        if "Placements" not in obj.PropertiesList:
            obj.addProperty("App::PropertyLinkList", "Placements")
        obj.setEditorMode("Placement", 2)
        if FreeCAD.GuiUp:
            TransformViewProxy(obj.ViewObject)

    def execute(self, obj):
        plcs = [ftr.Placement for ftr in obj.Placements]
        if isDerivedFrom(obj, "Part::FeaturePython"):
            setGeometry(obj, Shapes.transform(obj.Source.Shape, *plcs))
            obj.ViewObject.DiffuseColor = obj.Source.ViewObject.DiffuseColor

        elif isDerivedFrom(obj, "Mesh::FeaturePython"):
            setGeometry(obj, Meshes.transform(meshOf(obj.Source), *plcs))

        else:
            raise TypeError

class TransformViewProxy(object):
    def __init__(self, view):
        view.Proxy = self
        self.children = []

    def getIcon(self):
        return "Geometric_transform.png"

    def claimChildren(self):
        return self.children

    def updateData(self, obj, p):
        if p in ["Source", "Placements"]:
            prop = obj.getPropertyByName(p)
            if prop is not None:
                if p == "Source":
                    prop.ViewObject.hide()
                elif p == "Placements":
                    for ftr in prop:
                        ftr.ViewObject.hide()
            self.children = [obj.Source] + list(obj.Placements)

    def onDelete(self, obj, subelems):
        for ftr in self.children:
            ftr.ViewObject.show()
        return True

Complement = ComplementProxy
Transform = TransformProxy


def common(*ftrs, **kw):
    ftrs = distinct_list(subftr for ftr in ftrs for subftr in ftrlist(ftr))
    if len(ftrs) == 0:
        return None

    if len(ftrs) == 1:
        return ftrs[0]

    parent = kw.pop("parent") if "parent" in kw else ftrs[0].getParentGroup()
    obj = addObject("Part::MultiCommon", "Intersection", parent=parent)
    obj.Shapes = ftrs
    return obj

def fuse(*ftrs, **kw):
    ftrs = distinct_list(subftr for ftr in ftrs for subftr in ftrlist(ftr))
    if len(ftrs) == 0:
        return None

    if len(ftrs) == 1:
        return ftrs[0]

    parent = kw.pop("parent") if "parent" in kw else ftrs[0].getParentGroup()
    obj = addObject("Part::MultiFuse", "Union", parent=parent)
    obj.Shapes = ftrs
    return obj

def complement(ftr, parent=None):
    parent = parent if parent is not None else ftr.getParentGroup()
    obj = addObject(Complement, "Complement", parent=parent)
    obj.Source = ftr
    return obj

def transform(ftr, *plcs, **kw):
    parent = kw.pop("parent") if "parent" in kw else ftr.getParentGroup()
    obj = addObject(Transform, "Transform", parent=parent)
    obj.Source = ftr
    obj.Placements = plcs
    return obj


def compound(*ftrs, **kw):
    ftrs = distinct_list(subftr for ftr in ftrs for subftr in ftrlist(ftr))
    parent = kw.pop("parent") if "parent" in kw else ftrs[0].getParentGroup()
    obj = addObject("Part::Compound", "Compound", parent=parent)
    obj.Links = ftrs
    return obj

def compound_common(target, *ftrs, **kw):
    if len(ftrs) == 0:
        return target

    ftrss = [ftrlist(ftr) for ftr in ftrs]
    if len(ftrlist(target)) > 0:
        ftrss = [ftrlist(target)] + ftrss
    target.Links = [common(*ftrs, **kw) for ftrs in product(*ftrss)]
    return target

def compound_slice(target, *ftrs, **kw):
    if len(ftrs) == 0:
        return target

    ftrss = [[ftr, complement(ftr)] for ftr in ftrs]
    if len(ftrlist(target)) > 0:
        ftrss = [ftrlist(target)] + ftrss
    target.Links = [common(*ftrs, **kw) for ftrs in product(*ftrss)]
    return target

def compound_transform(target, *plcs, **kw):
    if len(plcs) == 0:
        return target

    plcss = [ftrlist(plc) for plc in plcs]
    argss = [ftrlist(target)] + plcss
    target.Links = [transform(*args, **kw) for args in product(*argss)]
    return target

