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
        if any(isDerivedFrom(s, ("Part::Compound", Compound)) for s in sel):
            need_recompute = P.autorecomp
            method = cross_common
        else:
            need_recompute = P.autorecomp or all(not isTouched(s) for s in sel)
            method = common

        if P.incmdline:
            FreeCADGui.doCommand("_ftr = MagicPart.%s(*%s)"%(method.__name__, ftrstr(sel)))
            if need_recompute:
                FreeCADGui.doCommand("MagicPart.recompute([_ftr])")
            if P.autosel:
                FreeCADGui.doCommand("MagicPart.select([_ftr])")

        else:
            ftr = method(*sel)
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

        if P.incmdline:
            FreeCADGui.doCommand("_ftr = MagicPart.fuse(*%s)"%ftrstr(sel))
            if need_recompute:
                FreeCADGui.doCommand("MagicPart.recompute([_ftr])")
            if P.autosel:
                FreeCADGui.doCommand("MagicPart.select([_ftr])")

        else:
            ftr = fuse(sel)
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

        if P.incmdline:
            FreeCADGui.doCommand("_ftr = MagicPart.cut(%s, %s)"%(ftrstr(sel[0]), ftrstr(sel[1])))
            if need_recompute:
                FreeCADGui.doCommand("MagicPart.recompute([_ftr])")
            if P.autosel:
                FreeCADGui.doCommand("MagicPart.select([_ftr])")

        else:
            ftr = cut(sel[0], sel[1])
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

        if P.incmdline:
            FreeCADGui.doCommand("_ftr = MagicPart.complement(%s)"%ftrstr(sel))
            if need_recompute:
                FreeCADGui.doCommand("MagicPart.recompute([_ftr])")
            if P.autosel:
                FreeCADGui.doCommand("MagicPart.select([_ftr])")

        else:
            ftr = complement(sel)
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

        if P.incmdline:
            FreeCADGui.doCommand("_ftr = MagicPart.transform(%s)"%ftrstr(sel))
            if need_recompute:
                FreeCADGui.doCommand("MagicPart.recompute([_ftr])")
            if P.autosel:
                FreeCADGui.doCommand("MagicPart.select([_ftr])")

        else:
            ftr = transform(sel)
            if need_recompute:
                recompute([ftr])
            if P.autosel:
                select([ftr])

    def IsActive(self):
        return len(FreeCADGui.Selection.getSelection()) == 1


class PartitionCommand(object):
    def GetResources(self):
        return {"Pixmap"  : "MagicPart_partition.png",
                "MenuText": "partition",
                "ToolTip" : "make a partition of several shapes"}

    def Activated(self):
        sel = distinct_list(FreeCADGui.Selection.getSelection())

        if P.incmdline:
            FreeCADGui.doCommand("_ftr = MagicPart.partition(*%s)"%ftrstr(sel))
            if P.autorecomp:
                FreeCADGui.doCommand("MagicPart.recompute([_ftr])")
            if P.autosel:
                FreeCADGui.doCommand("MagicPart.select([_ftr])")

        else:
            ftr = partition(*sel)
            if P.autorecomp:
                recompute([ftr])
            if P.autosel:
                select([ftr])

    def IsActive(self):
        return len(FreeCADGui.Selection.getSelection()) > 0

class FragmentCommand(object):
    def GetResources(self):
        return {"Pixmap"  : "MagicPart_fragment.png",
                "MenuText": "fragment",
                "ToolTip" : "make a fragment of several shapes"}

    def Activated(self):
        sel = distinct_list(FreeCADGui.Selection.getSelection())

        if P.incmdline:
            FreeCADGui.doCommand("_ftr = MagicPart.fragment(*%s)"%ftrstr(sel))
            if P.autorecomp:
                FreeCADGui.doCommand("MagicPart.recompute([_ftr])")
            if P.autosel:
                FreeCADGui.doCommand("MagicPart.select([_ftr])")

        else:
            ftr = fragment(*sel)
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
            FreeCADGui.doCommand("_ftr = MagicPart.slice(%s, *%s)"%(ftrstr(target), ftrstr(sel)))
            if P.autorecomp:
                FreeCADGui.doCommand("MagicPart.recompute([_ftr])")
            if P.autosel:
                FreeCADGui.doCommand("MagicPart.select([_ftr])")

        else:
            ftr = slice(target, *sel)
            if P.autorecomp:
                recompute([ftr])
            if P.autosel:
                select([ftr])

    def IsActive(self):
        return len(FreeCADGui.Selection.getSelection()) > 0


