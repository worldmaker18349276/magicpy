import math
from symplus.affine import AffineTransformation, rmat_k2d
import symplus.euclid as euclid
import FreeCAD, Part, Mesh, BuildRegularGeoms
from MagicPart.Basic import spstr2spexpr, spexpr2spstr
from MagicPart.Features.Utilities import *
from MagicPart.Features.ViewBox import getViewBox
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
            SymPyExpression = clazz.SymPyType()
        prop["SymPyExpression"] = args.get("SymPyExpression", SymPyExpression)

        return prop

    def getSymPyPropertiesList(self, obj):
        return [p for p in obj.PropertiesList if obj.getGroupOfProperty(p) == "SymPyExpression"]

    def getSymPyExpression(self, obj, normalization=True):
        kwargs = {"normalization": normalization}
        for p in self.getSymPyPropertiesList(obj):
            kwargs[p.lower()] = spstr2spexpr(obj.getPropertyByName(p))
        return self.SymPyType(**kwargs)

    def setSymPyExpression(self, obj, expr):
        if not isinstance(expr, self.SymPyType):
            raise TypeError
        for p in self.getSymPyPropertiesList(obj):
            setattr(obj, p, spexpr2spstr(getattr(expr, p.lower())))

    def execute(self, obj):
        V = getattr(obj, "ViewBox", None)
        mbb = boundBoxOf(V) if V is not None else None
        expr = self.getSymPyExpression(obj)

        if isDerivedFrom(obj, "Part::FeaturePython"):
            shape = Shapes.primitive(expr, mbb)

            if shape is True:
                obj.Shape = Shapes.primitive(euclid.WholeSpace(), mbb)
            elif shape is False:
                obj.Shape = Part.Shape()
            else:
                obj.Shape = Shapes.reshape(shape)

        elif isDerivedFrom(obj, "Mesh::FeaturePython"):
            mesh = Meshes.primitive(expr, mbb)

            if mesh is True:
                obj.Mesh = Meshes.primitive(euclid.WholeSpace(), mbb)
            elif mesh is False:
                obj.Mesh = Mesh.Mesh()
            else:
                obj.Mesh = Meshes.remesh(mesh)

        else:
            raise TypeError

    def _trace(self, obj):
        return [None]*len(obj.Shape.Faces)

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


WholeSpace = SymbolicPrimitiveWholeSpaceProxy
Halfspace = SymbolicPrimitiveHalfspaceProxy
Sphere = SymbolicPrimitiveSphereProxy
InfiniteCylinder = SymbolicPrimitiveInfiniteCylinderProxy
SemiInfiniteCone = SymbolicPrimitiveSemiInfiniteConeProxy
Box = SymbolicPrimitiveBoxProxy
Cylinder = SymbolicPrimitiveCylinderProxy
Cone = SymbolicPrimitiveConeProxy

