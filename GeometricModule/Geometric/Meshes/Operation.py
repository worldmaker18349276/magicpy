import FreeCAD, Mesh, OpenSCADUtils


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

def transform(mesh, plc):
    mesh = remesh(mesh)
    mesh.Placement = plc
    return mesh

def complement(mesh):
    mesh = remesh(mesh)
    mesh.flipNormals()
    return mesh

def common(meshes):
    meshes1 = []
    meshes2 = []
    for mesh in meshes:
        o = orientation(mesh)
        if o == "Forward":
            meshes1.append(mesh)
        elif o == "Reversed":
            meshes2.append(complement(mesh))
        else:
            raise TypeError

    mesh1 = None
    if len(meshes1) > 1:
        mesh1 = OpenSCADUtils.meshoptempfile("intersection", meshes1)
    elif len(meshes1) == 1:
        mesh1 = meshes1[0]
    mesh2 = None
    if len(meshes2) > 1:
        mesh2 = OpenSCADUtils.meshoptempfile("union", meshes2)
    elif len(meshes2) == 1:
        mesh2 = meshes2[0]

    if mesh1 is None and mesh2 is None:
        return None
    elif mesh1 is None:
        return complement(mesh2)
    elif mesh2 is None:
        return mesh1
    else:
        return OpenSCADUtils.meshoptempfile("difference", [mesh1, mesh2])

def fuse(meshes):
    meshes1 = []
    meshes2 = []
    for mesh in meshes:
        o = orientation(mesh)
        if o == "Forward":
            meshes1.append(mesh)
        elif o == "Reversed":
            meshes2.append(complement(mesh))
        else:
            raise TypeError

    mesh1 = None
    if len(meshes1) > 1:
        mesh1 = OpenSCADUtils.meshoptempfile("union", meshes1)
    elif len(meshes1) == 1:
        mesh1 = meshes1[0]
    mesh2 = None
    if len(meshes2) > 1:
        mesh2 = OpenSCADUtils.meshoptempfile("intersection", meshes2)
    elif len(meshes2) == 1:
        mesh2 = meshes2[0]

    if mesh1 is None and mesh2 is None:
        return None
    elif mesh1 is None:
        return complement(mesh2)
    elif mesh2 is None:
        return mesh1
    else:
        return complement(OpenSCADUtils.meshoptempfile("difference", [mesh2, mesh1]))

