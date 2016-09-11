

class MagicPartWorkbench(Workbench):

    MenuText = "Magic Part"
    ToolTip = "~"
    Icon = """
            /* XPM */
            static const char *icon[]={
            "16 16 2 1",
            "# c #000000",
            ". c None",
            "...##########...",
            "...##########...",
            "..##........##..",
            "..####....####..",
            ".##.########.##.",
            ".##...####...##.",
            "##.....##.....##",
            "##.....##.....##",
            "##.....##.....##",
            "##.....##.....##",
            ".##...####...##.",
            ".##.########.##.",
            "..####....####..",
            "..##........##..",
            "...##########...",
            "...##########..."};
            """

    def Initialize(self):
        import MagicPart
        import MagicPart.Commands
        Gui.doCommand("import MagicPart")
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
                         "OpenSCAD_MeshBoolean",
                         ]
        self.objlist = MagicPart.Commands.objlist
        self.oplist = MagicPart.Commands.oplist
        self.ctrllist = MagicPart.Commands.ctrllist

        self.appendToolbar("Part", self.partlist)
        self.appendToolbar("Mesh", self.meshlist)
        self.appendToolbar("Primitive", self.objlist)
        self.appendToolbar("Operation", self.oplist)

        self.appendMenu("Magic Part", self.objlist)
        self.appendMenu("Magic Part", self.oplist)
        self.appendMenu("Magic Part", self.ctrllist)

    def Activated(self):
        return

    def Deactivated(self):
        return

    def ContextMenu(self, recipient):
        self.appendContextMenu("Control", self.ctrllist)

    def GetClassName(self): 
        return "Gui::PythonWorkbench"

Gui.addWorkbench(MagicPartWorkbench())

