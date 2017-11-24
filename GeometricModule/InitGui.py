

class GeometricWorkbench(Workbench):

    MenuText = "Geometric"
    ToolTip = "~"
    Icon = ":/icons/view-isometric.svg"

    def Initialize(self):
        import Geometric
        import Geometric.Commands
        Gui.doCommand("import Geometric")
        Gui.activateWorkbench("PartWorkbench")
        Gui.activateWorkbench("MeshWorkbench")
        Gui.activateWorkbench("OpenSCADWorkbench")

        self.partlist = ["Part_Box",
                         "Part_Cylinder",
                         "Part_Sphere",
                         "Part_Cone",
                         "Part_Torus",
                         "Part_Common",
                         "Part_Fuse",
                         "Part_Cut",
                         "Part_BooleanFragments",
                         "Part_Slice",
                         "Part_XOR",
                         "Part_CheckGeometry"]
        self.meshlist = ["Mesh_BuildRegularSolid",
                         "Mesh_FromPartShape",
                         "OpenSCAD_AddOpenSCADElement",
                         "OpenSCAD_MeshBoolean"]
        self.ctrllist = Geometric.Commands.ctrllist
        self.objlist = Geometric.Commands.objlist

        self.appendToolbar("Part", self.partlist)
        self.appendToolbar("Mesh", self.meshlist)
        self.appendToolbar("Geometric", self.objlist)

        self.appendMenu("Geometric", self.ctrllist)
        self.appendMenu("Geometric", self.objlist)

    def Activated(self):
        return

    def Deactivated(self):
        return

    def ContextMenu(self, recipient):
        self.appendContextMenu("Control", self.ctrllist)

    def GetClassName(self): 
        return "Gui::PythonWorkbench"

Gui.addWorkbench(GeometricWorkbench())

