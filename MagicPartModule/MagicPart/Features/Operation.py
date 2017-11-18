from itertools import product, imap, starmap, islice
from functools import wraps
import FreeCAD
import symplus.setplus as setplus
from symplus.affine import EuclideanTransformation
from MagicPart.Basic import fuzzyCompare, spstr2spexpr, spexpr2spstr, spexpr2fcexpr, P
from MagicPart.Features.Utilities import *
from MagicPart.Features.SubObject import subFaceLinksOf, subColorOf, trace, outFaceLinksOf
from MagicPart import Shapes, Meshes


class DerivedFeatureViewProxy(object):
    def __init__(self, icon=""):
        self.icon = icon
        self.children = []

    def getIcon(self):
        return self.icon

    def claimChildren(self):
        return self.children

    def updateData(self, obj, p):
        if obj.getTypeIdOfProperty(p) in ["App::PropertyLink", "App::PropertyLinkList"]:
            outlist = ftrlist(obj.OutList)
            for ftr in outlist:
                if ftr not in self.children:
                    ftr.ViewObject.hide()
            self.children = outlist

        if p == "Outfaces":
            outlinks = outFaceLinksOf(obj, traced=False)
            if outlinks != []:
                clrs = []
                default_clr = obj.ViewObject.ShapeColor[:3]+(obj.ViewObject.Transparency/100.,)
                for outlink in outlinks:
                    clrs.append(subColorOf(outlink, default_clr))
                obj.ViewObject.DiffuseColor = clrs

    def onDelete(self, obj, subelems):
        for ftr in self.children:
            ftr.ViewObject.show()
        return True

class DerivedFeatureProxy(FeaturePythonProxy):
    pass

class FeatureIntersectionProxy(DerivedFeatureProxy):
    @classmethod
    def featurePropertiesOf(clazz, obj=None, args={}):
        prop = {}
        prop["TypeId"] = clazz

        Sources = getattr(obj, "Sources", None)
        prop["Sources"] = sorted(args.get("Sources", Sources), key=hash)

        return prop

    def getSymPyExpression(self, obj):
        return setplus.Intersection(*[s.Proxy.getSymPyExpression(s) for s in obj.Sources])

    def onChanged(self, obj, p):
        if p == "Proxy":
            if isDerivedFrom(obj, "Part::FeaturePython"):
                if "Outfaces" not in obj.PropertiesList:
                    obj.addProperty("App::PropertyPythonObject", "Outfaces")
                    obj.Outfaces = []
                    obj.setEditorMode("Outfaces", 2)

            if "Sources" not in obj.PropertiesList:
                obj.addProperty("App::PropertyLinkList", "Sources")
            obj.setEditorMode("Placement", 2)
            if FreeCAD.GuiUp:
                obj.ViewObject.Proxy = DerivedFeatureViewProxy()

    def execute(self, obj):
        if isDerivedFrom(obj, "Part::FeaturePython"):
            if P.hard:
                V = getattr(obj.Document, "ViewBox", None)
                mbb = boundBoxOf(V) if V is not None else None
                expr = self.getSymPyExpression(obj)
                shape = Shapes.construct(expr, mbb)
                obj.Shape = shape
                obj.Placement = shape.Placement
            else:
                obj.Shape = Shapes.common(s.Shape for s in obj.Sources)

            obj.Placement = FreeCAD.Placement()

            obj.Outfaces = trace(obj) if P.autotrace else []

        elif isDerivedFrom(obj, "Mesh::FeaturePython"):
            if P.hard:
                V = getattr(obj.Document, "ViewBox", None)
                mbb = boundBoxOf(V) if V is not None else None
                expr = self.getSymPyExpression(obj)
                mesh = Meshes.construct(expr, mbb)
                obj.Mesh = mesh
                obj.Placement = mesh.Placement
            else:
                obj.Mesh = Meshes.common(meshOf(s) for s in obj.Sources)

            obj.Placement = FreeCAD.Placement()

        else:
            raise TypeError

