import symplus.euclid as euclid
import symplus.setplus as setplus
import FreeCAD
from MagicPart.Basic import spstr2spexpr, spexpr2spstr, P
from MagicPart.Features.Utilities import *
from MagicPart.Features.ViewBox import getViewBox, viewAllBounded
from MagicPart.Features.Operation import (Intersection, Union, AbsoluteComplement, Image,
    complement, common, fuse, cut, transform)
from MagicPart import Shapes, Meshes


class SymbolicPrimitiveViewProxy(object):
    def __init__(self, icon=""):
        self.icon = icon

    def getIcon(self):
        return self.icon

    def onChanged(self, view, p):
        if isDerivedFrom(view.Object, "Part::FeaturePython"):
            if p == "ShapeColor":
                clrs = diffuseColorOf(view.Object)
                for i in range(len(clrs)):
                    clrs[i] = view.ShapeColor[:3] + clrs[i][-1:]
                view.DiffuseColor = clrs

            elif p == "Transparency":
                clrs = diffuseColorOf(view.Object)
                tr = (view.Transparency/100.,)
                for i in range(len(clrs)):
                    clrs[i] = clrs[i][:3]+tr
                view.DiffuseColor = clrs

class SymbolicPrimitiveProxy(FeaturePythonProxy):
    @classmethod
    def featurePropertiesOf(clazz, obj=None, args={}):
        prop = {}
        prop["TypeId"] = clazz

        if obj is not None:
            SymPyExpression = obj.Proxy.getSymPyExpression(obj)
        else:
            SymPyExpression = clazz.SymPyType() if hasattr(clazz, "SymPyType") else None

        prop["SymPyExpression"] = args.get("SymPyExpression", SymPyExpression)

        return prop

    def getSymPyPropertiesList(self, obj):
        return [p for p in obj.PropertiesList if obj.getGroupOfProperty(p) == "SymPyExpression"]

    def getSymPyExpression(self, obj, normalization=True):
        if hasattr(self, "SymPyType"):
            kwargs = {"normalization": normalization}
            for p in self.getSymPyPropertiesList(obj):
                kwargs[p.lower()] = spstr2spexpr(obj.getPropertyByName(p))
            return self.SymPyType(**kwargs)

        else:
            return obj.SymPyExpression

    def setSymPyExpression(self, obj, expr):
        if hasattr(self, "SymPyType"):
            if not isinstance(expr, self.SymPyType):
                raise TypeError
            for p in self.getSymPyPropertiesList(obj):
                setattr(obj, p, spexpr2spstr(getattr(expr, p.lower())))

        else:
            obj.SymPyExpression = expr

    def onChanged(self, obj, p):
        if p == "Proxy":
            if "ViewBox" not in obj.PropertiesList:
                obj.addProperty("App::PropertyLink", "ViewBox")
                obj.setEditorMode("ViewBox", 2)
                obj.ViewBox = getViewBox(obj.Document)
            if "SymPyExpression" not in obj.PropertiesList:
                obj.addProperty("App::PropertyPythonObject", "SymPyExpression")
            obj.setEditorMode("Placement", 2)
            if FreeCAD.GuiUp:
                obj.ViewObject.Proxy = SymbolicPrimitiveViewProxy()

    def execute(self, obj):
        V = getattr(obj, "ViewBox", None)
        mbb = boundBoxOf(V) if V is not None else None
        expr = self.getSymPyExpression(obj)

        if isDerivedFrom(obj, "Part::FeaturePython"):
            shape = Shapes.construct(expr, mbb)
            obj.Shape = shape
            obj.Placement = shape.Placement

        elif isDerivedFrom(obj, "Mesh::FeaturePython"):
            mesh = Meshes.construct(expr, mbb)
            obj.Mesh = mesh
            obj.Placement = mesh.Placement

        else:
            raise TypeError

    def _trace(self, obj):
        return [None]*len(obj.Shape.Faces)

class SymbolicPrimitiveEmptySpaceProxy(SymbolicPrimitiveProxy):
    SymPyType = euclid.EmptySpace

    def onChanged(self, obj, p):
        if p == "Proxy":
            obj.setEditorMode("Placement", 2)
            if FreeCAD.GuiUp:
                obj.ViewObject.Proxy = SymbolicPrimitiveViewProxy()

