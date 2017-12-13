import FreeCAD, FreeCADGui
import GeometricResources
from Geometric.Features import *

def do_createObject(name, unbounded=False):
    viewboxGroup = FreeCADGui.activeView().getActiveObject("viewboxGroup")
    if viewboxGroup is not None:
        prefix = "_ftr = FreeCAD.ActiveDocument.%s.newObject"%viewboxGroup.Name
    else:
        prefix = "_ftr = FreeCAD.ActiveDocument.addObject"

    FreeCADGui.doCommand(prefix+str(("Part::FeaturePython", name)))
    FreeCADGui.doCommand("Geometric.%s(_ftr)"%name)
    if unbounded:
        FreeCADGui.doCommand("_ftr.ViewObject.Transparency = 50")
    FreeCADGui.doCommand("FreeCAD.ActiveDocument.recompute()")
    FreeCADGui.doCommand("FreeCADGui.SendMsgToActiveView('ViewFit')")

class CreateSphereCommand(object):
    def GetResources(self):
        return {"Pixmap"  : ":/icons/primitive/Geometric_sphere.svg",
                "MenuText": "sphere",
                "ToolTip" : "create a sphere"}

    def Activated(self):
        do_createObject("Sphere")

    def IsActive(self):
        return FreeCAD.ActiveDocument is not None

class CreateConeCommand(object):
    def GetResources(self):
        return {"Pixmap"  : ":/icons/primitive/Geometric_cone.svg",
                "MenuText": "cone",
                "ToolTip" : "create a cone"}

    def Activated(self):
        do_createObject("Cone")

    def IsActive(self):
        return FreeCAD.ActiveDocument is not None

class CreateCylinderCommand(object):
    def GetResources(self):
        return {"Pixmap"  : ":/icons/primitive/Geometric_cylinder.svg",
                "MenuText": "cylinder",
                "ToolTip" : "create a cylinder"}

    def Activated(self):
        do_createObject("Cylinder")

    def IsActive(self):
        return FreeCAD.ActiveDocument is not None

class EmptySpaceCommand(object):
    def GetResources(self):
        return {"Pixmap"  : ":/icons/primitive/Geometric_empty_space.svg",
                "MenuText": "empty space",
                "ToolTip" : "create a empty space"}

    def Activated(self):
        do_createObject("EmptySpace")

    def IsActive(self):
        return FreeCAD.ActiveDocument is not None

class WholeSpaceCommand(object):
    def GetResources(self):
        return {"Pixmap"  : ":/icons/primitive/Geometric_whole_space.svg",
                "MenuText": "whole space",
                "ToolTip" : "create a whole space"}

    def Activated(self):
        do_createObject("WholeSpace", True)

    def IsActive(self):
        return FreeCAD.ActiveDocument is not None

class CreateHalfspaceCommand(object):
    def GetResources(self):
        return {"Pixmap"  : ":/icons/primitive/Geometric_halfspace.svg",
                "MenuText": "halfspace",
                "ToolTip" : "create a halfspace"}

    def Activated(self):
        do_createObject("Halfspace", True)

    def IsActive(self):
        return FreeCAD.ActiveDocument is not None

class CreateInfiniteCylinderCommand(object):
    def GetResources(self):
        return {"Pixmap"  : ":/icons/primitive/Geometric_infinite_cylinder.svg",
                "MenuText": "infinite cylinder",
                "ToolTip" : "create an infinite cylinder"}

    def Activated(self):
        do_createObject("InfiniteCylinder", True)

    def IsActive(self):
        return FreeCAD.ActiveDocument is not None

class CreateSemiInfiniteConeCommand(object):
    def GetResources(self):
        return {"Pixmap"  : ":/icons/primitive/Geometric_semi_infinite_cone.svg",
                "MenuText": "semi-infinite cone",
                "ToolTip" : "create a semi-infinite cone"}

    def Activated(self):
        do_createObject("SemiInfiniteCone", True)

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

