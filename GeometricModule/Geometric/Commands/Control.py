import FreeCAD, FreeCADGui
from Geometric.Basic import *


class ToggleTransparencyCommand(object):
    def GetResources(self):
        return {"MenuText": "Toggle Transparency",
                "Accel"   : "Shift+Space"}

    def Activated(self):
        for sel in FreeCADGui.Selection.getSelection():
            if sel.ViewObject.Transparency == 0:
                sel.ViewObject.Transparency = 50
            else:
                sel.ViewObject.Transparency = 0

    def IsActive(self):
        return len(FreeCADGui.Selection.getSelection()) > 0

FreeCADGui.addCommand("Geometric_ToggleTransparency", ToggleTransparencyCommand())

ctrllist = ["Std_ToggleVisibility",
            "Geometric_ToggleTransparency"]
