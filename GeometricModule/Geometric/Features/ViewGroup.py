import FreeCAD, Part
from Geometric.Basic import *
from Geometric.Features.Utilities import *
from Geometric.Features.Primitive import PrimitiveProxy, UnboundedPrimitiveProxy
from Geometric.Features.Operation import ComplementProxy


class ViewGroupProxy(object):
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

    def execute(self, obj):
        bb_ = FreeCAD.BoundBox(obj.Min, obj.Max)
        bb = FreeCAD.BoundBox(bb_)
        bb.enlarge(-obj.Margin)
        for ftr in obj.Group:
            ftr_bb = self.getBoundBox(ftr)
            if ftr_bb.isValid() and ftr_bb.DiagonalLength != float('inf'):
                bb.add(ftr_bb)
        bb.enlarge(obj.Margin)

        self.setBoundBox(obj, bb)
        for ftr in obj.Group:
            self.setBoundBox(ftr, bb)
        # if not fuzzyCompare(bb, bb_):
        #     self.setBoundBox(obj, bb)
        #     for ftr in obj.Group:
        #         self.setBoundBox(ftr, bb)

    def isBounded(self, ftr):
        if isDerivedFrom(ftr, "Part::Common"):
            return self.isBounded(ftr.Base) or self.isBounded(ftr.Tool)
        elif isDerivedFrom(ftr, "Part::Fuse"):
            return self.isBounded(ftr.Base) and self.isBounded(ftr.Tool)
        elif isDerivedFrom(ftr, "Part::Cut"):
            return self.isBounded(ftr.Base)
        elif isDerivedFrom(ftr, "Part::MultiCommon"):
            return any(self.isBounded(sub) for sub in ftr.Shapes)
        elif isDerivedFrom(ftr, "Part::MultiFuse"):
            return all(self.isBounded(sub) for sub in ftr.Shapes)
        elif isDerivedFrom(ftr, "Part::Compound"):
            return all(self.isBounded(sub) for sub in ftr.Links)
        elif isDerivedFrom(ftr, "Part::Mirroring"):
            return self.isBounded(ftr.Source)
        elif isDerivedFrom(ftr, "Part::Primitive"):
            return True
        elif isDerivedFrom(ftr, ComplementProxy):
            return False
        elif isDerivedFrom(ftr, UnboundedPrimitiveProxy):
            return False
        elif isDerivedFrom(ftr, PrimitiveProxy):
            return True
        else:
            return False

    def getBoundBox(self, ftr):
        if isDerivedFrom(ftr, "Part::Common"):
            bb = self.getBoundBox(ftr.Base)
            bb.intersected(self.getBoundBox(ftr.Tool))
            bb = bb.transformed(ftr.Placement.toMatrix())
            return bb

        elif isDerivedFrom(ftr, "Part::Fuse"):
            bb = self.getBoundBox(ftr.Base)
            bb.add(self.getBoundBox(ftr.Tool))
            bb = bb.transformed(ftr.Placement.toMatrix())
            return bb

        elif isDerivedFrom(ftr, "Part::Cut"):
            return self.getBoundBox(ftr.Base)

        elif isDerivedFrom(ftr, "Part::MultiCommon"):
            bb = self.getBoundBox(ftr.Shapes[0])
            for sub in ftr.Shapes[1:]:
                bb.intersected(self.getBoundBox(sub))
            bb = bb.transformed(ftr.Placement.toMatrix())
            return bb

        elif isDerivedFrom(ftr, "Part::MultiFuse"):
            bb = self.getBoundBox(ftr.Shapes[0])
            for sub in ftr.Shapes[1:]:
                bb.add(self.getBoundBox(sub))
            bb = bb.transformed(ftr.Placement.toMatrix())
            return bb

        elif isDerivedFrom(ftr, "Part::Compound"):
            bb = self.getBoundBox(ftr.Links[0])
            for sub in ftr.Links[1:]:
                bb.add(self.getBoundBox(sub))
            bb = bb.transformed(ftr.Placement.toMatrix())
            return bb

        elif isDerivedFrom(ftr, "Part::Mirroring"):
            bb = self.getBoundBox(ftr.Source)
            bb = bb.transformed(mirror(ftr.Base, ftr.Normal))
            bb = bb.transformed(ftr.Placement.toMatrix())
            bb = FreeCAD.BoundBox(bb.getPoint(2), bb.getPoint(4))
            return bb

        elif isDerivedFrom(ftr, [ComplementProxy, UnboundedPrimitiveProxy]):
            bb = FreeCAD.BoundBox()
            bb.scale(-1,-1,-1)
            return bb

        elif isDerivedFrom(ftr, ["Part::Primitive", PrimitiveProxy]):
            return boundBoxOf(ftr)

        else:
            return FreeCAD.BoundBox()

    def setBoundBox(self, ftr, bb):
        if "Min" in ftr.PropertiesList and ftr.getGroupOfProperty("Min") == "ViewBox":
            if not fuzzyCompare(ftr.Min, bb.getPoint(4)):
                ftr.Min = bb.getPoint(4)
            if not fuzzyCompare(ftr.Max, bb.getPoint(2)):
                ftr.Max = bb.getPoint(2)

        elif isDerivedFrom(ftr, ["Part::Common", "Part::Fuse", "Part::Cut"]):
            bb_ = bb.transformed(ftr.Placement.inverse().toMatrix())
            self.setBoundBox(ftr.Base, bb_)
            self.setBoundBox(ftr.Tool, bb_)

        elif isDerivedFrom(ftr, ["Part::MultiCommon", "Part::MultiFuse"]):
            bb_ = bb.transformed(ftr.Placement.inverse().toMatrix())
            for outftr in ftr.Shapes:
                self.setBoundBox(outftr, bb_)

        elif isDerivedFrom(ftr, "Part::Compound"):
            bb_ = bb.transformed(ftr.Placement.inverse().toMatrix())
            for outftr in ftr.Shapes:
                self.setBoundBox(outftr, bb_)

        elif isDerivedFrom(ftr, "Part::Mirroring"):
            bb_ = bb.transformed(ftr.Placement.inverse().toMatrix())
            bb_ = bb_.transformed(mirror(ftr.Base, ftr.Normal))
            self.setBoundBox(ftr.Source, bb_)

ViewGroup = ViewGroupProxy


# def hideAllUnbounded():
#     for obj in FreeCAD.ActiveDocument.Objects:
#         if not isBounded(obj):
#             obj.ViewObject.hide()
# 
# def viewAllBounded():
#     import FreeCADGui
#     unbounded = set()
#     for obj in FreeCAD.ActiveDocument.Objects:
#         if obj.ViewObject.Visibility and not isBounded(obj):
#             unbounded.add(obj)
# 
#     for obj in unbounded:
#         obj.ViewObject.hide()
#     FreeCADGui.SendMsgToActiveView("ViewFit")
#     for obj in unbounded:
#         obj.ViewObject.show()
# 
# def viewBoundedSelections():
#     import FreeCADGui
#     unbounded = set()
#     for obj in set(FreeCADGui.Selection.getSelection()):
#         if obj.ViewObject.Visibility and not isBounded(obj):
#             unbounded.add(obj)
# 
#     for obj in unbounded:
#         obj.ViewObject.hide()
#     FreeCADGui.SendMsgToActiveView("ViewSelection")
#     for obj in unbounded:
#         obj.ViewObject.show()
