import FreeCAD, FreeCADGui, Draft
import MagicPartResources
from MagicPart.Basic import P
from MagicPart.Features import *


class CommonCommand(object):
    def GetResources(self):
        return {"Pixmap"  : "MagicPart_common.png",
                "MenuText": "common",
                "ToolTip" : "make an intersection of several shapes"}

    def Activated(self):
        sel = distinct_list(FreeCADGui.Selection.getSelection())
        need_recompute = P.autorecomp or all(not isTouched(s) for s in sel)
        if len(sel) > 0:
            parent = sel[0].getParentGroup()

        if P.incmdline:
            if parent is None:
                FreeCADGui.doCommand("_ftr = MagicPart.common(*%s)"%ftrstr(sel))
            else:
                FreeCADGui.doCommand("_ftr = MagicPart.common(*%s, parent=%s)"%(ftrstr(sel), ftrstr(parent)))
            if need_recompute:
                FreeCADGui.doCommand("MagicPart.recompute([_ftr])")
            if P.autosel:
                FreeCADGui.doCommand("MagicPart.select([_ftr])")

        else:
            ftr = common(*sel, parent=parent)
            if need_recompute:
                recompute([ftr])
            if P.autosel:
                select([ftr])

    def IsActive(self):
        return len(FreeCADGui.Selection.getSelection()) > 0

class FuseCommand(object):
    def GetResources(self):
        return {"Pixmap"  : "MagicPart_fuse.png",
                "MenuText": "fuse",
                "ToolTip" : "make an union of several shapes"}

    def Activated(self):
        sel = distinct_list(FreeCADGui.Selection.getSelection())
        need_recompute = P.autorecomp or all(not isTouched(s) for s in sel)
        if len(sel) > 0:
            parent = sel[0].getParentGroup()

        if P.incmdline:
            if parent is None:
                FreeCADGui.doCommand("_ftr = MagicPart.fuse(*%s)"%ftrstr(sel))
            else:
                FreeCADGui.doCommand("_ftr = MagicPart.fuse(*%s, parent=%s)"%(ftrstr(sel), ftrstr(parent)))
            if need_recompute:
                FreeCADGui.doCommand("MagicPart.recompute([_ftr])")
            if P.autosel:
                FreeCADGui.doCommand("MagicPart.select([_ftr])")

        else:
            ftr = fuse(*sel, parent=parent)
            if need_recompute:
                recompute([ftr])
            if P.autosel:
                select([ftr])

    def IsActive(self):
        return len(FreeCADGui.Selection.getSelection()) > 0

class CutCommand(object):
    def GetResources(self):
        return {"Pixmap"  : "MagicPart_cut.png",
                "MenuText": "cut",
                "ToolTip" : "make a difference of two shapes"}

    def Activated(self):
        sel = distinct_list(FreeCADGui.Selection.getSelection())
        if len(sel) != 2:
            raise ValueError
        need_recompute = P.autorecomp or all(not isTouched(s) for s in sel)
        if len(sel) > 0:
            parent = sel[0].getParentGroup()

        if P.incmdline:
            if parent is None:
                FreeCADGui.doCommand("_ftr = MagicPart.cut(%s, %s)"%(ftrstr(sel[0]), ftrstr(sel[1])))
            else:
                FreeCADGui.doCommand("_ftr = MagicPart.cut(%s, %s, parent=%s)"%(ftrstr(sel[0]), ftrstr(sel[1]), ftrstr(parent)))
            if need_recompute:
                FreeCADGui.doCommand("MagicPart.recompute([_ftr])")
            if P.autosel:
                FreeCADGui.doCommand("MagicPart.select([_ftr])")

        else:
            ftr = cut(sel[0], sel[1], parent=parent)
            if need_recompute:
                recompute([ftr])
            if P.autosel:
                select([ftr])

    def IsActive(self):
        return len(FreeCADGui.Selection.getSelection()) == 2

class ComplementCommand(object):
    def GetResources(self):
        return {"Pixmap"  : "MagicPart_complement.png",
                "MenuText": "complement",
                "ToolTip" : "make a complement of shape"}

    def Activated(self):
        sel = FreeCADGui.Selection.getSelection()[0]
        need_recompute = P.autorecomp or not isTouched(sel)
        if len(sel) > 0:
            parent = sel[0].getParentGroup()

        if P.incmdline:
            if parent is None:
                FreeCADGui.doCommand("_ftr = MagicPart.complement(%s)"%ftrstr(sel))
            else:
                FreeCADGui.doCommand("_ftr = MagicPart.complement(%s, parent=%s)"%(ftrstr(sel), ftrstr(parent)))
            if need_recompute:
                FreeCADGui.doCommand("MagicPart.recompute([_ftr])")
            if P.autosel:
                FreeCADGui.doCommand("MagicPart.select([_ftr])")

        else:
            ftr = complement(sel, parent=parent)
            if need_recompute:
                recompute([ftr])
            if P.autosel:
                select([ftr])

    def IsActive(self):
        return len(FreeCADGui.Selection.getSelection()) == 1

