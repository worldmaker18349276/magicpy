import FreeCAD, FreeCADGui
import GeometricResources
from Geometric.Features import *


class CreateSphereCommand(object):
    def GetResources(self):
        return {"Pixmap"  : ":/icons/primitive/Geometric_sphere.svg",
                "MenuText": "sphere",
                "ToolTip" : "create a sphere"}

    def Activated(self):
        FreeCADGui.doCommand("_ftr = FreeCAD.ActiveDocument.addObject('Part::FeaturePython', 'Sphere')")
        FreeCADGui.doCommand("Geometric.Sphere(_ftr)")
        viewGroup = FreeCADGui.activeView().getActiveObject("viewGroup")
        if viewGroup is not None:
            FreeCADGui.doCommand("FreeCAD.ActiveDocument.%s.addObject(_ftr)"%viewGroup.Name)
        FreeCADGui.doCommand("FreeCAD.ActiveDocument.recompute()")
        FreeCADGui.doCommand("FreeCADGui.SendMsgToActiveView('ViewFit')")

    def IsActive(self):
        return FreeCAD.ActiveDocument is not None

class CreateConeCommand(object):
    def GetResources(self):
        return {"Pixmap"  : ":/icons/primitive/Geometric_cone.svg",
                "MenuText": "cone",
                "ToolTip" : "create a cone"}

    def Activated(self):
        FreeCADGui.doCommand("_ftr = FreeCAD.ActiveDocument.addObject('Part::FeaturePython', 'Cone')")
        FreeCADGui.doCommand("Geometric.Cone(_ftr)")
        viewGroup = FreeCADGui.activeView().getActiveObject("viewGroup")
        if viewGroup is not None:
            FreeCADGui.doCommand("FreeCAD.ActiveDocument.%s.addObject(_ftr)"%viewGroup.Name)
        FreeCADGui.doCommand("FreeCAD.ActiveDocument.recompute()")
        FreeCADGui.doCommand("FreeCADGui.SendMsgToActiveView('ViewFit')")

    def IsActive(self):
        return FreeCAD.ActiveDocument is not None

class CreateCylinderCommand(object):
    def GetResources(self):
        return {"Pixmap"  : ":/icons/primitive/Geometric_cylinder.svg",
                "MenuText": "cylinder",
                "ToolTip" : "create a cylinder"}

    def Activated(self):
        FreeCADGui.doCommand("_ftr = FreeCAD.ActiveDocument.addObject('Part::FeaturePython', 'Cylinder')")
        FreeCADGui.doCommand("Geometric.Cylinder(_ftr)")
        viewGroup = FreeCADGui.activeView().getActiveObject("viewGroup")
        if viewGroup is not None:
            FreeCADGui.doCommand("FreeCAD.ActiveDocument.%s.addObject(_ftr)"%viewGroup.Name)
        FreeCADGui.doCommand("FreeCAD.ActiveDocument.recompute()")
        FreeCADGui.doCommand("FreeCADGui.SendMsgToActiveView('ViewFit')")

    def IsActive(self):
        return FreeCAD.ActiveDocument is not None

class EmptySpaceCommand(object):
    def GetResources(self):
        return {"Pixmap"  : ":/icons/primitive/Geometric_empty_space.svg",
                "MenuText": "empty space",
                "ToolTip" : "create a empty space"}

    def Activated(self):
        FreeCADGui.doCommand("_ftr = FreeCAD.ActiveDocument.addObject('Part::FeaturePython', 'EmptySpace')")
        FreeCADGui.doCommand("Geometric.EmptySpace(_ftr)")
        viewGroup = FreeCADGui.activeView().getActiveObject("viewGroup")
        if viewGroup is not None:
            FreeCADGui.doCommand("FreeCAD.ActiveDocument.%s.addObject(_ftr)"%viewGroup.Name)
        FreeCADGui.doCommand("FreeCAD.ActiveDocument.recompute()")
        FreeCADGui.doCommand("FreeCADGui.SendMsgToActiveView('ViewFit')")

    def IsActive(self):
        return FreeCAD.ActiveDocument is not None

class WholeSpaceCommand(object):
    def GetResources(self):
        return {"Pixmap"  : ":/icons/primitive/Geometric_whole_space.svg",
                "MenuText": "whole space",
                "ToolTip" : "create a whole space"}

    def Activated(self):
        FreeCADGui.doCommand("_ftr = FreeCAD.ActiveDocument.addObject('Part::FeaturePython', 'WholeSpace')")
        FreeCADGui.doCommand("Geometric.WholeSpace(_ftr)")
        viewGroup = FreeCADGui.activeView().getActiveObject("viewGroup")
        if viewGroup is not None:
            FreeCADGui.doCommand("FreeCAD.ActiveDocument.%s.addObject(_ftr)"%viewGroup.Name)
        FreeCADGui.doCommand("_ftr.ViewObject.Transparency = 50")
        FreeCADGui.doCommand("FreeCAD.ActiveDocument.recompute()")
        FreeCADGui.doCommand("FreeCADGui.SendMsgToActiveView('ViewFit')")

    def IsActive(self):
        return FreeCAD.ActiveDocument is not None