class SymbolicPrimitiveWholeSpaceProxy(SymbolicPrimitiveProxy):
    SymPyType = euclid.WholeSpace

    def onChanged(self, obj, p):
        if p == "Proxy":
            if "ViewBox" not in obj.PropertiesList:
                obj.addProperty("App::PropertyLink", "ViewBox")
                obj.setEditorMode("ViewBox", 2)
                obj.ViewBox = getViewBox(obj.Document)
            obj.setEditorMode("Placement", 2)
            if FreeCAD.GuiUp:
                obj.ViewObject.Proxy = SymbolicPrimitiveViewProxy()

class SymbolicPrimitiveHalfspaceProxy(SymbolicPrimitiveProxy):
    SymPyType = euclid.Halfspace

    def onChanged(self, obj, p):
        if p == "Proxy":
            if "Offset" not in obj.PropertiesList:
                obj.addProperty("App::PropertyString", "Offset", "SymPyExpression")
                obj.Offset = "0"
            if "Direction" not in obj.PropertiesList:
                obj.addProperty("App::PropertyString", "Direction", "SymPyExpression")
                obj.Direction = "[0, 0, 1]"
            if "ViewBox" not in obj.PropertiesList:
                obj.addProperty("App::PropertyLink", "ViewBox")
                obj.setEditorMode("ViewBox", 2)
                obj.ViewBox = getViewBox(obj.Document)
            obj.setEditorMode("Placement", 2)
            if FreeCAD.GuiUp:
                obj.ViewObject.Proxy = SymbolicPrimitiveViewProxy()

class SymbolicPrimitiveSphereProxy(SymbolicPrimitiveProxy):
    SymPyType = euclid.Sphere

    def onChanged(self, obj, p):
        if p == "Proxy":
            if "Radius" not in obj.PropertiesList:
                obj.addProperty("App::PropertyString", "Radius", "SymPyExpression")
                obj.Radius = "1"
            if "Center" not in obj.PropertiesList:
                obj.addProperty("App::PropertyString", "Center", "SymPyExpression")
                obj.Center = "[0, 0, 0]"
            obj.setEditorMode("Placement", 2)
            if FreeCAD.GuiUp:
                obj.ViewObject.Proxy = SymbolicPrimitiveViewProxy()

class SymbolicPrimitiveInfiniteCylinderProxy(SymbolicPrimitiveProxy):
    SymPyType = euclid.InfiniteCylinder

    def onChanged(self, obj, p):
        if p == "Proxy":
            if "Radius" not in obj.PropertiesList:
                obj.addProperty("App::PropertyString", "Radius", "SymPyExpression")
                obj.Radius = "1"
            if "Center" not in obj.PropertiesList:
                obj.addProperty("App::PropertyString", "Center", "SymPyExpression")
                obj.Center = "[0, 0, 0]"
            if "Direction" not in obj.PropertiesList:
                obj.addProperty("App::PropertyString", "Direction", "SymPyExpression")
                obj.Direction = "[0, 0, 1]"
            if "ViewBox" not in obj.PropertiesList:
                obj.addProperty("App::PropertyLink", "ViewBox")
                obj.setEditorMode("ViewBox", 2)
                obj.ViewBox = getViewBox(obj.Document)
            obj.setEditorMode("Placement", 2)
            if FreeCAD.GuiUp:
                obj.ViewObject.Proxy = SymbolicPrimitiveViewProxy()

