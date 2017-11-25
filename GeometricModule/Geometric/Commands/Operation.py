import FreeCAD, FreeCADGui, Draft
from Geometric.Features import *


class CommonCommand(object):
    def GetResources(self):
        return {"Pixmap"  : "MagicPart_common.png",
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
        return {"Pixmap"  : "MagicPart_fuse.png",
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
        return {"Pixmap"  : "MagicPart_complement.png",
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
        return {"Pixmap"  : "MagicPart_transform.png",
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
        return {"Pixmap"  : "MagicPart_group.png",
                "MenuText": "group",
                "ToolTip" : "make a group of several shapes"}

    def Activated(self):
        sel = FreeCADGui.Selection.getSelection()
        FreeCADGui.doCommand("Geometric.group(%s)"%ftrstr(*sel))

    def IsActive(self):
        return len(FreeCADGui.Selection.getSelection()) >= 0

class MaskCommand(object):
    def GetResources(self):
        return {"Pixmap"  : "MagicPart_mask.png",
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
        return {"Pixmap"  : "MagicPart_slice.png",
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


FreeCADGui.addCommand("Geometric_common", CommonCommand())
FreeCADGui.addCommand("Geometric_fuse", FuseCommand())
FreeCADGui.addCommand("Geometric_complement", ComplementCommand())
FreeCADGui.addCommand("Geometric_transform", TransformCommand())
FreeCADGui.addCommand("Geometric_group", GroupCommand())
FreeCADGui.addCommand("Geometric_mask", MaskCommand())
FreeCADGui.addCommand("Geometric_slice", SliceCommand())

oplist = ["Geometric_common",
          "Geometric_fuse",
          "Geometric_complement",
          "Geometric_transform",
          "Geometric_group",
          "Geometric_mask",
          "Geometric_slice"]