class CreateHalfspaceCommand(object):
    def GetResources(self):
        return {"Pixmap"  : ":/icons/primitive/Geometric_halfspace.svg",
                "MenuText": "halfspace",
                "ToolTip" : "create a halfspace"}

    def Activated(self):
        FreeCADGui.doCommand("_ftr = FreeCAD.ActiveDocument.addObject('Part::FeaturePython', 'Halfspace')")
        FreeCADGui.doCommand("Geometric.Halfspace(_ftr)")
        viewGroup = FreeCADGui.activeView().getActiveObject("viewGroup")
        if viewGroup is not None:
            FreeCADGui.doCommand("FreeCAD.ActiveDocument.%s.addObject(_ftr)"%viewGroup.Name)
        FreeCADGui.doCommand("_ftr.ViewObject.Transparency = 50")
        FreeCADGui.doCommand("FreeCAD.ActiveDocument.recompute()")
        FreeCADGui.doCommand("FreeCADGui.SendMsgToActiveView('ViewFit')")

    def IsActive(self):
        return FreeCAD.ActiveDocument is not None

class CreateInfiniteCylinderCommand(object):
    def GetResources(self):
        return {"Pixmap"  : ":/icons/primitive/Geometric_infinite_cylinder.svg",
                "MenuText": "infinite cylinder",
                "ToolTip" : "create an infinite cylinder"}

    def Activated(self):
        FreeCADGui.doCommand("_ftr = FreeCAD.ActiveDocument.addObject('Part::FeaturePython', 'InfiniteCylinder')")
        FreeCADGui.doCommand("Geometric.InfiniteCylinder(_ftr)")
        viewGroup = FreeCADGui.activeView().getActiveObject("viewGroup")
        if viewGroup is not None:
            FreeCADGui.doCommand("FreeCAD.ActiveDocument.%s.addObject(_ftr)"%viewGroup.Name)
        FreeCADGui.doCommand("_ftr.ViewObject.Transparency = 50")
        FreeCADGui.doCommand("FreeCAD.ActiveDocument.recompute()")
        FreeCADGui.doCommand("FreeCADGui.SendMsgToActiveView('ViewFit')")

    def IsActive(self):
        return FreeCAD.ActiveDocument is not None

class CreateSemiInfiniteConeCommand(object):
    def GetResources(self):
        return {"Pixmap"  : ":/icons/primitive/Geometric_semi_infinite_cone.svg",
                "MenuText": "semi-infinite cone",
                "ToolTip" : "create a semi-infinite cone"}

    def Activated(self):
        FreeCADGui.doCommand("_ftr = FreeCAD.ActiveDocument.addObject('Part::FeaturePython', 'SemiInfiniteCone')")
        FreeCADGui.doCommand("Geometric.SemiInfiniteCone(_ftr)")
        viewGroup = FreeCADGui.activeView().getActiveObject("viewGroup")
        if viewGroup is not None:
            FreeCADGui.doCommand("FreeCAD.ActiveDocument.%s.addObject(_ftr)"%viewGroup.Name)
        FreeCADGui.doCommand("_ftr.ViewObject.Transparency = 50")
        FreeCADGui.doCommand("FreeCAD.ActiveDocument.recompute()")
        FreeCADGui.doCommand("FreeCADGui.SendMsgToActiveView('ViewFit')")

    def IsActive(self):
        return FreeCAD.ActiveDocument is not None


FreeCADGui.addCommand("Geometric_empty_space", EmptySpaceCommand())
FreeCADGui.addCommand("Geometric_whole_space", WholeSpaceCommand())
FreeCADGui.addCommand("Geometric_halfspace", CreateHalfspaceCommand())
FreeCADGui.addCommand("Geometric_infinite_cylinder", CreateInfiniteCylinderCommand())
FreeCADGui.addCommand("Geometric_semi_infinite_cone", CreateSemiInfiniteConeCommand())
FreeCADGui.addCommand("Geometric_sphere", CreateSphereCommand())
FreeCADGui.addCommand("Geometric_cone", CreateConeCommand())
FreeCADGui.addCommand("Geometric_cylinder", CreateCylinderCommand())

objlist = [
    "Geometric_sphere",
    "Geometric_cone",
    "Geometric_cylinder",
    "Geometric_empty_space",
    "Geometric_whole_space",
    "Geometric_halfspace",
    "Geometric_infinite_cylinder",
    "Geometric_semi_infinite_cone",
]

