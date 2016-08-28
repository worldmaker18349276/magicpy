import FreeCAD, Mesh


def asMesh(shape, precision=0.01):
    return Mesh.Mesh(shape.tessellate(precision))

def remesh(mesh):
    plc = mesh.Placement.toMatrix()
    mesh = Mesh.Mesh(mesh)
    mesh.Placement = FreeCAD.Placement()
    mesh.transform(plc)
    return mesh

def orientation(mesh):
    mesh_ = Mesh.Mesh(mesh)
    mesh_.offset(0.001)
    Mesh.Mesh().offset(0)
    if mesh_.Volume > mesh.Volume:
        return "Forward"
    else:
        return "Reversed"

def mass(mesh):
    M = 0.0
    for submesh in mesh.getSeparateComponents():
        if orientation(submesh) == "Forward":
            M += submesh.Volume
        else:
            M -= submesh.Volume

def center(mesh):
    return mesh.BoundBox.Center

