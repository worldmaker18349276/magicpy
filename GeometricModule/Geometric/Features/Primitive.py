import FreeCAD
from Geometric.Basic import o, k
from Geometric.Features.Utilities import *
from Geometric.Features.ViewBox import getViewBox, viewAllBounded
from Geometric import Shapes, Meshes


class PrimitiveProxy(ScriptedObjectProxy):
    def __init__(self, obj):
        obj.Proxy = self
        obj.setEditorMode("Placement", 2)

        if FreeCAD.GuiUp:
            PrimitiveViewProxy(obj.ViewObject)

class UnboundedPrimitiveProxy(PrimitiveProxy):
    def __init__(self, obj):
        obj.Proxy = self
        if "ViewBox" not in obj.PropertiesList:
            obj.addProperty("App::PropertyLink", "ViewBox")
            obj.setEditorMode("ViewBox", 2)
            obj.ViewBox = getViewBox(obj.Document)
        obj.setEditorMode("Placement", 2)

        if FreeCAD.GuiUp:
            PrimitiveViewProxy(obj.ViewObject)

class PrimitiveViewProxy(object):
    def __init__(self, view, icon=""):
        view.Proxy = self
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


class EmptySpaceProxy(PrimitiveProxy):
    def execute(self, obj):
        if isDerivedFrom(obj, "Part::FeaturePython"):
            builder = Shapes
        elif isDerivedFrom(obj, "Mesh::FeaturePython"):
            builder = Meshes
        else:
            raise TypeError

        setGeometry(obj, builder.makeEmptySpace())

class WholeSpaceProxy(UnboundedPrimitiveProxy):
    def execute(self, obj):
        if isDerivedFrom(obj, "Part::FeaturePython"):
            builder = Shapes
        elif isDerivedFrom(obj, "Mesh::FeaturePython"):
            builder = Meshes
        else:
            raise TypeError

        bb = boundBoxOf(obj.ViewBox)
        bb.enlarge(obj.ViewBox.Margin)
        setGeometry(obj, builder.makeWholeSpace(bb=bb))

class HalfspaceProxy(UnboundedPrimitiveProxy):
    def __init__(self, obj):
        obj.Proxy = self
        if "ViewBox" not in obj.PropertiesList:
            obj.addProperty("App::PropertyLink", "ViewBox")
            obj.setEditorMode("ViewBox", 2)
            obj.ViewBox = getViewBox(obj.Document)
        if "Offset" not in obj.PropertiesList:
            obj.addProperty("App::PropertyFloat", "Offset")
            obj.Offset = 0.
        if "Direction" not in obj.PropertiesList:
            obj.addProperty("App::PropertyVector", "Direction")
            obj.Direction = k
        obj.setEditorMode("Placement", 2)

        if FreeCAD.GuiUp:
            PrimitiveViewProxy(obj.ViewObject)

    def execute(self, obj):
        if isDerivedFrom(obj, "Part::FeaturePython"):
            builder = Shapes
        elif isDerivedFrom(obj, "Mesh::FeaturePython"):
            builder = Meshes
        else:
            raise TypeError

        bb = boundBoxOf(obj.ViewBox)
        bb.enlarge(obj.ViewBox.Margin)
        setGeometry(obj, builder.makeHalfspace(direction=obj.Direction, offset=obj.Offset, bb=bb))

class InfiniteCylinderProxy(UnboundedPrimitiveProxy):
    def __init__(self, obj):
        obj.Proxy = self
        if "ViewBox" not in obj.PropertiesList:
            obj.addProperty("App::PropertyLink", "ViewBox")
            obj.setEditorMode("ViewBox", 2)
            obj.ViewBox = getViewBox(obj.Document)
        if "Radius" not in obj.PropertiesList:
            obj.addProperty("App::PropertyFloat", "Radius")
            obj.Radius = 1.
        if "Direction" not in obj.PropertiesList:
            obj.addProperty("App::PropertyVector", "Direction")
            obj.Direction = k
        if "Center" not in obj.PropertiesList:
            obj.addProperty("App::PropertyVector", "Center")
            obj.Center = o
        obj.setEditorMode("Placement", 2)

        if FreeCAD.GuiUp:
            PrimitiveViewProxy(obj.ViewObject)

    def execute(self, obj):
        if isDerivedFrom(obj, "Part::FeaturePython"):
            builder = Shapes
        elif isDerivedFrom(obj, "Mesh::FeaturePython"):
            builder = Meshes
        else:
            raise TypeError

        bb = boundBoxOf(obj.ViewBox)
        bb.enlarge(obj.ViewBox.Margin)
        setGeometry(obj, builder.makeInfiniteCylinder(radius=obj.Radius, direction=obj.Direction, center=obj.Center, bb=bb))

