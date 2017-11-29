import FreeCAD, Part
import GeometricResources
from Geometric.Basic import Vec, o, k
from Geometric.Features.Utilities import *
from Geometric import Shapes, Meshes


class MaskedProxy(ScriptedObjectProxy):
    def __init__(self, obj):
        obj.Proxy = self
        if "Min" not in obj.PropertiesList:
            obj.addProperty("App::PropertyVector", "Min", "ViewBox")
            obj.Min = Vec(-1.5,-1.5,-1.5)
        if "Max" not in obj.PropertiesList:
            obj.addProperty("App::PropertyVector", "Max", "ViewBox")
            obj.Max = Vec( 1.5, 1.5, 1.5)
        if "Margin" not in obj.PropertiesList:
            obj.addProperty("App::PropertyFloat", "Margin", "ViewBox")
            obj.Margin = 0.01

    def getViewBox(self, obj):
        V = obj.Max - obj.Min
        if V.x <= 0 or V.y <= 0 or V.z <= 0:
             return Part.Shape()
        else:
             return Part.makeBox(V.x, V.y, V.z, obj.Min)

    def getBoundBox(self, obj):
        return FreeCAD.BoundBox(obj.Min, obj.Max)

    def setBoundBox(self, obj, bb):
        obj.Min = bb.getPoint(4)
        obj.Max = bb.getPoint(2)

class PrimitiveProxy(ScriptedObjectProxy):
    def __init__(self, obj):
        obj.Proxy = self
        obj.setEditorMode("Placement", 2)

        if FreeCAD.GuiUp:
            PrimitiveViewProxy(obj.ViewObject)

class UnboundedPrimitiveProxy(PrimitiveProxy, MaskedProxy):
    pass

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
    def __init__(self, obj):
        obj.Proxy = self
        obj.setEditorMode("Placement", 2)

        if FreeCAD.GuiUp:
            PrimitiveViewProxy(obj.ViewObject, ":/icons/primitive/Geometric_empty_space.svg")

    def execute(self, obj):
        if isDerivedFrom(obj, "Part::FeaturePython"):
            builder = Shapes
        elif isDerivedFrom(obj, "Mesh::FeaturePython"):
            builder = Meshes
        else:
            raise TypeError

        setGeometry(obj, builder.makeEmptySpace())

class WholeSpaceProxy(UnboundedPrimitiveProxy):
    def __init__(self, obj):
        obj.Proxy = self
        if "Min" not in obj.PropertiesList:
            obj.addProperty("App::PropertyVector", "Min", "ViewBox")
            obj.Min = Vec(-1.5,-1.5,-1.5)
        if "Max" not in obj.PropertiesList:
            obj.addProperty("App::PropertyVector", "Max", "ViewBox")
            obj.Max = Vec( 1.5, 1.5, 1.5)
        if "Margin" not in obj.PropertiesList:
            obj.addProperty("App::PropertyFloat", "Margin", "ViewBox")
            obj.Margin = 0.01
        obj.setEditorMode("Placement", 2)

        if FreeCAD.GuiUp:
            PrimitiveViewProxy(obj.ViewObject, ":/icons/primitive/Geometric_whole_space.svg")

            # obj.ViewObject.DisplayMode = "Wireframe"
            # obj.ViewObject.DrawStyle = "Dashed"
            # obj.ViewObject.DiffuseColor = [(1., 1., 1., 1.)]*6
            # obj.ViewObject.LineColor = (1., 0., 0.)

    def execute(self, obj):
        if isDerivedFrom(obj, "Part::FeaturePython"):
            builder = Shapes
        elif isDerivedFrom(obj, "Mesh::FeaturePython"):
            builder = Meshes
        else:
            raise TypeError

        bb = self.getBoundBox(obj)
        bb.enlarge(obj.Margin)
        geo = builder.makeWholeSpace(bb=bb)
        geo = builder.common([geo, self.getViewBox(obj)])
        setGeometry(obj, geo)