class FeatureUnionProxy(DerivedFeatureProxy):
    @classmethod
    def featurePropertiesOf(clazz, obj=None, args={}):
        prop = {}
        prop["TypeId"] = clazz

        Sources = getattr(obj, "Sources", None)
        prop["Sources"] = sorted(args.get("Sources", Sources), key=hash)

        return prop

    def getSymPyExpression(self, obj):
        return setplus.Union(*[s.Proxy.getSymPyExpression(s) for s in obj.Sources])

    def onChanged(self, obj, p):
        if p == "Proxy":
            if isDerivedFrom(obj, "Part::FeaturePython"):
                if "Outfaces" not in obj.PropertiesList:
                    obj.addProperty("App::PropertyPythonObject", "Outfaces")
                    obj.Outfaces = []
                    obj.setEditorMode("Outfaces", 2)

            if "Sources" not in obj.PropertiesList:
                obj.addProperty("App::PropertyLinkList", "Sources")
            obj.setEditorMode("Placement", 2)
            if FreeCAD.GuiUp:
                obj.ViewObject.Proxy = DerivedFeatureViewProxy()

    def execute(self, obj):
        if isDerivedFrom(obj, "Part::FeaturePython"):
            if P.hard:
                V = getattr(obj.Document, "ViewBox", None)
                mbb = boundBoxOf(V) if V is not None else None
                expr = self.getSymPyExpression(obj)
                shape = Shapes.construct(expr, mbb)
                obj.Shape = shape
                obj.Placement = shape.Placement
            else:
                obj.Shape = Shapes.fuse(s.Shape for s in obj.Sources)

            obj.Placement = FreeCAD.Placement()

            obj.Outfaces = trace(obj) if P.autotrace else []

        elif isDerivedFrom(obj, "Mesh::FeaturePython"):
            if P.hard:
                V = getattr(obj.Document, "ViewBox", None)
                mbb = boundBoxOf(V) if V is not None else None
                expr = self.getSymPyExpression(obj)
                mesh = Meshes.construct(expr, mbb)
                obj.Mesh = mesh
                obj.Placement = mesh.Placement
            else:
                obj.Mesh = Meshes.fuse(meshOf(s) for s in obj.Sources)

            obj.Placement = FreeCAD.Placement()

        else:
            raise TypeError

class FeatureAbsoluteComplementProxy(DerivedFeatureProxy):
    @classmethod
    def featurePropertiesOf(clazz, obj=None, args={}):
        prop = {}
        prop["TypeId"] = clazz

        Source = getattr(obj, "Source", None)
        prop["Source"] = args.get("Source", Source)

        return prop

    def getSymPyExpression(self, obj):
        return setplus.AbsoluteComplement(obj.Source.Proxy.getSymPyExpression(obj.Source))

    def onChanged(self, obj, p):
        if p == "Proxy":
            if isDerivedFrom(obj, "Part::FeaturePython"):
                if "Outfaces" not in obj.PropertiesList:
                    obj.addProperty("App::PropertyPythonObject", "Outfaces")
                    obj.Outfaces = []
                    obj.setEditorMode("Outfaces", 2)

            if "Source" not in obj.PropertiesList:
                obj.addProperty("App::PropertyLink", "Source")
            obj.setEditorMode("Placement", 2)
            if FreeCAD.GuiUp:
                obj.ViewObject.Proxy = DerivedFeatureViewProxy()

    def execute(self, obj):
        if isDerivedFrom(obj, "Part::FeaturePython"):
            if P.hard:
                V = getattr(obj.Document, "ViewBox", None)
                mbb = boundBoxOf(V) if V is not None else None
                expr = self.getSymPyExpression(obj)
                shape = Shapes.construct(expr, mbb)
                obj.Shape = shape
                obj.Placement = shape.Placement
            else:
                shape = Shapes.complement(obj.Source.Shape)
                obj.Shape = shape
                obj.Placement = shape.Placement

            obj.Outfaces = trace(obj) if P.autotrace else []

        elif isDerivedFrom(obj, "Mesh::FeaturePython"):
            if P.hard:
                V = getattr(obj.Document, "ViewBox", None)
                mbb = boundBoxOf(V) if V is not None else None
                expr = self.getSymPyExpression(obj)
                mesh = Meshes.construct(expr, mbb)
                obj.Mesh = mesh
                obj.Placement = mesh.Placement
            else:
                mesh = Meshes.complement(meshOf(obj.Source))
                obj.Mesh = mesh
                obj.Placement = mesh.Placement

        else:
            raise TypeError

    def _trace(self, obj):
        return subFaceLinksOf(obj.Source)

