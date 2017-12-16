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
        view_space = FreeCADGui.activeView().getActiveObject("ViewSpace")
        if view_space is not None:
            FreeCADGui.doCommand("FreeCAD.ActiveDocument.%s.addObject(_ftr)"%view_space.Name)
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
        view_space = FreeCADGui.activeView().getActiveObject("ViewSpace")
        if view_space is not None:
            FreeCADGui.doCommand("FreeCAD.ActiveDocument.%s.addObject(_ftr)"%view_space.Name)
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
        view_space = FreeCADGui.activeView().getActiveObject("ViewSpace")
        if view_space is not None:
            FreeCADGui.doCommand("FreeCAD.ActiveDocument.%s.addObject(_ftr)"%view_space.Name)
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
        plc = FreeCADGui.Selection.getSelection()[1]
        FreeCADGui.doCommand("_ftr = Geometric.transform(%s, %s)"%(ftrstr(sel), ftrstr(plc)))
        view_space = FreeCADGui.activeView().getActiveObject("ViewSpace")
        if view_space is not None:
            FreeCADGui.doCommand("FreeCAD.ActiveDocument.%s.addObject(_ftr)"%view_space.Name)
        FreeCADGui.doCommand("FreeCAD.ActiveDocument.recompute()")
        FreeCADGui.doCommand("FreeCADGui.SendMsgToActiveView('ViewFit')")

    def IsActive(self):
        return len(FreeCADGui.Selection.getSelection()) == 2


class CompoundCommand(object):
    def GetResources(self):
        return {"Pixmap"  : "Geometric_group.png",
                "MenuText": "compound",
                "ToolTip" : "make a compound of several shapes"}

    def Activated(self):
        sel = FreeCADGui.Selection.getSelection()
        FreeCADGui.doCommand("_ftr = Geometric.compound(%s)"%ftrstr(*sel))
        view_space = FreeCADGui.activeView().getActiveObject("ViewSpace")
        if view_space is not None:
            FreeCADGui.doCommand("FreeCAD.ActiveDocument.%s.addObject(_ftr)"%view_space.Name)

    def IsActive(self):
        return len(FreeCADGui.Selection.getSelection()) >= 0

class CompoundCommonCommand(object):
    def GetResources(self):
        return {"Pixmap"  : "Geometric_group_common.png",
                "MenuText": "compound common",
                "ToolTip" : "make a common of several shapes"}

    def Activated(self):
        target = FreeCADGui.Selection.getSelection()[0]
        sel = distinct_list(FreeCADGui.Selection.getSelection()[1:])
        FreeCADGui.doCommand("Geometric.compound_common(%s, %s)"%(ftrstr(target), ftrstr(*sel)))
        FreeCADGui.doCommand("FreeCAD.ActiveDocument.recompute()")
        FreeCADGui.doCommand("FreeCADGui.SendMsgToActiveView('ViewFit')")

    def IsActive(self):
        return len(FreeCADGui.Selection.getSelection()) > 0

class CompoundSliceCommand(object):
    def GetResources(self):
        return {"Pixmap"  : "Geometric_group_slice.png",
                "MenuText": "compound slice",
                "ToolTip" : "make a slice of several shapes"}

    def Activated(self):
        target = FreeCADGui.Selection.getSelection()[0]
        sel = distinct_list(FreeCADGui.Selection.getSelection()[1:])
        FreeCADGui.doCommand("Geometric.compound_slice(%s, %s)"%(ftrstr(target), ftrstr(*sel)))
        FreeCADGui.doCommand("FreeCAD.ActiveDocument.recompute()")
        FreeCADGui.doCommand("FreeCADGui.SendMsgToActiveView('ViewFit')")

    def IsActive(self):
        return len(FreeCADGui.Selection.getSelection()) > 0


class ViewSpaceCommand(object):
    def GetResources(self):
        return {"Pixmap"  : ":/icons/Geometric_viewbox.svg",
                "MenuText": "add view space",
                "ToolTip" : "add view space"}

    def Activated(self):
        FreeCADGui.doCommand("_ftr = FreeCAD.ActiveDocument.addObject('App::DocumentObjectGroupPython', 'ViewSpace')")
        FreeCADGui.doCommand("Geometric.ViewSpace(_ftr)")
        FreeCADGui.doCommand("FreeCADGui.activeView().setActiveObject('ViewSpace', _ftr)")

    def IsActive(self):
        return FreeCAD.ActiveDocument is not None


FreeCADGui.addCommand("Geometric_common", CommonCommand())
FreeCADGui.addCommand("Geometric_fuse", FuseCommand())
FreeCADGui.addCommand("Geometric_complement", ComplementCommand())
FreeCADGui.addCommand("Geometric_transform", TransformCommand())
FreeCADGui.addCommand("Geometric_compound", CompoundCommand())
FreeCADGui.addCommand("Geometric_compound_common", CompoundCommonCommand())
FreeCADGui.addCommand("Geometric_compound_slice", CompoundSliceCommand())
FreeCADGui.addCommand("Geometric_viewbox", ViewSpaceCommand())

oplist = ["Geometric_common",
          "Geometric_fuse",
          "Geometric_complement",
          "Geometric_transform",
          "Geometric_compound",
          "Geometric_compound_common",
          "Geometric_compound_slice",
          "Geometric_viewbox",
        ]

