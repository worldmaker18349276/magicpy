import FreeCAD, FreeCADGui
import MagicPartResources
from MagicPart.Basic import P
from MagicPart.Features import *


class CreateNumberCommand(object):
    def GetResources(self):
        return {"MenuText": "number",
                "ToolTip" : "create a number"}

    def Activated(self):
        if P.incmdline:
            FreeCADGui.doCommand("_var = MagicPart.addObject(MagicPart.Number, 'Number', rep=%r, cached=False)"%P.rep)
            FreeCADGui.doCommand("MagicPart.recompute([_var])")
            if P.autosel:
                FreeCADGui.doCommand("MagicPart.select([_var])")

        else:
            var = addObject(Number, "Number", rep=P.rep, cached=False)
            recompute([var])
            if P.autosel:
                select([var])
            viewAllBounded()

    def IsActive(self):
        return FreeCAD.ActiveDocument is not None

class CreateVectorCommand(object):
    def GetResources(self):
        return {"MenuText": "vector",
                "ToolTip" : "create a vector"}

    def Activated(self):
        if P.incmdline:
            FreeCADGui.doCommand("_var = MagicPart.addObject(MagicPart.Vector, 'Vector', rep=%r, cached=False)"%P.rep)
            FreeCADGui.doCommand("MagicPart.recompute([_var])")
            if P.autosel:
                FreeCADGui.doCommand("MagicPart.select([_var])")

        else:
            var = addObject(Vector, "Vector", rep=P.rep, cached=False)
            recompute([var])
            if P.autosel:
                select([var])
            viewAllBounded()

    def IsActive(self):
        return FreeCAD.ActiveDocument is not None

class CreatePlacementCommand(object):
    def GetResources(self):
        return {"MenuText": "placement",
                "ToolTip" : "create a placement"}

    def Activated(self):
        if P.incmdline:
            FreeCADGui.doCommand("_var = MagicPart.addObject(MagicPart.Placement, 'Placement', rep=%r, cached=False)"%P.rep)
            FreeCADGui.doCommand("MagicPart.recompute([_var])")
            if P.autosel:
                FreeCADGui.doCommand("MagicPart.select([_var])")

        else:
            var = addObject(Placement, "Placement", rep=P.rep, cached=False)
            recompute([var])
            if P.autosel:
                select([var])
            viewAllBounded()

    def IsActive(self):
        return FreeCAD.ActiveDocument is not None


FreeCADGui.addCommand("MagicPart_number", CreateNumberCommand())
FreeCADGui.addCommand("MagicPart_vector", CreateVectorCommand())
FreeCADGui.addCommand("MagicPart_placement", CreatePlacementCommand())

varlist = ["MagicPart_number",
           "MagicPart_vector",
           "MagicPart_placement"]

