from itertools import islice
from MagicPart.Features.Utilities import *
from MagicPart import Shapes


def subFaceLinksOf(obj):
    return [(obj, "Face%s"%(i+1)) for i in range(len(obj.Shape.Faces))]

def subShapeOf(link):
    if link is None:
        return None

    if link[1].startswith("Face") or link[1].startswith("Edge") or link[1].startswith("Vertex"):
        return getattr(link[0].Shape, link[1])
    elif link[1] == "Shape":
        return link[0].Shape
    else:
        raise TypeError

def subColorOf(link, default=(0.8,0.8,0.8,0.0)):
    if link is None:
        return default

    if link[1].startswith("Face"):
        return diffuseColorOf(link[0])[int(link[1][4:])-1]
    else:
        raise TypeError


def _trace(obj, outobjs=None, N=4):
    if outobjs is None:
        outobjs = ftrlist(obj.OutList)

    outinds = Shapes.trace(obj.Shape, [outobj.Shape for outobj in outobjs], N)
    links = [subFaceLinksOf(outobj) for outobj in outobjs]
    outlinks = [links[ind[0]][ind[1]] if ind is not None else None for ind in outinds]

    return outlinks

def trace(obj):
    if isDerivedFrom(obj, "Part::Compound"):
        return [link for outobj in obj.Links for link in subFaceLinksOf(outobj)]

    elif isDerivedFrom(obj, "Part::FeaturePython") and hasattr(obj.Proxy, "_trace"):
        return obj.Proxy._trace(obj)

    else:
        return _trace(obj)

def outFaceLinksOf(obj, traced=True):
    if "Outfaces" in obj.PropertiesList:
        if obj.Outfaces == []:
            if traced:
                obj.Outfaces = trace(obj)
            else:
                return []

        return obj.Outfaces

    else:
        if traced:
            return trace(obj)
        else:
            return []

def outOf(link):
    if link is None:
        return None
    if not link[1].startswith("Face"):
        raise TypeError
    outlinks = outFaceLinksOf(link[0])
    if len(outlinks) == 0:
        raise ValueError
    return outlinks[int(link[1][4:])-1]


def getSubSelection():
    import FreeCADGui
    sobjs = FreeCADGui.Selection.getSelectionEx()
    subsel = []
    for sobj in sobjs:
        if sobj.HasSubObjects:
            for field in sobj.SubElementNames:
                subsel.append((sobj.Object, field))

        else:
            subsel.append((sobj.Object, "Shape"))
    return subsel

def shiftToChildren():
    import FreeCADGui
    sobjs = FreeCADGui.Selection.getSelectionEx()
    FreeCADGui.Selection.clearSelection()
    for sobj in sobjs:
        if sobj.HasSubObjects:
            no_children = True
            for field, v in zip(sobj.SubElementNames, sobj.PickedPoints):
                outlink = outOf((sobj.Object, field))
                if outlink is not None:
                    no_children = False
                    FreeCADGui.Selection.addSelection(outlink[0], outlink[1], v.x, v.y, v.z)
            if no_children:
                FreeCADGui.Selection.addSelection(sobj.Object)

        else:
            if len(sobj.Object.OutList) == 0:
                FreeCADGui.Selection.addSelection(sobj.Object)
            for outobj in sobj.Object.OutList:
                FreeCADGui.Selection.addSelection(outobj)

