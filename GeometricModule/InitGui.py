

class GeometricWorkbench(Workbench):

    MenuText = "Geometric"
    ToolTip = "~"
    Icon = ":/icons/view-isometric.svg"

    def Initialize(self):
        pass

    def Activated(self):
        return

    def Deactivated(self):
        return

    def ContextMenu(self, recipient):
        pass

    def GetClassName(self): 
        return "Gui::PythonWorkbench"

Gui.addWorkbench(GeometricWorkbench())

