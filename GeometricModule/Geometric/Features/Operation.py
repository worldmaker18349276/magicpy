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
        if obj.getTypeIdOfProperty(p) in ["App::PropertyLink", "App::PropertyLinkList", "App::PropertyPlacementLink"]:
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
            DerivedFeatureViewProxy(obj.ViewObject)

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
        if "PlacementLink" not in obj.PropertiesList:
            obj.addProperty("App::PropertyPlacementLink", "PlacementLink")
        obj.setEditorMode("Placement", 2)
        if FreeCAD.GuiUp:
            DerivedFeatureViewProxy(obj.ViewObject)

    def execute(self, obj):
        if isDerivedFrom(obj, "Part::FeaturePython"):
            geo = Shapes.reshape(obj.Source.Shape)
            geo.Placement = obj.PlacementLink.Placement
            setGeometry(obj, geo)
            obj.ViewObject.DiffuseColor = obj.Source.ViewObject.DiffuseColor

        elif isDerivedFrom(obj, "Mesh::FeaturePython"):
            geo = Meshes.reshape(meshOf(obj.Source))
            geo.Placement = obj.PlacementLink.Placement
            setGeometry(obj, geo)

        else:
            raise TypeError

Complement = ComplementProxy
Transform = TransformProxy


def autohide(func):
    @wraps(func)
    def func_(*ftrs, **kwargs):
        autohide = kwargs.pop("autohide", True)
        if autohide:
            for ftr in ftrs:
                ftr.ViewObject.hide()
        res = func(*ftrs, **kwargs)
        if autohide and res is not None:
            res.ViewObject.show()
        return res
    return func_

@autohide
def common(*ftrs):
    ftrs = distinct_list(subftr for ftr in ftrs for subftr in ftrlist(ftr))
    if len(ftrs) == 0:
        return None

    if len(ftrs) == 1:
        return ftrs[0]

    obj = ftrs[0].Document.addObject("Part::MultiCommon", "Intersection")
    obj.Shapes = ftrs
    return obj

@autohide
def fuse(*ftrs):
    ftrs = distinct_list(subftr for ftr in ftrs for subftr in ftrlist(ftr))
    if len(ftrs) == 0:
        return None

    if len(ftrs) == 1:
        return ftrs[0]

    obj = ftrs[0].Document.addObject("Part::MultiFuse", "Union")
    obj.Shapes = ftrs
    return obj

@autohide
def complement(ftr):
    obj = ftr.Document.addObject("Part::FeaturePython", "Complement")
    Complement(obj)
    obj.Source = ftr
    return obj

@autohide
def transform(ftr, plc):
    obj = ftr.Document.addObject("Part::FeaturePython", "Transform")
    Transform(obj)
    obj.Source = ftr
    obj.PlacementLink = plc
    return obj


def group(*ftrs):
    ftrs = distinct_list(subftr for ftr in ftrs for subftr in ftrlist(ftr))

    obj = ftrs[0].Document.addObject("App::DocumentObjectGroup", "Group")
    for ftr in ftrs:
        ftr.getParentGroup().removeObject(ftr)
    obj.Group = ftrs
    return obj

def group_common(target, *ftrs):
    if len(ftrs) == 0:
        return target

    ftrss = [ftrlist(ftr) for ftr in ftrs]
    if len(ftrlist(target)) > 0:
        ftrss = [ftrlist(target)] + ftrss
    target.Group = [common(*ftrs) for ftrs in product(*ftrss)]
    return target

def group_slice(target, *ftrs):
    if len(ftrs) == 0:
        return target

    ftrss = [[ftr, complement(ftr)] for ftr in ftrs]
    if len(ftrlist(target)) > 0:
        ftrss = [ftrlist(target)] + ftrss
    target.Group = [common(*ftrs) for ftrs in product(*ftrss)]
    return target

