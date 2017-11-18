import FreeCAD, FreeCADGui, Draft
import MagicPartResources
from MagicPart.Basic import P
from MagicPart.Features import *


class AdjustViewBoxCommand(object):
    def GetResources(self):
        return {"Pixmap"  : ":/icons/MagicPart_adjust_viewbox.svg",
                "MenuText": "adjust viewbox",
                "ToolTip" : "set/adjust viewbox by selected object"}

    def Activated(self):
        if P.incmdline:
            if len(FreeCADGui.Selection.getSelection()) == 0:
                FreeCADGui.doCommand("MagicPart.fitBounded(MagicPart.getViewBox())")
            else:
                FreeCADGui.doCommand("MagicPart.fitBounded(MagicPart.getViewBox(), FreeCADGui.Selection.getSelection())")
            FreeCADGui.doCommand("MagicPart.recompute([MagicPart.getViewBox()])")

        else:
            vb = getViewBox()
            if len(FreeCADGui.Selection.getSelection()) == 0:
                fitBounded(vb)
            else:
                fitBounded(vb, FreeCADGui.Selection.getSelection())
            recompute([vb])

    def IsActive(self):
        return FreeCAD.ActiveDocument is not None

class CreateBoxCommand(object):
    def GetResources(self):
        return {"Pixmap"  : ":/icons/primitive/MagicPart_cube.svg",
                "MenuText": "box",
                "ToolTip" : "create a box"}

    def Activated(self):
        if P.incmdline:
            FreeCADGui.doCommand("_ftr = MagicPart.addObject(MagicPart.Box, 'Box', rep=%r, cached=False)"%P.rep)
            FreeCADGui.doCommand("MagicPart.recompute([_ftr])")
            if P.autosel:
                FreeCADGui.doCommand("MagicPart.select([_ftr])")
            FreeCADGui.doCommand("MagicPart.viewAllBounded()")

        else:
            ftr = addObject(Box, "Box", rep=P.rep, cached=False)
            recompute([ftr])
            if P.autosel:
                select([ftr])
            viewAllBounded()

    def IsActive(self):
        return FreeCAD.ActiveDocument is not None

class CreateCylinderCommand(object):
    def GetResources(self):
        return {"Pixmap"  : ":/icons/primitive/MagicPart_cylinder.svg",
                "MenuText": "cylinder",
                "ToolTip" : "create a cylinder"}

    def Activated(self):
        if P.incmdline:
            FreeCADGui.doCommand("_ftr = MagicPart.addObject(MagicPart.Cylinder, 'Cylinder', rep=%r, cached=False)"%P.rep)
            FreeCADGui.doCommand("MagicPart.recompute([_ftr])")
            if P.autosel:
                FreeCADGui.doCommand("MagicPart.select([_ftr])")
            FreeCADGui.doCommand("MagicPart.viewAllBounded()")

        else:
            ftr = addObject(Cylinder, "Cylinder", rep=P.rep, cached=False)
            recompute([ftr])
            if P.autosel:
                select([ftr])
            viewAllBounded()

    def IsActive(self):
        return FreeCAD.ActiveDocument is not None

class CreateConeCommand(object):
    def GetResources(self):
        return {"Pixmap"  : ":/icons/primitive/MagicPart_cone.svg",
                "MenuText": "cone",
                "ToolTip" : "create a cone"}

    def Activated(self):
        if P.incmdline:
            FreeCADGui.doCommand("_ftr = MagicPart.addObject(MagicPart.Cone, 'Cone', rep=%r, cached=False)"%P.rep)
            FreeCADGui.doCommand("MagicPart.recompute([_ftr])")
            if P.autosel:
                FreeCADGui.doCommand("MagicPart.select([_ftr])")
            FreeCADGui.doCommand("MagicPart.viewAllBounded()")

        else:
            ftr = addObject(Cone, "Cone", rep=P.rep, cached=False)
            recompute([ftr])
            if P.autosel:
                select([ftr])
            viewAllBounded()

    def IsActive(self):
        return FreeCAD.ActiveDocument is not None

class CreateSphereCommand(object):
    def GetResources(self):
        return {"Pixmap"  : ":/icons/primitive/MagicPart_sphere.svg",
                "MenuText": "sphere",
                "ToolTip" : "create a sphere"}

    def Activated(self):
        if P.incmdline:
            FreeCADGui.doCommand("_ftr = MagicPart.addObject(MagicPart.Sphere, 'Sphere', rep=%r, cached=False)"%P.rep)
            FreeCADGui.doCommand("MagicPart.recompute([_ftr])")
            if P.autosel:
                FreeCADGui.doCommand("MagicPart.select([_ftr])")
            FreeCADGui.doCommand("MagicPart.viewAllBounded()")

        else:
            ftr = addObject(Sphere, "Sphere", rep=P.rep, cached=False)
            recompute([ftr])
            if P.autosel:
                select([ftr])
            viewAllBounded()

    def IsActive(self):
        return FreeCAD.ActiveDocument is not None

class CreateHalfspaceCommand(object):
    def GetResources(self):
        return {"Pixmap"  : ":/icons/primitive/MagicPart_halfspace.svg",
                "MenuText": "halfspace",
                "ToolTip" : "create a halfspace"}

    def Activated(self):
        if P.incmdline:
            FreeCADGui.doCommand("_ftr = MagicPart.addObject(MagicPart.Halfspace, 'Halfspace', rep=%r, cached=False)"%P.rep)
            FreeCADGui.doCommand("_ftr.ViewObject.Transparency = 50")
            FreeCADGui.doCommand("MagicPart.recompute([_ftr])")
            if P.autosel:
                FreeCADGui.doCommand("MagicPart.select([_ftr])")

        else:
            ftr = addObject(Halfspace, "Halfspace", rep=P.rep, cached=False)
            ftr.ViewObject.Transparency = 50
            recompute([ftr])
            if P.autosel:
                select([ftr])

    def IsActive(self):
        return FreeCAD.ActiveDocument is not None