class SemiInfiniteConeProxy(UnboundedPrimitiveProxy):
    def __init__(self, obj):
        obj.Proxy = self
        if "ViewBox" not in obj.PropertiesList:
            obj.addProperty("App::PropertyLink", "ViewBox")
            obj.setEditorMode("ViewBox", 2)
            obj.ViewBox = getViewBox(obj.Document)
        if "Slope" not in obj.PropertiesList:
            obj.addProperty("App::PropertyFloat", "Slope")
            obj.Slope = 1.
        if "Direction" not in obj.PropertiesList:
            obj.addProperty("App::PropertyVector", "Direction")
            obj.Direction = k
        if "Center" not in obj.PropertiesList:
            obj.addProperty("App::PropertyVector", "Center")
            obj.Center = o
        obj.setEditorMode("Placement", 2)

        if FreeCAD.GuiUp:
            PrimitiveViewProxy(obj.ViewObject)

    def execute(self, obj):
        if isDerivedFrom(obj, "Part::FeaturePython"):
            builder = Shapes
        elif isDerivedFrom(obj, "Mesh::FeaturePython"):
            builder = Meshes
        else:
            raise TypeError

        bb = boundBoxOf(obj.ViewBox)
        bb.enlarge(obj.ViewBox.Margin)
        setGeometry(obj, builder.makeSemiInfiniteCone(slope=obj.Slope, direction=obj.Direction, center=obj.Center, bb=bb))

class SphereProxy(PrimitiveProxy):
    def __init__(self, obj):
        obj.Proxy = self
        if "Radius" not in obj.PropertiesList:
            obj.addProperty("App::PropertyFloat", "Radius")
            obj.Radius = 1.
        if "Center" not in obj.PropertiesList:
            obj.addProperty("App::PropertyVector", "Center")
            obj.Center = o
        obj.setEditorMode("Placement", 2)

        if FreeCAD.GuiUp:
            PrimitiveViewProxy(obj.ViewObject)

    def execute(self, obj):
        if isDerivedFrom(obj, "Part::FeaturePython"):
            builder = Shapes
        elif isDerivedFrom(obj, "Mesh::FeaturePython"):
            builder = Meshes
        else:
            raise TypeError

        setGeometry(obj, builder.makeSphere(radius=obj.Radius, center=obj.Center))

class ConeProxy(PrimitiveProxy):
    def __init__(self, obj):
        obj.Proxy = self
        if "Radius" not in obj.PropertiesList:
            obj.addProperty("App::PropertyFloat", "Radius")
            obj.Radius = 1.
        if "Center" not in obj.PropertiesList:
            obj.addProperty("App::PropertyVector", "Center")
            obj.Center = o
        if "Axis" not in obj.PropertiesList:
            obj.addProperty("App::PropertyVector", "Axis")
            obj.Axis = k
        obj.setEditorMode("Placement", 2)

        if FreeCAD.GuiUp:
            PrimitiveViewProxy(obj.ViewObject)

    def execute(self, obj):
        if isDerivedFrom(obj, "Part::FeaturePython"):
            builder = Shapes
        elif isDerivedFrom(obj, "Mesh::FeaturePython"):
            builder = Meshes
        else:
            raise TypeError

        setGeometry(obj, builder.makeConicalFrustum(radius1=0, radius2=obj.Radius, center=obj.Center, axis=obj.Axis))

class CylinderProxy(PrimitiveProxy):
    def __init__(self, obj):
        obj.Proxy = self
        if "Radius" not in obj.PropertiesList:
            obj.addProperty("App::PropertyFloat", "Radius")
            obj.Radius = 1.
        if "Center" not in obj.PropertiesList:
            obj.addProperty("App::PropertyVector", "Center")
            obj.Center = o
        if "Axis" not in obj.PropertiesList:
            obj.addProperty("App::PropertyVector", "Axis")
            obj.Axis = k*2
        obj.setEditorMode("Placement", 2)

        if FreeCAD.GuiUp:
            PrimitiveViewProxy(obj.ViewObject)

    def execute(self, obj):
        if isDerivedFrom(obj, "Part::FeaturePython"):
            builder = Shapes
        elif isDerivedFrom(obj, "Mesh::FeaturePython"):
            builder = Meshes
        else:
            raise TypeError

        setGeometry(obj, builder.makeConicalFrustum(radius1=obj.Radius, radius2=obj.Radius, center=obj.Center-obj.Axis*0.5, axis=obj.Axis))


Primitive = PrimitiveProxy
EmptySpace = EmptySpaceProxy
WholeSpace = WholeSpaceProxy
Halfspace = HalfspaceProxy
InfiniteCylinder = InfiniteCylinderProxy
SemiInfiniteCone = SemiInfiniteConeProxy
Sphere = SphereProxy
Cone = ConeProxy
Cylinder = CylinderProxy

