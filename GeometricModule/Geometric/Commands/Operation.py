import FreeCAD, FreeCADGui, Draft
from Geometric.Features import *


class CommonCommand(object):
    def GetResources(self):
        return {"Pixmap"  : "Geometric_common.png",
                "MenuText": "common",
                "ToolTip" : "make an intersection of several shapes"}

    def Activated(self):
        sel = distinct_list(FreeCADGui.Selection.getSelection())
        FreeCADGui.doCommand("_ftr = Geometric.common(%s)"%ftrstr(*sel))
        viewGroup = FreeCADGui.activeView().getActiveObject("viewGroup")
        if viewGroup is not None:
            FreeCADGui.doCommand("FreeCAD.ActiveDocument.%s.addObject(_ftr)"%viewGroup.Name)
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
        FreeCADGui.doCommand("_ftr = Geometric.fuse(%s)"%ftrstr(*sel))
        viewGroup = FreeCADGui.activeView().getActiveObject("viewGroup")
        if viewGroup is not None:
            FreeCADGui.doCommand("FreeCAD.ActiveDocument.%s.addObject(_ftr)"%viewGroup.Name)
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
        FreeCADGui.doCommand("_ftr = Geometric.complement(%s)"%ftrstr(sel))
        viewGroup = FreeCADGui.activeView().getActiveObject("viewGroup")
        if viewGroup is not None:
            FreeCADGui.doCommand("FreeCAD.ActiveDocument.%s.addObject(_ftr)"%viewGroup.Name)
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
        FreeCADGui.doCommand("_ftr = Geometric.transform(%s)"%ftrstr(sel))
        viewGroup = FreeCADGui.activeView().getActiveObject("viewGroup")
        if viewGroup is not None:
            FreeCADGui.doCommand("FreeCAD.ActiveDocument.%s.addObject(_ftr)"%viewGroup.Name)
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
        FreeCADGui.doCommand("_ftr = Geometric.group(%s)"%ftrstr(*sel))
        viewGroup = FreeCADGui.activeView().getActiveObject("viewGroup")
        if viewGroup is not None:
            FreeCADGui.doCommand("FreeCAD.ActiveDocument.%s.addObject(_ftr)"%viewGroup.Name)

    def IsActive(self):
        return len(FreeCADGui.Selection.getSelection()) >= 0

class GroupCommonCommand(object):
    def GetResources(self):
        return {"Pixmap"  : "Geometric_mask.png",
                "MenuText": "group common",
                "ToolTip" : "make a common of several shapes"}

    def Activated(self):
        target = FreeCADGui.Selection.getSelection()[0]
        sel = distinct_list(FreeCADGui.Selection.getSelection()[1:])
        FreeCADGui.doCommand("Geometric.group_common(%s, %s)"%(ftrstr(target), ftrstr(*sel)))
        FreeCADGui.doCommand("FreeCAD.ActiveDocument.recompute()")
        FreeCADGui.doCommand("FreeCADGui.SendMsgToActiveView('ViewFit')")

    def IsActive(self):
        return len(FreeCADGui.Selection.getSelection()) > 0

class GroupSliceCommand(object):
    def GetResources(self):
        return {"Pixmap"  : "Geometric_slice.png",
                "MenuText": "group slice",
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
        FreeCADGui.doCommand("FreeCADGui.activeView().setActiveObject('viewGroup', _ftr)")

    def IsActive(self):
        return FreeCAD.ActiveDocument is not None


FreeCADGui.addCommand("Geometric_common", CommonCommand())
FreeCADGui.addCommand("Geometric_fuse", FuseCommand())
FreeCADGui.addCommand("Geometric_complement", ComplementCommand())
FreeCADGui.addCommand("Geometric_transform", TransformCommand())
FreeCADGui.addCommand("Geometric_group", GroupCommand())
FreeCADGui.addCommand("Geometric_common", GroupCommonCommand())
FreeCADGui.addCommand("Geometric_slice", GroupSliceCommand())
FreeCADGui.addCommand("Geometric_viewgroup", ViewGroupCommand())

oplist = ["Geometric_common",
          "Geometric_fuse",
          "Geometric_complement",
          "Geometric_transform",
          "Geometric_group",
          "Geometric_common",
          "Geometric_slice",
          "Geometric_viewgroup",
        ]

