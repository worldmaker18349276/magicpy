import FreeCAD, Units, Part, Mesh
from Geometric import Shapes, Meshes
from Draft import select

types = [
    "App::DocumentObject",
    "App::GeoFeature",
    "App::FeatureTest",
    "App::FeatureTestException",
    "App::FeaturePython",
    "App::GeometryPython",
    "App::DocumentObjectGroup",
    "App::DocumentObjectGroupPython",
    "App::DocumentObjectFileIncluded",
    "App::InventorObject",
    "App::VRMLObject",
    "App::Annotation",
    "App::AnnotationLabel",
    "App::MeasureDistance",
    "App::MaterialObject",
    "App::MaterialObjectPython",
    "App::TextDocument",
    "App::Placement",
    "App::OriginFeature",
    "App::Plane",
    "App::Line",
    "App::Part",
    "App::Origin",
    "Part::Feature",
    "Part::FeatureExt",
    "Part::BodyBase",
    "Part::FeaturePython",
    "Part::FeatureGeometrySet",
    "Part::CustomFeature",
    "Part::CustomFeaturePython",
    "Part::Primitive",
    "Part::Box",
    "Part::Spline",
    "Part::Boolean",
    "Part::Common",
    "Part::MultiCommon",
    "Part::Cut",
    "Part::Fuse",
    "Part::MultiFuse",
    "Part::Section",
    "Part::FilletBase",
    "Part::Fillet",
    "Part::Chamfer",
    "Part::Compound",
    "Part::Extrusion",
    "Part::Revolution",
    "Part::Mirroring",
    "Part::ImportStep",
    "Part::ImportIges",
    "Part::ImportBrep",
    "Part::CurveNet",
    "Part::Polygon",
    "Part::Circle",
    "Part::Ellipse",
    "Part::Vertex",
    "Part::Line",
    "Part::Ellipsoid",
    "Part::Plane",
    "Part::Sphere",
    "Part::Cylinder",
    "Part::Prism",
    "Part::RegularPolygon",
    "Part::Cone",
    "Part::Torus",
    "Part::Helix",
    "Part::Spiral",
    "Part::Wedge",
    "Part::Part2DObject",
    "Part::Part2DObjectPython",
    "Part::Face",
    "Part::RuledSurface",
    "Part::Loft",
    "Part::Sweep",
    "Part::Offset",
    "Part::Offset2D",
    "Part::Thickness",
    "Part::Datum",
    "Mesh::Feature",
    "Mesh::FeatureCustom",
    "Mesh::FeaturePython",
    "Mesh::Import",
    "Mesh::Export",
    "Mesh::Transform",
    "Mesh::TransformDemolding",
    "Mesh::Curvature",
    "Mesh::SegmentByMesh",
    "Mesh::SetOperations",
    "Mesh::FixDefects",
    "Mesh::HarmonizeNormals",
    "Mesh::FlipNormals",
    "Mesh::FixNonManifolds",
    "Mesh::FixDuplicatedFaces",
    "Mesh::FixDuplicatedPoints",
    "Mesh::FixDegenerations",
    "Mesh::FixDeformations",
    "Mesh::FixIndices",
    "Mesh::FillHoles",
    "Mesh::RemoveComponents",
    "Mesh::Sphere",
    "Mesh::Ellipsoid",
    "Mesh::Cylinder",
    "Mesh::Cone",
    "Mesh::Torus",
    "Mesh::Cube",
]

scripted_types = [
    "App::FeaturePython",
    "App::GeometryPython",
    "App::DocumentObjectGroupPython",
    "App::MaterialObjectPython",
    "Part::FeaturePython",
    "Part::CustomFeaturePython",
    "Part::RegularPolygon",
    "Part::Part2DObjectPython",
    "Mesh::FeaturePython",
]

geo_types = [
    "App::GeoFeature",
    "App::GeometryPython",
    "App::InventorObject",
    "App::VRMLObject",
    "App::Placement",
    "App::OriginFeature",
    "App::Plane",
    "App::Line",
    "App::Part",
    "Part::Feature",
    "Part::FeatureExt",
    "Part::BodyBase",
    "Part::FeaturePython",
    "Part::FeatureGeometrySet",
    "Part::CustomFeature",
    "Part::CustomFeaturePython",
    "Part::Primitive",
    "Part::Box",
    "Part::Spline",
    "Part::Boolean",
    "Part::Common",
    "Part::MultiCommon",
    "Part::Cut",
    "Part::Fuse",
    "Part::MultiFuse",
    "Part::Section",
    "Part::FilletBase",
    "Part::Fillet",
    "Part::Chamfer",
    "Part::Compound",
    "Part::Extrusion",
    "Part::Revolution",
    "Part::Mirroring",
    "Part::ImportStep",
    "Part::ImportIges",
    "Part::ImportBrep",
    "Part::CurveNet",
    "Part::Polygon",
    "Part::Circle",
    "Part::Ellipse",
    "Part::Vertex",
    "Part::Line",
    "Part::Ellipsoid",
    "Part::Plane",
    "Part::Sphere",
    "Part::Cylinder",
    "Part::Prism",
    "Part::RegularPolygon",
    "Part::Cone",
    "Part::Torus",
    "Part::Helix",
    "Part::Spiral",
    "Part::Wedge",
    "Part::Part2DObject",
    "Part::Part2DObjectPython",
    "Part::Face",
    "Part::RuledSurface",
    "Part::Loft",
    "Part::Sweep",
    "Part::Offset",
    "Part::Offset2D",
    "Part::Thickness",
    "Part::Datum",
    "Mesh::Feature",
    "Mesh::FeatureCustom",
    "Mesh::FeaturePython",
    "Mesh::Import",
    "Mesh::Transform",
    "Mesh::TransformDemolding",
    "Mesh::SegmentByMesh",
    "Mesh::SetOperations",
    "Mesh::FixDefects",
    "Mesh::HarmonizeNormals",
    "Mesh::FlipNormals",
    "Mesh::FixNonManifolds",
    "Mesh::FixDuplicatedFaces",
    "Mesh::FixDuplicatedPoints",
    "Mesh::FixDegenerations",
    "Mesh::FixDeformations",
    "Mesh::FixIndices",
    "Mesh::FillHoles",
    "Mesh::RemoveComponents",
    "Mesh::Sphere",
    "Mesh::Ellipsoid",
    "Mesh::Cylinder",
    "Mesh::Cone",
    "Mesh::Torus",
    "Mesh::Cube",
]