class SymbolicPrimitiveSemiInfiniteConeProxy(SymbolicPrimitiveProxy):
    SymPyType = euclid.SemiInfiniteCone

    def onChanged(self, obj, p):
        if p == "Proxy":
            if "Slope" not in obj.PropertiesList:
                obj.addProperty("App::PropertyString", "Slope", "SymPyExpression")
                obj.Slope = "1"
            if "Center" not in obj.PropertiesList:
                obj.addProperty("App::PropertyString", "Center", "SymPyExpression")
                obj.Center = "[0, 0, 0]"
            if "Direction" not in obj.PropertiesList:
                obj.addProperty("App::PropertyString", "Direction", "SymPyExpression")
                obj.Direction = "[0, 0, 1]"
            if "ViewBox" not in obj.PropertiesList:
                obj.addProperty("App::PropertyLink", "ViewBox")
                obj.setEditorMode("ViewBox", 2)
                obj.ViewBox = getViewBox(obj.Document)
            obj.setEditorMode("Placement", 2)
            if FreeCAD.GuiUp:
                obj.ViewObject.Proxy = SymbolicPrimitiveViewProxy()

class SymbolicPrimitiveBoxProxy(SymbolicPrimitiveProxy):
    SymPyType = euclid.Box

    def onChanged(self, obj, p):
        if p == "Proxy":
            if "Size" not in obj.PropertiesList:
                obj.addProperty("App::PropertyString", "Size", "SymPyExpression")
                obj.Size = "[2, 2, 2]"
            if "Center" not in obj.PropertiesList:
                obj.addProperty("App::PropertyString", "Center", "SymPyExpression")
                obj.Center = "[0, 0, 0]"
            if "Orientation" not in obj.PropertiesList:
                obj.addProperty("App::PropertyString", "Orientation", "SymPyExpression")
                obj.Orientation = "eye(3)"
            obj.setEditorMode("Placement", 2)
            if FreeCAD.GuiUp:
                obj.ViewObject.Proxy = SymbolicPrimitiveViewProxy()

class SymbolicPrimitiveCylinderProxy(SymbolicPrimitiveProxy):
    SymPyType = euclid.Cylinder

    def onChanged(self, obj, p):
        if p == "Proxy":
            if "Radius" not in obj.PropertiesList:
                obj.addProperty("App::PropertyString", "Radius", "SymPyExpression")
                obj.Radius = "1"
            if "Height" not in obj.PropertiesList:
                obj.addProperty("App::PropertyString", "Height", "SymPyExpression")
                obj.Height = "2"
            if "Center" not in obj.PropertiesList:
                obj.addProperty("App::PropertyString", "Center", "SymPyExpression")
                obj.Center = "[0, 0, 0]"
            if "Direction" not in obj.PropertiesList:
                obj.addProperty("App::PropertyString", "Direction", "SymPyExpression")
                obj.Direction = "[0, 0, 1]"
            obj.setEditorMode("Placement", 2)
            if FreeCAD.GuiUp:
                obj.ViewObject.Proxy = SymbolicPrimitiveViewProxy()

class SymbolicPrimitiveConeProxy(SymbolicPrimitiveProxy):
    SymPyType = euclid.Cone

    def onChanged(self, obj, p):
        if p == "Proxy":
            if "Radius" not in obj.PropertiesList:
                obj.addProperty("App::PropertyString", "Radius", "SymPyExpression")
                obj.Radius = "1"
            if "Height" not in obj.PropertiesList:
                obj.addProperty("App::PropertyString", "Height", "SymPyExpression")
                obj.Height = "1"
            if "Center" not in obj.PropertiesList:
                obj.addProperty("App::PropertyString", "Center", "SymPyExpression")
                obj.Center = "[0, 0, 0]"
            if "Direction" not in obj.PropertiesList:
                obj.addProperty("App::PropertyString", "Direction", "SymPyExpression")
                obj.Direction = "[0, 0, 1]"
            obj.setEditorMode("Placement", 2)
            if FreeCAD.GuiUp:
                obj.ViewObject.Proxy = SymbolicPrimitiveViewProxy()


Feature = SymbolicPrimitiveProxy
EmptySpace = SymbolicPrimitiveEmptySpaceProxy
WholeSpace = SymbolicPrimitiveWholeSpaceProxy
Halfspace = SymbolicPrimitiveHalfspaceProxy
Sphere = SymbolicPrimitiveSphereProxy
InfiniteCylinder = SymbolicPrimitiveInfiniteCylinderProxy
SemiInfiniteCone = SymbolicPrimitiveSemiInfiniteConeProxy
Box = SymbolicPrimitiveBoxProxy
Cylinder = SymbolicPrimitiveCylinderProxy
Cone = SymbolicPrimitiveConeProxy