class CompoundCommand(object):
    def GetResources(self):
        return {"Pixmap"  : "MagicPart_compound.png",
                "MenuText": "compound",
                "ToolTip" : "make a compound of several shapes"}

    def Activated(self):
        sel = distinct_list(FreeCADGui.Selection.getSelection())
        need_recompute = P.autorecomp or all(not isTouched(s) for s in sel)

        if P.incmdline:
            FreeCADGui.doCommand("_ftr = MagicPart.compound(*%s)"%ftrstr(sel))
            if need_recompute:
                FreeCADGui.doCommand("MagicPart.recompute([_ftr])")
            if P.autosel:
                FreeCADGui.doCommand("MagicPart.select([_ftr])")

        else:
            ftr = compound(*sel)
            if need_recompute:
                recompute([ftr])
            if P.autosel:
                select([ftr])

    def IsActive(self):
        return len(FreeCADGui.Selection.getSelection()) > 0

# class CompoundRemoveCommand(object):
#     def GetResources(self):
#         return {"Pixmap"  : "MagicPart_compoundRemove.png",
#                 "MenuText": "compound remove",
#                 "ToolTip" : "remove several elements from compound"}
# 
#     def Activated(self):
#         sel = distinct_list(FreeCADGui.Selection.getSelection())
#         if len(sel) != 1:
#             raise ValueError
#         if not isDerivedFrom(sel[0], ("Part::Compound", Compound)):
#             raise TypeError
#         subsel = ftrlist(outOf(link)[0] for link in getSubSelection() if link[1].startswith("Face"))
#         remained = ftrlist(sel[0].OutList)
#         for s in subsel:
#             remained.remove(s)
#         need_recompute = all(not isTouched(s) for s in remained) or P.autorecomp
# 
#         if P.incmdline:
#             FreeCADGui.doCommand("%s.ViewObject.hide()"%ftrstr(sel[0]))
#             if len(remained) > 0:
#                 FreeCADGui.doCommand("_ftr = MagicPart.compound(%s)"%ftrstr(remained))
#                 if need_recompute:
#                     FreeCADGui.doCommand("MagicPart.recompute([_ftr])")
#                 if P.autosel:
#                     FreeCADGui.doCommand("MagicPart.select([_ftr])")
# 
#             else:
#                 if P.autosel:
#                     FreeCADGui.doCommand("MagicPart.select([])")
# 
#         else:
#             sel[0].ViewObject.hide()
#             if len(remained) > 0:
#                 ftr = compound(remained)
#                 if need_recompute:
#                     recompute([ftr])
#                 if P.autosel:
#                     select([ftr])
# 
#             else:
#                 if P.autosel:
#                     select([])
# 
#     def IsActive(self):
#         return len(FreeCADGui.Selection.getSelection()) > 0
# 
# class CompoundFuseCommand(object):
#     def GetResources(self):
#         return {"Pixmap"  : "MagicPart_compoundFuse.png",
#                 "MenuText": "compound fuse",
#                 "ToolTip" : "fuse several elements in compound"}
# 
#     def Activated(self):
#         sel = distinct_list(FreeCADGui.Selection.getSelection())
#         if len(sel) != 1:
#             raise ValueError
#         if not isDerivedFrom(sel[0], ("Part::Compound", Compound)):
#             raise TypeError
#         subsel = ftrlist(outOf(link)[0] for link in getSubSelection() if link[1].startswith("Face"))
#         need_recompute = all(not isTouched(s) for s in sel[0].OutList) or P.autorecomp
# 
#         if P.incmdline:
#             FreeCADGui.doCommand("_ftr = MagicPart.compoundFuse(%s, %s)"%(ftrstr(sel[0]), ftrstr(subsel)))
#             if need_recompute:
#                 FreeCADGui.doCommand("MagicPart.recompute([_ftr])")
#             if P.autosel:
#                 FreeCADGui.doCommand("MagicPart.select([_ftr])")
# 
#         else:
#             ftr = compoundFuse(sel[0], subsel)
#             if need_recompute:
#                 recompute([ftr])
#             if P.autosel:
#                 select([ftr])
# 
#     def IsActive(self):
#         return len(FreeCADGui.Selection.getSelection()) > 0
# 
# class CompoundTransformCommand(object):
#     def GetResources(self):
#         return {"Pixmap"  : "MagicPart_compoundTransform.png",
#                 "MenuText": "compound transform",
#                 "ToolTip" : "transform several elements in compound"}
# 
#     def Activated(self):
#         sel = ftrlist(FreeCADGui.Selection.getSelection())
#         if len(sel) != 1:
#             raise ValueError
#         if not isDerivedFrom(sel[0], ("Part::Compound", Compound)):
#             raise TypeError
#         subsel = ftrlist(outOf(link)[0] for link in getSubSelection() if link[1].startswith("Face"))
#         need_recompute = all(not isTouched(s) for s in sel[0].OutList) or P.autorecomp
# 
#         if P.incmdline:
#             FreeCADGui.doCommand("_ftr = MagicPart.compoundTransform(%s, %s)"%(ftrstr(sel[0]), ftrstr(subsel)))
#             if need_recompute:
#                 FreeCADGui.doCommand("MagicPart.recompute([_ftr])")
#             if P.autosel:
#                 FreeCADGui.doCommand("MagicPart.select([_ftr])")
# 
#         else:
#             ftr = compoundTransform(sel[0], subsel)
#             if need_recompute:
#                 recompute([ftr])
#             if P.autosel:
#                 select([ftr])
# 
#     def IsActive(self):
#         return len(FreeCADGui.Selection.getSelection()) > 0