class HalfspaceProxy(UnboundedPrimitiveProxy):
    def __init__(self, obj):
        obj.Proxy = self
        if "Min" not in obj.PropertiesList:
            obj.addProperty("App::PropertyVector", "Min", "ViewBox")
            obj.Min = Vec(-1.5,-1.5,-1.5)
        if "Max" not in obj.PropertiesList:
            obj.addProperty("App::PropertyVector", "Max", "ViewBox")
            obj.Max = Vec( 1.5, 1.5, 1.5)
        if "Margin" not in obj.PropertiesList:
            obj.addProperty("App::PropertyFloat", "Margin", "ViewBox")
            obj.Margin = 0.01
        if "Offset" not in obj.PropertiesList:
            obj.addProperty("App::PropertyFloat", "Offset")
            obj.Offset = 0.
        if "Direction" not in obj.PropertiesList:
            obj.addProperty("App::PropertyVector", "Direction")
            obj.Direction = k
        obj.setEditorMode("Placement", 2)

        if FreeCAD.GuiUp:
            PrimitiveViewProxy(obj.ViewObject, ":/icons/primitive/Geometric_halfspace.svg")

    def execute(self, obj):
        if isDerivedFrom(obj, "Part::FeaturePython"):
            builder = Shapes
        elif isDerivedFrom(obj, "Mesh::FeaturePython"):
            builder = Meshes
        else:
            raise TypeError

        bb = self.getBoundBox(obj)
        bb.enlarge(obj.Margin)
        geo = builder.makeHalfspace(direction=obj.Direction, offset=obj.Offset, bb=bb)
        geo = builder.common([geo, self.getViewBox(obj)])
        setGeometry(obj, geo)

class InfiniteCylinderProxy(UnboundedPrimitiveProxy):
    def __init__(self, obj):
        obj.Proxy = self
        if "Min" not in obj.PropertiesList:
            obj.addProperty("App::PropertyVector", "Min", "ViewBox")
            obj.Min = Vec(-1.5,-1.5,-1.5)
        if "Max" not in obj.PropertiesList:
            obj.addProperty("App::PropertyVector", "Max", "ViewBox")
            obj.Max = Vec( 1.5, 1.5, 1.5)
        if "Margin" not in obj.PropertiesList:
            obj.addProperty("App::PropertyFloat", "Margin", "ViewBox")
            obj.Margin = 0.01
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
            PrimitiveViewProxy(obj.ViewObject, ":/icons/primitive/Geometric_infinite_cylinder.svg")

    def execute(self, obj):
        if isDerivedFrom(obj, "Part::FeaturePython"):
            builder = Shapes
        elif isDerivedFrom(obj, "Mesh::FeaturePython"):
            builder = Meshes
        else:
            raise TypeError

        bb = self.getBoundBox(obj)
        bb.enlarge(obj.Margin)
        geo = builder.makeInfiniteCylinder(radius=obj.Radius, direction=obj.Direction, center=obj.Center, bb=bb)
        geo = builder.common([geo, self.getViewBox(obj)])
        setGeometry(obj, geo)

class SemiInfiniteConeProxy(UnboundedPrimitiveProxy):
    def __init__(self, obj):
        obj.Proxy = self
        if "Min" not in obj.PropertiesList:
            obj.addProperty("App::PropertyVector", "Min", "ViewBox")
            obj.Min = Vec(-1.5,-1.5,-1.5)
        if "Max" not in obj.PropertiesList:
            obj.addProperty("App::PropertyVector", "Max", "ViewBox")
            obj.Max = Vec( 1.5, 1.5, 1.5)
        if "Margin" not in obj.PropertiesList:
            obj.addProperty("App::PropertyFloat", "Margin", "ViewBox")
            obj.Margin = 0.01
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
            PrimitiveViewProxy(obj.ViewObject, ":/icons/primitive/Geometric_semi_infinite_cone.svg")

    def execute(self, obj):
        if isDerivedFrom(obj, "Part::FeaturePython"):
            builder = Shapes
        elif isDerivedFrom(obj, "Mesh::FeaturePython"):
            builder = Meshes
        else:
            raise TypeError

        bb = self.getBoundBox(obj)
        bb.enlarge(obj.Margin)
        geo = builder.makeSemiInfiniteCone(slope=obj.Slope, direction=obj.Direction, center=obj.Center, bb=bb)
        geo = builder.common([geo, self.getViewBox(obj)])
        setGeometry(obj, geo)

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
            PrimitiveViewProxy(obj.ViewObject, ":/icons/primitive/Geometric_sphere.svg")

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
            PrimitiveViewProxy(obj.ViewObject, ":/icons/primitive/Geometric_cone.svg")

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
            PrimitiveViewProxy(obj.ViewObject, ":/icons/primitive/Geometric_cylinder.svg")

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

