import FreeCAD, FreeCADGui
import GeometricResources
from Geometric.Features import *

def do_createPolyhedron(name, tag, icon):
    view_space = FreeCADGui.activeView().getActiveObject("ViewSpace")
    if view_space is not None:
        prefix = "_ftr = FreeCAD.ActiveDocument.%s.newObject"%view_space.Name
    else:
        prefix = "_ftr = FreeCAD.ActiveDocument.addObject"

    FreeCADGui.doCommand(prefix+str(("Part::FeaturePython", name)))
    FreeCADGui.doCommand("Geometric.Polyhedron(_ftr, '%s', '%s')"%(tag, icon))
    FreeCADGui.doCommand("FreeCAD.ActiveDocument.recompute()")
    FreeCADGui.doCommand("FreeCADGui.SendMsgToActiveView('ViewFit')")

class CreateCubeCommand(object):
    def GetResources(self):
        return {"Pixmap"  : ":/icons/primitive/Geometric_cube.svg",
                "MenuText": "cube",
                "ToolTip" : "create a cube"}

    def Activated(self):
        do_createPolyhedron("Cube", "4.4.4", ":/icons/primitive/Geometric_cube.svg")

    def IsActive(self):
        return FreeCAD.ActiveDocument is not None

class CreateTetrahedronCommand(object):
    def GetResources(self):
        return {"Pixmap"  : ":/icons/primitive/Geometric_cube.svg",
                "MenuText": "tetrahedron",
                "ToolTip" : "create a tetrahedron"}

    def Activated(self):
        do_createPolyhedron("Tetrahedron", "3.3.3", ":/icons/primitive/Geometric_cube.svg")

    def IsActive(self):
        return FreeCAD.ActiveDocument is not None

class CreateOctahedronCommand(object):
    def GetResources(self):
        return {"Pixmap"  : ":/icons/primitive/Geometric_cube.svg",
                "MenuText": "octahedron",
                "ToolTip" : "create a octahedron"}

    def Activated(self):
        do_createPolyhedron("Octahedron", "3.3.3.3", ":/icons/primitive/Geometric_cube.svg")

    def IsActive(self):
        return FreeCAD.ActiveDocument is not None

class CreateIcosahedronCommand(object):
    def GetResources(self):
        return {"Pixmap"  : ":/icons/primitive/Geometric_cube.svg",
                "MenuText": "icosahedron",
                "ToolTip" : "create a icosahedron"}

    def Activated(self):
        do_createPolyhedron("Icosahedron", "3.3.3.3.3", ":/icons/primitive/Geometric_cube.svg")

    def IsActive(self):
        return FreeCAD.ActiveDocument is not None

class CreateDodecahedronCommand(object):
    def GetResources(self):
        return {"Pixmap"  : ":/icons/primitive/Geometric_cube.svg",
                "MenuText": "dodecahedron",
                "ToolTip" : "create a dodecahedron"}

    def Activated(self):
        do_createPolyhedron("Dodecahedron", "5.5.5", ":/icons/primitive/Geometric_cube.svg")

    def IsActive(self):
        return FreeCAD.ActiveDocument is not None


FreeCADGui.addCommand("Geometric_cube", CreateCubeCommand())
FreeCADGui.addCommand("Geometric_tetrahedron", CreateTetrahedronCommand())
FreeCADGui.addCommand("Geometric_octahedron", CreateOctahedronCommand())
FreeCADGui.addCommand("Geometric_icosahedron", CreateIcosahedronCommand())
FreeCADGui.addCommand("Geometric_dodecahedron", CreateDodecahedronCommand())

polylist = [
    "Geometric_cube",
    "Geometric_tetrahedron",
    "Geometric_octahedron",
    "Geometric_icosahedron",
    "Geometric_dodecahedron",
]

