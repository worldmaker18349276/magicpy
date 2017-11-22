import FreeCAD, Units, Part, Mesh
from Geometric import Shapes, Meshes
from Draft import select


# Property

def setView(obj, view):
    if isDerivedFrom(obj, "Part::FeaturePython"):
        obj.Shape = view
        obj.Placement = view.Placement
    elif isDerivedFrom(obj, "Mesh::FeaturePython"):
        obj.Mesh = view
        obj.Placement = view.Placement
    else:
        raise TypeError

def meshOf(obj, precision=0.01):
    if obj is None:
        return Mesh.Mesh()
    elif isDerivedFrom(obj, "Part::Feature"):
        return Meshes.asMesh(obj.Shape, precision=precision)
    elif isDerivedFrom(obj, "Mesh::Feature"):
        return obj.Mesh
    else:
        raise TypeError

def centerOf(obj):
    if obj is None:
        return FreeCAD.Vector()
    elif isDerivedFrom(obj, "Part::Feature"):
        return Shapes.center(obj.Shape)
    elif isDerivedFrom(obj, "Mesh::Feature"):
        return Meshes.center(obj.Mesh)
    else:
        raise TypeError

def massOf(obj):
    if obj is None:
        return 0.0
    elif isDerivedFrom(obj, "Part::Feature"):
        return Shapes.mass(obj.Shape)
    elif isDerivedFrom(obj, "Mesh::Feature"):
        return Meshes.mass(obj.Mesh)
    else:
        raise TypeError

def boundBoxOf(obj):
    if obj is None:
        return FreeCAD.BoundBox()
    elif isDerivedFrom(obj, "Part::Feature"):
        if obj.Shape.isNull():
            return FreeCAD.BoundBox()
        else:
            return obj.Shape.BoundBox
    elif isDerivedFrom(obj, "Mesh::Feature"):
        if obj.Mesh.Volume == 0:
            return FreeCAD.BoundBox()
        else:
            return obj.Mesh.BoundBox
    else:
        raise TypeError

def diffuseColorOf(obj):
    clrs = obj.ViewObject.DiffuseColor
    if len(clrs) != len(obj.Shape.Faces):
        clr = obj.ViewObject.ShapeColor[:3] + (obj.ViewObject.Transparency/100.,)
        clrs = [clr]*len(obj.Shape.Faces)
    return clrs


# Feature

def distinct_list(ls):
    ls_ = []
    for e in ls:
        if e in ls_:
            ls_.remove(e)
        ls_.append(e)
    return ls_

def ftrlist(ftrs):
    if hasattr(ftrs, "__iter__"):
        return list(ftrs)

    elif isDerivedFrom(ftrs, "App::DocumentObjectGroup"):
        return ftrs.Group

    elif isDerivedFrom(ftrs, "App::GeoFeature"):
        return [ftrs]

    else:
        raise TypeError

def ftrstr(*ftrs):
    return ", ".join("FreeCAD.ActiveDocument.%s"%ftr.Name for ftr in ftrs)


class FeaturePythonViewProxy(object):
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

class FeaturePythonProxy(object):
    @classmethod
    def featurePropertiesOf(clazz, obj=None, args={}):
        prop = {}
        prop["TypeId"] = clazz
        return prop

    def onChanged(self, obj, p):
        if p == "Proxy":
            obj.setEditorMode("Placement", 2)
            if FreeCAD.GuiUp:
                obj.ViewObject.Proxy = FeaturePythonViewProxy()

    def execute(self, obj):
        pass


def typeIdOf(obj):
    if obj.isDerivedFrom("Part::FeaturePython") or obj.isDerivedFrom("Mesh::FeaturePython"):
        return type(obj.Proxy)
    else:
        return getattr(obj, "TypeId", type(obj))

def isDerivedFrom(obj, TypeId):
    if isinstance(TypeId, (tuple, list)):
        return any(isDerivedFrom(obj, TypeId_i) for TypeId_i in TypeId)

    if not hasattr(obj, "isDerivedFrom"):
        return isinstance(TypeId, type) and isinstance(obj, TypeId)
    elif isinstance(TypeId, str):
        return obj.isDerivedFrom(TypeId)
    elif issubclass(TypeId, FeaturePythonProxy):
        if obj.isDerivedFrom("Part::FeaturePython") or obj.isDerivedFrom("Mesh::FeaturePython"):
            return isinstance(obj.Proxy, TypeId)
        else:
            return False
    else:
        return False

def isDependOn(obj, father):
    if obj is None:
        return False
    elif obj == father:
        return True
    else:
        return any(isDependOn(outobj, father) for outobj in obj.OutList)

