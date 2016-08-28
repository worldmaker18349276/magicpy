import FreeCAD, FreeCADGui
import MagicPartResources
from MagicPart.Basic import P
from MagicPart.Control import *


class ToggleTransparencyCommand(object):
    def GetResources(self):
        return {"MenuText": "Toggle Transparency",
                "Accel"   : "Shift+Space"}

    def Activated(self):
        if P.incmdline:
            for sel in ftrlist(FreeCADGui.Selection.getSelection()):
                if sel.ViewObject.Transparency == 0:
                    FreeCADGui.doCommand("%s.ViewObject.Transparency = 50"%ftrstr(sel))
                else:
                    FreeCADGui.doCommand("%s.ViewObject.Transparency = 0"%ftrstr(sel))

        else:
            for sel in ftrlist(FreeCADGui.Selection.getSelection()):
                if sel.ViewObject.Transparency == 0:
                    sel.ViewObject.Transparency = 50
                else:
                    sel.ViewObject.Transparency = 0

    def IsActive(self):
        return len(FreeCADGui.Selection.getSelection()) > 0

class ToggleTouchedCommand(object):
    def GetResources(self):
        return {"MenuText": "Toggle Touched",
                "Accel"   : "F6"}

    def Activated(self):
        if P.incmdline:
            for sel in ftrlist(FreeCADGui.Selection.getSelection()):
                if "Touched" in sel.State:
                    FreeCADGui.doCommand("%s.purgeTouched()"%ftrstr(sel))
                else:
                    FreeCADGui.doCommand("MagicPart.forceTouch(%s)"%ftrstr(sel))

        else:
            for sel in ftrlist(FreeCADGui.Selection.getSelection()):
                if "Touched" in sel.State:
                    sel.purgeTouched()
                else:
                    forceTouch(sel)

    def IsActive(self):
        return len(FreeCADGui.Selection.getSelection()) > 0


class RefreshSelectedCommand(object):
    def GetResources(self):
        return {"MenuText": "Refresh selected",
                "Accel"   : "Ctrl+R"}

    def Activated(self):
        if P.incmdline:
            sel = ftrlist(FreeCADGui.Selection.getSelection())
            if len(sel) == 0:
                FreeCADGui.doCommand("FreeCAD.ActiveDocument.recompute()")
            else:
                FreeCADGui.doCommand("MagicPart.recompute(%s)"%ftrstr(sel))

        else:
            if len(FreeCADGui.Selection.getSelection()) == 0:
                FreeCAD.ActiveDocument.recompute()
            else:
                recompute(ftrlist(FreeCADGui.Selection.getSelection()))

    def IsActive(self):
        return FreeCAD.ActiveDocument is not None

class ForceRefreshSelectedCommand(object):
    def GetResources(self):
        return {"MenuText": "Force Refresh selected",
                "Accel"   : "Ctrl+Shift+R"}

    def Activated(self):
        if P.incmdline:
            sel = ftrlist(FreeCADGui.Selection.getSelection())
            if len(sel) == 0:
                FreeCADGui.doCommand("MagicPart.recompute(FreeCAD.ActiveDocument.Objects, forced=True)")
            else:
                FreeCADGui.doCommand("MagicPart.recompute(%s, forced=True)"%ftrstr(sel))

        else:
            if len(FreeCADGui.Selection.getSelection()) == 0:
                recompute(FreeCAD.ActiveDocument.Objects, forced=True)
            else:
                recompute(ftrlist(FreeCADGui.Selection.getSelection()), forced=True)

    def IsActive(self):
        return FreeCAD.ActiveDocument is not None


class ShiftToChildrenCommand(object):
    def GetResources(self):
        return {"MenuText": "Shift to Children",
                "Accel"   : "Shift+C"}

    def Activated(self):
        shiftToChildren()
        FreeCADGui.runCommand("Std_TreeSelection")

    def IsActive(self):
        return len(FreeCADGui.Selection.getSelection()) > 0

class ViewCommand(object):
    def GetResources(self):
        return {"MenuText": "View Selected Objects",
                "Accel"   : "Ctrl+G"}

    def Activated(self):
        if P.incmdline:
            if len(FreeCADGui.Selection.getSelection()) == 0:
                FreeCADGui.doCommand("MagicPart.viewAllBounded()")
            else:
                FreeCADGui.doCommand("MagicPart.viewBoundedSelections()")
                FreeCADGui.doCommand("FreeCADGui.runCommand('Std_TreeSelection')")

        else:
            if len(FreeCADGui.Selection.getSelection()) == 0:
                viewAllBounded()
            else:
                viewBoundedSelections()
                FreeCADGui.runCommand("Std_TreeSelection")

    def IsActive(self):
        return FreeCAD.ActiveDocument is not None

class FocusCommand(object):
    def GetResources(self):
        return {"MenuText": "Focus on Selected Objects",
                "Accel"   : "Ctrl+F"}

    def Activated(self):
        if P.incmdline:
            sel = FreeCADGui.Selection.getSelection()
            for obj in FreeCAD.ActiveDocument.Objects:
                if obj not in sel:
                    FreeCADGui.doCommand("%s.ViewObject.hide()"%ftrstr(obj))
            FreeCADGui.doCommand("MagicPart.viewBoundedSelections()")
            FreeCADGui.doCommand("FreeCADGui.runCommand('Std_TreeSelection')")

        else:
            sel = FreeCADGui.Selection.getSelection()
            for obj in FreeCAD.ActiveDocument.Objects:
                if obj not in sel:
                    obj.ViewObject.hide()
            viewBoundedSelections()
            FreeCADGui.runCommand("Std_TreeSelection")

    def IsActive(self):
        return len(FreeCADGui.Selection.getSelection()) > 0


FreeCADGui.addCommand("MagicPart_ToggleTransparency", ToggleTransparencyCommand())
FreeCADGui.addCommand("MagicPart_ToggleTouched", ToggleTouchedCommand())
FreeCADGui.addCommand("MagicPart_RefreshSelected", RefreshSelectedCommand())
FreeCADGui.addCommand("MagicPart_ForceRefreshSelected", ForceRefreshSelectedCommand())
FreeCADGui.addCommand("MagicPart_ShiftToChildren", ShiftToChildrenCommand())
FreeCADGui.addCommand("MagicPart_View", ViewCommand())
FreeCADGui.addCommand("MagicPart_Focus", FocusCommand())

ctrllist = ["Std_ToggleVisibility",
            "MagicPart_ToggleTransparency",
            "MagicPart_ToggleTouched",
            "MagicPart_RefreshSelected",
            "MagicPart_ForceRefreshSelected",
            "MagicPart_ShiftToChildren",
            "MagicPart_View",
            "MagicPart_Focus"]