class FeatureImageProxy(DerivedFeatureProxy):
    @classmethod
    def featurePropertiesOf(clazz, obj=None, **kwargs):
        prop = {}
        prop["TypeId"] = clazz

        if obj is not None:
            Source = obj.Source
            SymPyTransformation = obj.Proxy.getSymPyTransformation(obj)
        else:
            Source = None
            SymPyTransformation = EuclideanTransformation()
        prop["Source"] = kwargs.get("Source", Source)
        prop["SymPyTransformation"] = kwargs.get("SymPyTransformation", SymPyTransformation)

        return prop

    def getSymPyTransformation(self, obj):
        return EuclideanTransformation(
            tvec=spstr2spexpr(obj.tvec),
            rquat=spstr2spexpr(obj.rquat),
            parity=spstr2spexpr(obj.parity))

    def setSymPyTransformation(self, obj, expr):
        if not isinstance(expr, EuclideanTransformation):
            raise TypeError
        obj.tvec = spexpr2spstr(expr.tvec)
        obj.rquat = spexpr2spstr(expr.rquat)
        obj.parity = spexpr2spstr(expr.parity)

    def getSymPyExpression(self, obj):
        return setplus.Image(
            self.getSyPyTransformation(obj),
            obj.Source.Proxy.getSymPyExpression(obj.Source))

    def onChanged(self, obj, p):
        if p == "Proxy":
            if isDerivedFrom(obj, "Part::FeaturePython"):
                if "Outfaces" not in obj.PropertiesList:
                    obj.addProperty("App::PropertyPythonObject", "Outfaces")
                    obj.Outfaces = []
                    obj.setEditorMode("Outfaces", 2)

            if "Source" not in obj.PropertiesList:
                obj.addProperty("App::PropertyLink", "Source")
            if "tvec" not in obj.PropertiesList:
                obj.addProperty("App::PropertyString", "tvec", "SymPyTransformation")
                obj.tvec = "[0, 0, 0]"
            if "rquat" not in obj.PropertiesList:
                obj.addProperty("App::PropertyString", "rquat", "SymPyTransformation")
                obj.rquat = "[1, 0, 0, 0]"
            if "parity" not in obj.PropertiesList:
                obj.addProperty("App::PropertyString", "parity", "SymPyTransformation")
                obj.parity = "1"
            obj.setEditorMode("Placement", 2)
            if FreeCAD.GuiUp:
                obj.ViewObject.Proxy = DerivedFeatureViewProxy()

    def execute(self, obj):
        if isDerivedFrom(obj, "Part::FeaturePython"):
            if P.hard:
                V = getattr(obj.Document, "ViewBox", None)
                mbb = boundBoxOf(V) if V is not None else None
                expr = self.getSymPyExpression(obj)
                shape = Shapes.construct(expr, mbb)
                obj.Shape = shape
                obj.Placement = shape.Placement
            else:
                shape = Shapes.transform(obj.Source.Shape, self.getSymPyTransformation(obj))
                obj.Shape = shape
                obj.Placement = shape.Placement

            obj.Outfaces = trace(obj) if P.autotrace else []

        elif isDerivedFrom(obj, "Mesh::FeaturePython"):
            if P.hard:
                V = getattr(obj.Document, "ViewBox", None)
                mbb = boundBoxOf(V) if V is not None else None
                expr = self.getSymPyExpression(obj)
                mesh = Meshes.construct(expr, mbb)
                obj.Mesh = mesh
                obj.Placement = mesh.Placement
            else:
                mesh = Meshes.transform(meshOf(obj.Source), self.getSymPyTransformation(obj))
                obj.Mesh = mesh
                obj.Placement = mesh.Placement

        else:
            raise TypeError

    def _trace(self, obj):
        return subFaceLinksOf(obj.Source)