properties = [
    "App::PropertyBool",
    "App::PropertyBoolList",
    "App::PropertyFloat",
    "App::PropertyFloatList",
    "App::PropertyFloatConstraint",
    "App::PropertyPrecision",
    "App::PropertyQuantity",
    "App::PropertyQuantityConstraint",
    "App::PropertyAngle",
    "App::PropertyDistance",
    "App::PropertyLength",
    "App::PropertyArea",
    "App::PropertyVolume",
    "App::PropertySpeed",
    "App::PropertyAcceleration",
    "App::PropertyForce",
    "App::PropertyPressure",
    "App::PropertyInteger",
    "App::PropertyIntegerConstraint",
    "App::PropertyPercent",
    "App::PropertyEnumeration",
    "App::PropertyIntegerList",
    "App::PropertyIntegerSet",
    "App::PropertyMap",
    "App::PropertyString",
    "App::PropertyUUID",
    "App::PropertyFont",
    "App::PropertyStringList",
    "App::PropertyLink",
    "App::PropertyLinkChild",
    "App::PropertyLinkGlobal",
    "App::PropertyLinkSub",
    "App::PropertyLinkSubChild",
    "App::PropertyLinkSubGlobal",
    "App::PropertyLinkList",
    "App::PropertyLinkListChild",
    "App::PropertyLinkListGlobal",
    "App::PropertyLinkSubList",
    "App::PropertyLinkSubListChild",
    "App::PropertyLinkSubListGlobal",
    "App::PropertyMatrix",
    "App::PropertyVector",
    "App::PropertyVectorDistance",
    "App::PropertyPosition",
    "App::PropertyDirection",
    "App::PropertyVectorList",
    "App::PropertyPlacement",
    "App::PropertyPlacementList",
    "App::PropertyPlacementLink",
    "App::PropertyColor",
    "App::PropertyColorList",
    "App::PropertyMaterial",
    "App::PropertyMaterialList",
    "App::PropertyPath",
    "App::PropertyFile",
    "App::PropertyFileIncluded",
    "App::PropertyPythonObject",
    "App::PropertyExpressionEngine",
    "Part::PropertyPartShape",
    "Part::PropertyGeometryList",
    "Part::PropertyShapeHistory",
    "Part::PropertyFilletEdges",
    "Mesh::PropertyNormalList",
    "Mesh::PropertyCurvatureList",
    "Mesh::PropertyMeshKernel",
]


# Property

def setGeometry(obj, geo):
    if isDerivedFrom(obj, "Part::FeaturePython"):
        obj.Shape = geo
        obj.Placement = geo.Placement
    elif isDerivedFrom(obj, "Mesh::FeaturePython"):
        obj.Mesh = geo
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


class PartFeaturePythonViewProxy(object):
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
    def getTypeId(clz):
        return "App::FeaturePython"

    @classmethod
    def createObject(clz, name, doc=None, **kwargs):
        if doc is None:
            doc = FreeCAD.ActiveDocument
        proxy = clz(**kwargs)
        obj = doc.addObject(proxy.getTypeId(), name)
        obj.Proxy = proxy
        return obj

    def createViewProxy(self):
        return None

    def onChanged(self, obj, p):
        if p == "Proxy":
            self.init(obj)
            if FreeCAD.GuiUp:
                obj.ViewObject.Proxy = self.createViewProxy()

    def execute(self, obj):
        pass

def typeOf(obj):
    if any(obj.isDerivedFrom(t) for t in scripted_types):
        return type(obj.Proxy)
    else:
        return getattr(obj, "TypeId", type(obj))

def isDerivedFrom(obj, typ):
    if isinstance(typ, (tuple, list)):
        return any(isDerivedFrom(obj, typ_i) for typ_i in typ)

    if not hasattr(obj, "isDerivedFrom"):
        return isinstance(typ, type) and isinstance(obj, typ)
    elif isinstance(typ, str):
        return obj.isDerivedFrom(typ)
    elif issubclass(typ, FeaturePythonProxy):
        return obj.isDerivedFrom(typ.FeaturePythonProxy.gettyp()) and isinstance(obj.Proxy, typ)
    else:
        return False

# len(obj.getPathsByOutList(father)) > 0
