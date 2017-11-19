import math
import FreeCAD
from MagicPart.Basic import fuzzyCompare
from MagicPart.Features.Utilities import *


# def makeArrow(v, scale=1):
#     l = v.Length
#     if fuzzyCopmare(l, 0):
#         return Part.makeSphere(0.04*scale)
#     head = Part.makeCone(0, 0.1*scale, 0.3*scale, v, v*(-1))
#     tail = Part.makeCylinder(0.04*scale, abs(l-0.3*scale), FreeCAD.Vector(), v*math.copysign(1,l-0.3*scale))
#     return head.fuse(tail)

class VariableViewProxy(object):
    pass

class VariableProxy(FeaturePythonProxy):
    pass

class NumberProxy(VariableProxy):
    def onChanged(self, obj, p):
        if p == "Proxy":
            if "Number" not in obj.PropertiesList:
                obj.addProperty("App::PropertyFloat", "Number")
                obj.Number = 0.0
            obj.setEditorMode("Placement", 2)
            # if FreeCAD.GuiUp:
            #     obj.ViewObject.Proxy = VariableViewProxy()

    def execute(self, obj):
        pass

class VectorProxy(VariableProxy):
    def onChanged(self, obj, p):
        if p == "Proxy":
            if "Vector" not in obj.PropertiesList:
                obj.addProperty("App::PropertyVector", "Vector")
                obj.Vector = FreeCAD.Vector()
            obj.setEditorMode("Placement", 2)
            # if FreeCAD.GuiUp:
            #     obj.ViewObject.Proxy = VariableViewProxy()
    
    def execute(self, obj):
        pass
        # obj.Shape = makeArrow(obj.Vector)

class PlacementProxy(VariableProxy):
    def onChanged(self, obj, p):
        if p == "Proxy":
            pass
            # if FreeCAD.GuiUp:
            #     obj.ViewObject.Proxy = VariableViewProxy()

    def execute(self, obj):
        pass

Number = NumberProxy
Vector = VectorProxy
Placement = PlacementProxy