Intersection = FeatureIntersectionProxy
Union = FeatureUnionProxy
AbsoluteComplement = FeatureAbsoluteComplementProxy
Image = FeatureImageProxy


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
def common(*ftrs, **kwargs):
    ftrs = [subftr for ftr in ftrs for subftr in ftrlist(ftr)]
    if len(ftrs) == 0:
        return None

    if len(ftrs) == 1:
        return ftrs[0]

    parent = kwargs.pop("parent", None)
    if parent is not None:
        parent.removeObjects(ftrs)

    if P.originop:
        return addObject("Part::MultiCommon", "Intersection", parent=parent,
                         cached=P.cached, args=dict(Shapes=ftrs))
    else:
        return addObject(Intersection, "Intersection", rep=P.rep, parent=parent,
                         cached=P.cached, args=dict(Sources=ftrs))

@autohide
def fuse(*ftrs, **kwargs):
    ftrs = [subftr for ftr in ftrs for subftr in ftrlist(ftr)]
    if len(ftrs) == 0:
        return None

    if len(ftrs) == 1:
        return ftrs[0]

    parent = kwargs.pop("parent", None)
    if parent is not None:
        parent.removeObjects(ftrs)

    if P.originop:
        return addObject("Part::multiFuse", "Union", parent=parent, cached=P.cached,
                         args=dict(Shapes=ftrs))
    else:
        return addObject(Union, "Union", rep=P.rep, parent=parent, cached=P.cached,
                         args=dict(Sources=ftrs))

@autohide
def cut(ftr1, ftr2, parent=None):
    if parent is not None:
        parent.removeObjects([ftr1, ftr2])

    if P.originop:
        return addObject("Part::Cut", "Cut", parent=parent, cached=P.cached,
                         args=dict(Base=ftr1, Tool=ftr2))
    else:
        return common(ftr1, complement(ftr2, autohide=False), autohide=False)

@autohide
def complement(ftr, parent=None):
    if parent is not None:
        parent.removeObject(ftr)

    return addObject(AbsoluteComplement, "AbsoluteComplement", rep=P.rep, parent=parent,
                     cached=P.cached, args=dict(Source=ftr))

@autohide
def transform(ftr, trans=None, parent=None):
    if parent is not None:
        parent.removeObjects(ftr)

    args = dict(Source=ftr)
    if trans is not None:
        args.SymPyTransformation = trans
    return addObject(Image, "Image", rep=P.rep, parent=parent, cached=P.cached, args=args)


def group(*ftrs, **kwargs):
    ftrs = [subftr for ftr in ftrs for subftr in ftrlist(ftr)]
    if len(ftrs) == 0:
        return None

    parent = kwargs.pop("parent", None)

    return addObject("App::DocumentObjectGroup", "Group", parent=parent, cached=P.cached,
                     args=dict(Group=ftrs))

def group_mask(target, *ftrs):
    if len(ftrs) == 0:
        return target

    ftrss = [ftrlist(ftr) for ftr in ftrs]
    if len(ftrlist(target)) > 0:
        ftrss = [ftrlist(target)] + ftrss
    target.Group = [common(*ftrs, parent=target) for ftrs in product(*ftrss)]
    return target

def group_slice(target, *ftrs):
    if len(ftrs) == 0:
        return target

    ftrss = [[ftr, complement(ftr)] for ftr in ftrs]
    if len(ftrlist(target)) > 0:
        ftrss = [ftrlist(target)] + ftrss
    target.Group = [common(*ftrs, parent=target) for ftrs in product(*ftrss)]
    return target


def isOutside(ftr1, ftr2):
    return fuzzyCompare(ftr1.Shape.common(ftr2.Shape).Volume, 0)

def isInside(ftr1, ftr2):
    return fuzzyCompare(ftr1.Shape.cut(ftr2.Shape).Volume, 0)

def catch(ftrs, reg):
    ftrs = ftrlist(ftrs)
    return [ftr for ftr in ftrs if isInside(ftr, reg)]

def noCollision(ftrs):
    ftrs = ftrlist(ftrs)
    shps = []
    for ftr in ftrs:
        if isDerivedFrom(ftr, ("Part::Compound", Compound)):
            shps.append(Shapes.fuse(outftr.Shape for outftr in ftrlist(ftr)))
        else:
            shps.append(ftr.Shape)
    vol_sum = sum(shp.Volume for shp in shps)
    vol_fus = Shapes.fuse(shps).Volume
    return fuzzyCompare(vol_sum, vol_fus)
