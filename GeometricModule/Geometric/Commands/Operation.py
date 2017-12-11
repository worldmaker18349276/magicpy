import FreeCAD, FreeCADGui, Draft
from Geometric.Features import *


class CommonCommand(object):
    def GetResources(self):
        return {"Pixmap"  : "Geometric_common.png",
                "MenuText": "common",
                "ToolTip" : "make an intersection of several shapes"}

    def Activated(self):
        sel = distinct_list(FreeCADGui.Selection.getSelection())
        FreeCADGui.doCommand("Geometric.common(%s)"%ftrstr(*sel))
        FreeCADGui.doCommand("FreeCAD.ActiveDocument.recompute()")
        FreeCADGui.doCommand("FreeCADGui.SendMsgToActiveView('ViewFit')")

    def IsActive(self):
        return len(FreeCADGui.Selection.getSelection()) > 1

class FuseCommand(object):
    def GetResources(self):
        return {"Pixmap"  : "Geometric_fuse.png",
                "MenuText": "fuse",
                "ToolTip" : "make an union of several shapes"}

    def Activated(self):
        sel = distinct_list(FreeCADGui.Selection.getSelection())
        FreeCADGui.doCommand("Geometric.fuse(%s)"%ftrstr(*sel))
        FreeCADGui.doCommand("FreeCAD.ActiveDocument.recompute()")
        FreeCADGui.doCommand("FreeCADGui.SendMsgToActiveView('ViewFit')")

    def IsActive(self):
        return len(FreeCADGui.Selection.getSelection()) > 1

class ComplementCommand(object):
    def GetResources(self):
        return {"Pixmap"  : "Geometric_complement.png",
                "MenuText": "complement",
                "ToolTip" : "make a complement of shape"}

    def Activated(self):
        sel = FreeCADGui.Selection.getSelection()[0]
        FreeCADGui.doCommand("Geometric.complement(%s)"%ftrstr(sel))
        FreeCADGui.doCommand("FreeCAD.ActiveDocument.recompute()")
        FreeCADGui.doCommand("FreeCADGui.SendMsgToActiveView('ViewFit')")

    def IsActive(self):
        return len(FreeCADGui.Selection.getSelection()) == 1

class TransformCommand(object):
    def GetResources(self):
        return {"Pixmap"  : "Geometric_transform.png",
                "MenuText": "transform",
                "ToolTip" : "make a transformation of shape"}

    def Activated(self):
        sel = FreeCADGui.Selection.getSelection()[0]
        FreeCADGui.doCommand("Geometric.transform(%s)"%ftrstr(sel))
        FreeCADGui.doCommand("FreeCAD.ActiveDocument.recompute()")
        FreeCADGui.doCommand("FreeCADGui.SendMsgToActiveView('ViewFit')")

    def IsActive(self):
        return len(FreeCADGui.Selection.getSelection()) == 1


class GroupCommand(object):
    def GetResources(self):
        return {"Pixmap"  : "Geometric_group.png",
                "MenuText": "group",
                "ToolTip" : "make a group of several shapes"}

    def Activated(self):
        sel = FreeCADGui.Selection.getSelection()
        FreeCADGui.doCommand("Geometric.group(%s)"%ftrstr(*sel))

    def IsActive(self):
        return len(FreeCADGui.Selection.getSelection()) >= 0

class MaskCommand(object):
    def GetResources(self):
        return {"Pixmap"  : "Geometric_mask.png",
                "MenuText": "mask",
                "ToolTip" : "make a mask of several shapes"}

    def Activated(self):
        target = FreeCADGui.Selection.getSelection()[0]
        sel = distinct_list(FreeCADGui.Selection.getSelection()[1:])
        FreeCADGui.doCommand("Geometric.group_mask(%s, %s)"%(ftrstr(target), ftrstr(*sel)))
        FreeCADGui.doCommand("FreeCAD.ActiveDocument.recompute()")
        FreeCADGui.doCommand("FreeCADGui.SendMsgToActiveView('ViewFit')")

    def IsActive(self):
        return len(FreeCADGui.Selection.getSelection()) > 0

class SliceCommand(object):
    def GetResources(self):
        return {"Pixmap"  : "Geometric_slice.png",
                "MenuText": "slice",
                "ToolTip" : "make a slice of several shapes"}

    def Activated(self):
        target = FreeCADGui.Selection.getSelection()[0]
        sel = distinct_list(FreeCADGui.Selection.getSelection()[1:])
        FreeCADGui.doCommand("Geometric.group_slice(%s, %s)"%(ftrstr(target), ftrstr(*sel)))
        FreeCADGui.doCommand("FreeCAD.ActiveDocument.recompute()")
        FreeCADGui.doCommand("FreeCADGui.SendMsgToActiveView('ViewFit')")

    def IsActive(self):
        return len(FreeCADGui.Selection.getSelection()) > 0


class ViewGroupCommand(object):
    def GetResources(self):
        return {"Pixmap"  : ":/icons/Geometric_adjust_viewbox.svg",
                "MenuText": "add view group",
                "ToolTip" : "add view group"}

    def Activated(self):
        FreeCADGui.doCommand("_ftr = FreeCAD.ActiveDocument.addObject('App::DocumentObjectGroupPython', 'ViewGroup')")
        FreeCADGui.doCommand("Geometric.ViewGroup(_ftr)")

    def IsActive(self):
        return FreeCAD.ActiveDocument is not None


FreeCADGui.addCommand("Geometric_common", CommonCommand())
FreeCADGui.addCommand("Geometric_fuse", FuseCommand())
FreeCADGui.addCommand("Geometric_complement", ComplementCommand())
FreeCADGui.addCommand("Geometric_transform", TransformCommand())
FreeCADGui.addCommand("Geometric_group", GroupCommand())
FreeCADGui.addCommand("Geometric_mask", MaskCommand())
FreeCADGui.addCommand("Geometric_slice", SliceCommand())
FreeCADGui.addCommand("Geometric_viewgroup", ViewGroupCommand())

oplist = ["Geometric_common",
          "Geometric_fuse",
          "Geometric_complement",
          "Geometric_transform",
          "Geometric_group",
          "Geometric_mask",
          "Geometric_slice",
          "Geometric_viewgroup",
        ]

