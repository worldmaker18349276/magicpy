import FreeCAD, Units, Part, Mesh
from Geometric import Meshes
from Draft import select


# Property

def setGeometry(obj, geo):
    if isDerivedFrom(obj, "Part::FeaturePython"):
        obj.Shape = geo
        obj.Placement = geo.Placement
    elif isDerivedFrom(obj, "Mesh::FeaturePython"):
        obj.Mesh = geo
        obj.Placement = geo.Placement
    else:
        raise TypeError

def meshOf(obj, precision=0.01):
    if obj is None:
        return Mesh.Mesh()
    elif isDerivedFrom(obj, "Part::Feature"):
        return Mesh.Mesh(obj.Shape.tessellate(precision))
    elif isDerivedFrom(obj, "Mesh::Feature"):
        return obj.Mesh
    else:
        raise TypeError

def centerOf(obj):
    if obj is None:
        return FreeCAD.Vector()
    elif isDerivedFrom(obj, "Part::Feature"):
        R = FreeCAD.Vector()
        M = 0.0
        for sld in obj.Shape.Solids:
            R += sld.CenterOfMass*sld.Mass
            M += sld.Mass
        if M == 0.0:
            return None
        else:
            return R*(1/M)
    elif isDerivedFrom(obj, "Mesh::Feature"):
        return obj.Mesh.BoundBox.Center
    else:
        raise TypeError

def massOf(obj):
    if obj is None:
        return 0.0
    elif isDerivedFrom(obj, "Part::Feature"):
        M = 0.0
        for sld in obj.Shape.Solids:
            M += sld.Mass
        return M
    elif isDerivedFrom(obj, "Mesh::Feature"):
        M = 0.0
        for submesh in obj.Mesh.getSeparateComponents():
            if Meshes.orientation(submesh) == "Forward":
                M += submesh.Volume
            else:
                M -= submesh.Volume
        return M
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

    elif isDerivedFrom(ftrs, "Part::Compound"):
        return ftrs.Links

    elif isDerivedFrom(ftrs, "App::GeoFeature"):
        return [ftrs]

    else:
        raise TypeError

def ftrstr(*ftrs):
    return ", ".join("FreeCAD.ActiveDocument.%s"%ftr.Name for ftr in ftrs)


def addObject(TypeId, name, parent=None):
    if parent is None:
        parent = FreeCAD.ActiveDocument

    if isDerivedFrom(parent, "App::Document"):
        make = parent.addObject
    else:
        make = parent.newObject

    if isinstance(TypeId, str):
        obj = make(TypeId, name)
    else:
        obj = make("Part::FeaturePython", name)
        TypeId(obj)

    return obj

class ScriptedObjectProxy(object):
    pass

def typeOf(obj):
    if hasattr(obj, "Proxy") and obj.Proxy is not None and isinstance(obj.Proxy, ScriptedObjectProxy):
        return type(obj.Proxy)
    return getattr(obj, "TypeId", type(obj))

def isDerivedFrom(obj, typ):
    if isinstance(typ, (tuple, list)):
        return any(isDerivedFrom(obj, typ_i) for typ_i in typ)

    if not hasattr(obj, "isDerivedFrom"):
        return isinstance(typ, type) and isinstance(obj, typ)
    elif isinstance(typ, str):
        return obj.isDerivedFrom(typ)
    elif issubclass(typ, ScriptedObjectProxy):
        return hasattr(obj, "Proxy") and obj.Proxy is not None and isinstance(obj.Proxy, typ)
    else:
        return False

# len(obj.getPathsByOutList(father)) > 0