def featurePropertiesOf(obj, args={}):
    if isinstance(obj, str):
        ftr = None
        TypeId = obj
    elif isinstance(obj, type) and issubclass(obj, FeaturePythonProxy):
        ftr = None
        TypeId = obj
    elif isDerivedFrom(obj, "App::GeoFeature"):
        ftr = obj
        TypeId = typeIdOf(obj)
    else:
        raise TypeError

    prop = {}
    prop["TypeId"] = TypeId

    if TypeId == "Part::Compound":
        Links = getattr(ftr, "Links", [])
        Placement = getattr(ftr, "Placement", FreeCAD.Placement())
        prop["Links"] = sorted(args.get("Links", Links), key=hash)
        prop["Placement"] = args.get("Placement", Placement)

    elif TypeId in ["Part::MultiCommon", "Part::MultiFuse"]:
        Shapes = getattr(ftr, "Shapes", [])
        Placement = getattr(ftr, "Placement", FreeCAD.Placement())
        prop["Shapes"] = sorted(args.get("Shapes", Shapes), key=hash)
        prop["Placement"] = args.get("Placement", Placement)

    elif TypeId in ["Part::Cut", "Part::Fuse", "Part::Common"]:
        Base = getattr(ftr, "Base", None)
        Tool = getattr(ftr, "Tool", None)
        Placement = getattr(ftr, "Placement", FreeCAD.Placement())
        prop["Base"] = args.get("Base", Base)
        prop["Tool"] = args.get("Tool", Tool)
        prop["Placement"] = args.get("Placement", Placement)

    elif TypeId == "Part::Box":
        Length = getattr(ftr, "Length", Units.Quantity("10 mm"))
        Width = getattr(ftr, "Width", Units.Quantity("10 mm"))
        Height = getattr(ftr, "Height", Units.Quantity("10 mm"))
        Placement = getattr(ftr, "Placement", FreeCAD.Placement())
        prop["Length"] = args.get("Length", Length)
        prop["Width"] = args.get("Width", Width)
        prop["Height"] = args.get("Height", Height)
        prop["Placement"] = args.get("Placement", Placement)

    elif TypeId == "Part::Sphere":
        Radius = getattr(ftr, "Radius", Units.Quantity("5 mm"))
        Angle1 = getattr(ftr, "Angle1", Units.Quantity("-90 deg"))
        Angle2 = getattr(ftr, "Angle2", Units.Quantity("90 deg"))
        Angle3 = getattr(ftr, "Angle3", Units.Quantity("360 deg"))
        Placement = getattr(ftr, "Placement", FreeCAD.Placement())
        prop["Radius"] = args.get("Radius", Radius)
        prop["Angle1"] = args.get("Angle1", Angle1)
        prop["Angle2"] = args.get("Angle2", Angle2)
        prop["Angle3"] = args.get("Angle3", Angle3)
        prop["Placement"] = args.get("Placement", Placement)

    elif TypeId == "Part::Cylinder":
        Radius = getattr(ftr, "Radius", Units.Quantity("2 mm"))
        Height = getattr(ftr, "Height", Units.Quantity("10 mm"))
        Angle = getattr(ftr, "Angle", Units.Quantity("360 deg"))
        Placement = getattr(ftr, "Placement", FreeCAD.Placement())
        prop["Radius"] = args.get("Radius", Radius)
        prop["Height"] = args.get("Height", Height)
        prop["Angle"] = args.get("Angle", Angle)
        prop["Placement"] = args.get("Placement", Placement)

    elif TypeId == "Part::Cone":
        Radius1 = getattr(ftr, "Radius1", Units.Quantity("2 mm"))
        Radius2 = getattr(ftr, "Radius2", Units.Quantity("4 mm"))
        Height = getattr(ftr, "Height", Units.Quantity("10 mm"))
        Angle = getattr(ftr, "Angle", Units.Quantity("360 deg"))
        Placement = getattr(ftr, "Placement", FreeCAD.Placement())
        prop["Radius1"] = args.get("Radius1", Radius1)
        prop["Radius2"] = args.get("Radius2", Radius2)
        prop["Height"] = args.get("Height", Height)
        prop["Angle"] = args.get("Angle", Angle)
        prop["Placement"] = args.get("Placement", Placement)

    elif TypeId == "Part::Torus":
        Radius1 = getattr(ftr, "Radius1", Units.Quantity("10 mm"))
        Radius2 = getattr(ftr, "Radius2", Units.Quantity("2 mm"))
        Angle1 = getattr(ftr, "Angle1", Units.Quantity("-180 deg"))
        Angle2 = getattr(ftr, "Angle2", Units.Quantity("180 deg"))
        Angle3 = getattr(ftr, "Angle3", Units.Quantity("360 deg"))
        Placement = getattr(ftr, "Placement", FreeCAD.Placement())
        prop["Radius1"] = args.get("Radius1", Radius1)
        prop["Radius2"] = args.get("Radius2", Radius2)
        prop["Angle1"] = args.get("Angle1", Angle1)
        prop["Angle2"] = args.get("Angle2", Angle2)
        prop["Angle3"] = args.get("Angle3", Angle3)
        prop["Placement"] = args.get("Placement", Placement)

    elif isinstance(TypeId, type) and issubclass(TypeId, FeaturePythonProxy):
        prop = TypeId.featurePropertiesOf(ftr, args=args)

    else:
        raise TypeError

    return prop

def addObject(TypeId, name, rep="Shape", parent=None, args={}):
    if parent is None:
        parent = None
        doc = FreeCAD.ActiveDocument
    elif isDerivedFrom(parent, "App::Document"):
        parent = None
        doc = parent
    elif isDerivedFrom(parent, "App::DocumentObjectGroup"):
        doc = parent.Document
    else:
        raise TypeError

    if isinstance(TypeId, str):
        obj = doc.addObject(TypeId, name)
    else:
        if rep == "Shape":
            obj = doc.addObject("Part::FeaturePython", name)
        elif rep == "Mesh":
            obj = doc.addObject("Mesh::FeaturePython", name)
        else:
            raise TypeError
        obj.Proxy = TypeId()

    for k, v in args.items():
        if k in obj.PropertiesList:
            setattr(obj, k, v)
        else:
            getattr(obj.Proxy, "set"+k)(obj, v)

    if parent is not None:
        parent.addObject(obj)
    return obj

