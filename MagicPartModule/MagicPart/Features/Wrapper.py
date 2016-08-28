import FreeCAD
from MagicPart.Basic import P
from MagicPart.Features.Utilities import *
from MagicPart.Features.ViewBox import getViewBox
from MagicPart.Features.Operation import Compound, DerivedFeatureViewProxy
from MagicPart.Features.BooleanTracing import trace
from MagicPart import Shapes, Meshes


class WrappedFeatureProxy(FeaturePythonProxy):
    pass

class FeatureApartProxy(WrappedFeatureProxy):
    @classmethod
    def featurePropertiesOf(clazz, obj=None, args={}):
        prop = {}
        prop["TypeId"] = clazz

        Origin = getattr(obj, "Origin", None)
        Base = getattr(obj, "Base", FreeCAD.Vector(0,0,0))
        Ratio = getattr(obj, "Ratio", 1.5)
        prop["Origin"] = args.get("Origin", Origin)
        prop["Base"] = args.get("Base", Base)
        prop["Ratio"] = args.get("Ratio", Ratio)

        return prop

    def onChanged(self, obj, p):
        if p == "Proxy":
            if isDerivedFrom(obj, "Part::FeaturePython"):
                if "Outfaces" not in obj.PropertiesList:
                    obj.addProperty("App::PropertyPythonObject", "Outfaces")
                    obj.Outfaces = []
                    obj.setEditorMode("Outfaces", 2)

            if "Origin" not in obj.PropertiesList:
                obj.addProperty("App::PropertyLink", "Origin")
            if "Base" not in obj.PropertiesList:
                obj.addProperty("App::PropertyVector", "Base")
            if "Ratio" not in obj.PropertiesList:
                obj.addProperty("App::PropertyFloat", "Ratio")
                obj.Ratio = 1.5
            obj.setEditorMode("Placement", 2)
            if FreeCAD.GuiUp:
                obj.ViewObject.Proxy = DerivedFeatureViewProxy()

        if p == "Ratio":
            if not isTouched(obj.Origin):
                self.execute(obj)

    def execute(self, obj):
        if obj.Origin is None:
            obj.Shape = Part.Shape()
            return

        if isDerivedFrom(obj.Origin, "Part::Compound"):
            ftrs = obj.Origin.Links
        elif isDerivedFrom(obj.Origin, Compound):
            ftrs = obj.Origin.Sources
        else:
            raise TypeError

        if isDerivedFrom(obj, "Part::FeaturePython"):
            shapes = []
            for ftr in ftrs:
                shape = Shapes.reshape(ftr.Shape)
                center = Shapes.center(shape)
                if center is None:
                    R = FreeCAD.Vector(0,0,0)
                else:
                    R = center - obj.Base
                shift = R*obj.Ratio - R
                shape.Placement = FreeCAD.Placement(shift, FreeCAD.Rotation())
                shapes.append(shape)
            obj.Shape = Shapes.compound(shapes)

            obj.Outfaces = trace(obj) if P.autotrace else []

        elif isDerivedFrom(obj, "Mesh::FeaturePython"):
            meshes = []
            for ftr in ftrs:
                mesh = meshOf(ftr, remeshed=True)
                center = Meshes.center(mesh)
                if center is None:
                    R = FreeCAD.Vector(0,0,0)
                else:
                    R = center - obj.Base
                shift = R*obj.Ratio - R
                mesh.translate(*shift)
                meshes.append(mesh)
            obj.Mesh = Meshes.compound(meshes)

        else:
            raise TypeError

    def _trace(self, obj):
        return subFaceLinksOf(obj.Origin)

class FeatureMaskViewProxy(DerivedFeatureViewProxy):
    def updateData(self, obj, p):
        DerivedFeatureViewProxy.updateData(self, obj, p)

        if obj.getTypeIdOfProperty(p) in ["App::PropertyLink", "App::PropertyLinkList"]:
            self.children = [obj.Origin] if obj.Origin is not None else []

class FeatureMaskProxy(WrappedFeatureProxy):
    @classmethod
    def featurePropertiesOf(clazz, obj=None, args={}):
        prop = {}
        prop["TypeId"] = clazz

        Origin = getattr(obj, "Origin", None)
        Masker = getattr(obj, "Masker", None)
        prop["Origin"] = args.get("Origin", Origin)
        prop["Masker"] = args.get("Masker", Masker)

        return prop

    def onChanged(self, obj, p):
        if p == "Proxy":
            if isDerivedFrom(obj, "Part::FeaturePython"):
                if "Outfaces" not in obj.PropertiesList:
                    obj.addProperty("App::PropertyPythonObject", "Outfaces")
                    obj.Outfaces = []
                    obj.setEditorMode("Outfaces", 2)

            if "Origin" not in obj.PropertiesList:
                obj.addProperty("App::PropertyLink", "Origin")
            if "Masker" not in obj.PropertiesList:
                obj.addProperty("App::PropertyLink", "Masker")
                obj.Masker = getViewBox(obj.Document)
            obj.setEditorMode("Placement", 2)
            if FreeCAD.GuiUp:
                obj.ViewObject.Proxy = FeatureMaskViewProxy()

    def execute(self, obj):
        if isDerivedFrom(obj, "Part::FeaturePython"):
            obj.Shape = Shapes.common([obj.Origin.Shape, obj.Masker.Shape])
            obj.Placement = FreeCAD.Placement()

            obj.Outfaces = trace(obj) if P.autotrace else []

        elif isDerivedFrom(obj, "Mesh::FeaturePython"):
            obj.Mesh = Meshes.common([meshOf(obj.Origin), meshOf(obj.Masker)])
            obj.Placement = FreeCAD.Placement()

        else:
            raise TypeError

Apart = FeatureApartProxy
Mask = FeatureMaskProxy


def apart(ftr, ratio=1.5, center=None):
    doc = ftr.Document

    if center is None:
        center = centerOf(ftr)
        if center is None:
            center = FreeCAD.Vector(0,0,0)

    return addObject(Apart, "Apart", rep=P.rep, doc=doc, cached=P.cached,
                     args=dict(Origin=ftr, Ratio=ratio, Base=center))

def mask(ftr):
    doc = ftr.Document

    return addObject(Mask, "Mask", rep=P.rep, doc=doc, cached=P.cached,
                     args=dict(Origin=ftr))