class ApartCommand(object):
    def GetResources(self):
        return {"Pixmap"  : "MagicPart_apart.png",
                "MenuText": "apart",
                "ToolTip" : "apart compound from a point"}

    def Activated(self):
        sel = FreeCADGui.Selection.getSelection()[0]
        need_recompute = not isTouched(sel) or P.autorecomp

        if P.incmdline:
            FreeCADGui.doCommand("_ftr = MagicPart.apart(%s)"%ftrstr(sel))
            if need_recompute:
                FreeCADGui.doCommand("MagicPart.recompute([_ftr])")
            if P.autosel:
                FreeCADGui.doCommand("MagicPart.select([_ftr])")

        else:
            ftr = apart(sel)
            if need_recompute:
                recompute([ftr])
            if P.autosel:
                select([ftr])

    def IsActive(self):
        return len(FreeCADGui.Selection.getSelection()) == 1

class MaskCommand(object):
    def GetResources(self):
        return {"Pixmap"  : "MagicPart_mask",
                "MenuText": "mask",
                "ToolTip" : "mask several shapes"}

    def Activated(self):
        sel = ftrlist(FreeCADGui.Selection.getSelection())

        if len(sel) > 1:
            if P.incmdline:
                FreeCADGui.doCommand("_ftrs = []")
                for s in sel:
                    FreeCADGui.doCommand("_ftrs.append(MagicPart.mask(%s))"%ftrstr(s))
                if P.autorecomp:
                    FreeCADGui.doCommand("MagicPart.recompute(_ftrs)")
                if P.autosel:
                    FreeCADGui.doCommand("MagicPart.select(_ftrs)")

            else:
                ftrs = [mask(s) for s in sel]
                if P.autorecomp:
                    recompute(ftrs)
                if P.autosel:
                    select(ftrs)
    
        else:
            need_recompute = not isTouched(sel[0]) or P.autorecomp

            if P.incmdline:
                FreeCADGui.doCommand("_ftr = MagicPart.mask(%s)"%ftrstr(sel[0]))
                if need_recompute:
                    FreeCADGui.doCommand("MagicPart.recompute([_ftr])")
                if P.autosel:
                    FreeCADGui.doCommand("MagicPart.select([_ftr])")

            else:
                ftr = mask(sel[0])
                if need_recompute:
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
FreeCADGui.addCommand("MagicPart_partition", PartitionCommand())
FreeCADGui.addCommand("MagicPart_fragment", FragmentCommand())
FreeCADGui.addCommand("MagicPart_slice", SliceCommand())
FreeCADGui.addCommand("MagicPart_compound", CompoundCommand())
# FreeCADGui.addCommand("MagicPart_compoundRemove", CompoundRemoveCommand())
# FreeCADGui.addCommand("MagicPart_compoundFuse", CompoundFuseCommand())
# FreeCADGui.addCommand("MagicPart_compoundTranform", CompoundTransformCommand())
FreeCADGui.addCommand("MagicPart_apart", ApartCommand())
FreeCADGui.addCommand("MagicPart_mask", MaskCommand())

oplist = ["MagicPart_common",
          "MagicPart_fuse",
          "MagicPart_cut",
          "MagicPart_complement",
          "MagicPart_transform",
          "MagicPart_partition",
          "MagicPart_fragment",
          "MagicPart_slice",
          "MagicPart_compound",
        #   "MagicPart_compoundRemove",
        #   "MagicPart_compoundFuse",
        #   "MagicPart_compoundTranform",
          "MagicPart_apart",
          "MagicPart_mask"]