def show(expr):
    ftr = addObject(Feature, "Feature",
        rep=P.rep, cached=P.cached, args=dict(SymPyExpression=expr))
    recompute([ftr])
    viewAllBounded()
    return ftr

def construct(expr):
    if expr is None:
        return Part.Shape()

    elif isinstance(expr, setplus.Intersection):
        return common(*[construct(arg) for arg in expr.args])

    elif isinstance(expr, setplus.Union):
        return fuse(*[construct(arg) for arg in expr.args])

    elif isinstance(expr, setplus.Complement):
        return cut(construct(expr.args[0]), construct(expr.args[1]))

    elif isinstance(expr, setplus.AbsoluteComplement):
        return complement(construct(expr.args[0]))

    elif isinstance(expr, setplus.Image):
        return transform(construct(expr.set), expr.function)

    elif isinstance(expr, euclid.EmptySpace):
        return addObject(EmptySpace, "EmptySpace", rep=P.rep, cached=P.cached)

    elif isinstance(expr, euclid.WholeSpace):
        return addObject(WholeSpace, "WholeSpace", rep=P.rep, cached=P.cached)

    elif isinstance(expr, euclid.Halfspace):
        return addObject(Halfspace, "Halfspace",
            rep=P.rep, cached=P.cached, args=dict(SymPyExpression=expr))

    elif isinstance(expr, euclid.InfiniteCylinder):
        return addObject(InfiniteCylinder, "InfiniteCylinder",
            rep=P.rep, cached=P.cached, args=dict(SymPyExpression=expr))

    elif isinstance(expr, euclid.SemiInfiniteCone):
        return addObject(SemiInfiniteCone, "SemiInfiniteCone",
            rep=P.rep, cached=P.cached, args=dict(SymPyExpression=expr))

    elif isinstance(expr, euclid.Sphere):
        return addObject(Sphere, "Sphere",
            rep=P.rep, cached=P.cached, args=dict(SymPyExpression=expr))

    elif isinstance(expr, euclid.Box):
        return addObject(Box, "Box",
            rep=P.rep, cached=P.cached, args=dict(SymPyExpression=expr))

    elif isinstance(expr, euclid.Cylinder):
        return addObject(Cylinder, "Cylinder",
            rep=P.rep, cached=P.cached, args=dict(SymPyExpression=expr))

    elif isinstance(expr, euclid.Cone):
        return addObject(Cone, "Cone",
            rep=P.rep, cached=P.cached, args=dict(SymPyExpression=expr))

    else:
        raise TypeError

def SymPyExpressionOf(ftr):
    if ftr is None:
        return euclid.EmptySpace()

    elif isDerivedFrom(ftr, "MutliCommon"):
        return setplus.Intersection(*[SymPyExpressionOf(outftr) for outftr in ftr.Shapes])

    elif isDerivedFrom(ftr, Intersection):
        return setplus.Intersection(*[SymPyExpressionOf(outftr) for outftr in ftr.Sources])

    elif isDerivedFrom(ftr, "MultiFuse"):
        return setplus.Union(*[SymPyExpressionOf(outftr) for outftr in ftr.Shapes])

    elif isDerivedFrom(ftr, Union):
        return setplus.Union(*[SymPyExpressionOf(outftr) for outftr in ftr.Sources])

    elif isDerivedFrom(ftr, "Cut"):
        return setplus.Complement(SymPyExpressionOf(ftr.Base), SymPyExpressionOf(ftr.Tool))

    elif isDerivedFrom(ftr, AbsoluteComplement):
        return setplus.AbsoluteComplement(SymPyExpressionOf(ftr.Source))

    elif isDerivedFrom(ftr, Image):
        return setplus.Image(SymPyExpressionOf(ftr.Source), ftr.Proxy.getSymPyTransformation(ftr))

    elif isDerivedFrom(ftr, Feature):
        return ftr.Proxy.getSymPyExpression(ftr)

    else:
        raise TypeError