class TransformCommand(object):
    def GetResources(self):
        return {"Pixmap"  : "MagicPart_transform.png",
                "MenuText": "transform",
                "ToolTip" : "make a transformation of shape"}

    def Activated(self):
        sel = FreeCADGui.Selection.getSelection()[0]
        need_recompute = P.autorecomp or not isTouched(sel)
        if len(sel) > 0:
            parent = sel[0].getParentGroup()

        if P.incmdline:
            if parent is None:
                FreeCADGui.doCommand("_ftr = MagicPart.transform(%s)"%ftrstr(sel))
            else:
                FreeCADGui.doCommand("_ftr = MagicPart.transform(%s, parent=%s)"%(ftrstr(sel), ftrstr(parent)))
            if need_recompute:
                FreeCADGui.doCommand("MagicPart.recompute([_ftr])")
            if P.autosel:
                FreeCADGui.doCommand("MagicPart.select([_ftr])")

        else:
            ftr = transform(sel, parent=parent)
            if need_recompute:
                recompute([ftr])
            if P.autosel:
                select([ftr])

    def IsActive(self):
        return len(FreeCADGui.Selection.getSelection()) == 1


class GroupCommand(object):
    def GetResources(self):
        return {"Pixmap"  : "MagicPart_group.png",
                "MenuText": "group",
                "ToolTip" : "make a group of several shapes"}

    def Activated(self):
        sel = distinct_list(FreeCADGui.Selection.getSelection())
        need_recompute = P.autorecomp or all(not isTouched(s) for s in sel)

        if P.incmdline:
            FreeCADGui.doCommand("_ftr = MagicPart.group(*%s)"%ftrstr(sel))
            if need_recompute:
                FreeCADGui.doCommand("MagicPart.recompute([_ftr])")
            if P.autosel:
                FreeCADGui.doCommand("MagicPart.select([_ftr])")

        else:
            ftr = group(*sel)
            if need_recompute:
                recompute([ftr])
            if P.autosel:
                select([ftr])

    def IsActive(self):
        return len(FreeCADGui.Selection.getSelection()) > 0

class MaskCommand(object):
    def GetResources(self):
        return {"Pixmap"  : "MagicPart_mask.png",
                "MenuText": "mask",
                "ToolTip" : "make a mask of several shapes"}

    def Activated(self):
        target = FreeCADGui.Selection.getSelection()[0]
        sel = distinct_list(FreeCADGui.Selection.getSelection()[1:])
        if target in sel:
            sel.remove(target)

        if P.incmdline:
            FreeCADGui.doCommand("_ftr = MagicPart.group_mask(%s, *%s)"%(ftrstr(target), ftrstr(sel)))
            if P.autorecomp:
                FreeCADGui.doCommand("MagicPart.recompute([_ftr])")
            if P.autosel:
                FreeCADGui.doCommand("MagicPart.select([_ftr])")

        else:
            ftr = group_mask(target, *sel)
            if P.autorecomp:
                recompute([ftr])
            if P.autosel:
                select([ftr])

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
        if target in sel:
            sel.remove(target)

        if P.incmdline:
            FreeCADGui.doCommand("_ftr = MagicPart.group_slice(%s, *%s)"%(ftrstr(target), ftrstr(sel)))
            if P.autorecomp:
                FreeCADGui.doCommand("MagicPart.recompute([_ftr])")
            if P.autosel:
                FreeCADGui.doCommand("MagicPart.select([_ftr])")

        else:
            ftr = group_slice(target, *sel)
            if P.autorecomp:
                recompute([ftr])
            if P.autosel:
                select([ftr])

    def IsActive(self):
        return len(FreeCADGui.Selection.getSelection()) > 0


FreeCADGui.addCommand("MagicPart_common", CommonCommand())
FreeCADGui.addCommand("MagicPart_fuse", FuseCommand())
FreeCADGui.addCommand("MagicPart_cut", CutCommand())
FreeCADGui.addCommand("MagicPart_complement", ComplementCommand())
FreeCADGui.addCommand("MagicPart_transform", TransformCommand())
FreeCADGui.addCommand("MagicPart_group", GroupCommand())
FreeCADGui.addCommand("MagicPart_mask", MaskCommand())
FreeCADGui.addCommand("MagicPart_slice", SliceCommand())

oplist = ["MagicPart_common",
          "MagicPart_fuse",
          "MagicPart_cut",
          "MagicPart_complement",
          "MagicPart_transform",
          "MagicPart_group",
          "MagicPart_mask",
          "MagicPart_slice"]