class CreateInfiniteCylinderCommand(object):
    def GetResources(self):
        return {"Pixmap"  : ":/icons/primitive/MagicPart_infinite_cylinder.svg",
                "MenuText": "infinite cylinder",
                "ToolTip" : "create an infinite cylinder"}

    def Activated(self):
        if P.incmdline:
            FreeCADGui.doCommand("_ftr = MagicPart.addObject(MagicPart.InfiniteCylinder, 'InfiniteCylinder', rep=%r, cached=False)"%P.rep)
            FreeCADGui.doCommand("_ftr.ViewObject.Transparency = 50")
            FreeCADGui.doCommand("MagicPart.recompute([_ftr])")
            if P.autosel:
                FreeCADGui.doCommand("MagicPart.select([_ftr])")

        else:
            ftr = addObject(InfiniteCylinder, "InfiniteCylinder", rep=P.rep, cached=False)
            ftr.ViewObject.Transparency = 50
            recompute([ftr])
            if P.autosel:
                select([ftr])

    def IsActive(self):
        return FreeCAD.ActiveDocument is not None

class CreateSemiInfiniteConeCommand(object):
    def GetResources(self):
        return {"Pixmap"  : ":/icons/primitive/MagicPart_semi_infinite_cone.svg",
                "MenuText": "semi-infinite cone",
                "ToolTip" : "create a semi-infinite cone"}

    def Activated(self):
        if P.incmdline:
            FreeCADGui.doCommand("_ftr = MagicPart.addObject(MagicPart.SemiInfiniteCone, 'SemiInfiniteCone', rep=%r, cached=False)"%P.rep)
            FreeCADGui.doCommand("_ftr.ViewObject.Transparency = 50")
            FreeCADGui.doCommand("MagicPart.recompute([_ftr])")
            if P.autosel:
                FreeCADGui.doCommand("MagicPart.select([_ftr])")

        else:
            ftr = addObject(SemiInfiniteCone, "SemiInfiniteCone", rep=P.rep, cached=False)
            ftr.ViewObject.Transparency = 50
            recompute([ftr])
            if P.autosel:
                select([ftr])

    def IsActive(self):
        return FreeCAD.ActiveDocument is not None

class WholeSpaceCommand(object):
    def GetResources(self):
        return {"Pixmap"  : ":/icons/primitive/MagicPart_whole_space.svg",
                "MenuText": "whole space",
                "ToolTip" : "create a whole space"}

    def Activated(self):
        if P.incmdline:
            FreeCADGui.doCommand("_ftr = MagicPart.addObject(MagicPart.WholeSpace, 'WholeSpace', rep=%r, cached=False)"%P.rep)
            FreeCADGui.doCommand("_ftr.ViewObject.Transparency = 50")
            FreeCADGui.doCommand("MagicPart.recompute([_ftr])")
            if P.autosel:
                FreeCADGui.doCommand("MagicPart.select([_ftr])")

        else:
            ftr = addObject(WholeSpace, "WholeSpace", rep=P.rep, cached=False)
            ftr.ViewObject.Transparency = 50
            recompute([ftr])
            if P.autosel:
                select([ftr])

    def IsActive(self):
        return FreeCAD.ActiveDocument is not None

class EmptySpaceCommand(object):
    def GetResources(self):
        return {"Pixmap"  : ":/icons/primitive/MagicPart_empty_space.svg",
                "MenuText": "empty space",
                "ToolTip" : "create a empty space"}

    def Activated(self):
        if P.incmdline:
            FreeCADGui.doCommand("_ftr = MagicPart.addObject(MagicPart.EmptySpace, 'EmptySpace', rep=%r, cached=False)"%P.rep)
            FreeCADGui.doCommand("_ftr.ViewObject.Transparency = 50")
            FreeCADGui.doCommand("MagicPart.recompute([_ftr])")
            if P.autosel:
                FreeCADGui.doCommand("MagicPart.select([_ftr])")

        else:
            ftr = addObject(EmptySpace, "EmptySpace", rep=P.rep, cached=False)
            ftr.ViewObject.Transparency = 50
            recompute([ftr])
            if P.autosel:
                select([ftr])

    def IsActive(self):
        return FreeCAD.ActiveDocument is not None


FreeCADGui.addCommand("MagicPart_adjust_viewbox", AdjustViewBoxCommand())
FreeCADGui.addCommand("MagicPart_box", CreateBoxCommand())
FreeCADGui.addCommand("MagicPart_cylinder", CreateCylinderCommand())
FreeCADGui.addCommand("MagicPart_cone", CreateConeCommand())
FreeCADGui.addCommand("MagicPart_sphere", CreateSphereCommand())
FreeCADGui.addCommand("MagicPart_halfspace", CreateHalfspaceCommand())
FreeCADGui.addCommand("MagicPart_infinite_cylinder", CreateInfiniteCylinderCommand())
FreeCADGui.addCommand("MagicPart_semi_infinite_cone", CreateSemiInfiniteConeCommand())
FreeCADGui.addCommand("MagicPart_whole_space", WholeSpaceCommand())
FreeCADGui.addCommand("MagicPart_empty_space", EmptySpaceCommand())

objlist = ["MagicPart_adjust_viewbox",
           "MagicPart_box",
           "MagicPart_cylinder",
           "MagicPart_sphere",
           "MagicPart_cone",
           "MagicPart_halfspace",
           "MagicPart_infinite_cylinder",
           "MagicPart_semi_infinite_cone",
           "MagicPart_whole_space",
           "MagicPart_empty_space"]

