from MagicPart.Basic import spexpr2fcexpr
from MagicPart.Meshes.Utilities import remesh, orientation
import OpenSCADUtils


def complement(mesh, remeshed=False):
    if remeshed:
        mesh = remesh(mesh)
    else:
        mesh = Mesh.Mesh(mesh)
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

    # # broken
    # mesh1 = None
    # if len(meshes1) > 0:
    #     mesh1 = reduce(Mesh.Mesh.intersect, meshes1)
    # mesh2 = None
    # if len(meshes2) > 0:
    #     mesh2 = reduce(Mesh.Mesh.unite, meshes2)

    # if mesh1 is None and mesh2 is None:
    #     return None
    # elif mesh1 is None:
    #     return complement(mesh2)
    # elif mesh2 is None:
    #     return mesh1
    # else:
    #     return mesh1.difference(mesh2)

    mesh1 = None
    if len(meshes1) > 1:
        mesh1 = OpenSCADUtils.meshoptempfile('intersection', meshes1)
    elif len(meshes1) == 1:
        mesh1 = meshes1[0]
    mesh2 = None
    if len(meshes2) > 1:
        mesh2 = OpenSCADUtils.meshoptempfile('union', meshes2)
    elif len(meshes2) == 1:
        mesh2 = meshes2[0]

    if mesh1 is None and mesh2 is None:
        return None
    elif mesh1 is None:
        return complement(mesh2)
    elif mesh2 is None:
        return mesh1
    else:
        return OpenSCADUtils.meshoptempfile('difference', [mesh1, mesh2])

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

    # # broken
    # mesh1 = None
    # if len(meshes1) > 0:
    #     mesh1 = reduce(Mesh.Mesh.unite, meshes1)
    # mesh2 = None
    # if len(meshes2) > 0:
    #     mesh2 = reduce(Mesh.Mesh.intersect, meshes2)

    # if mesh1 is None and mesh2 is None:
    #     return None
    # elif mesh1 is None:
    #     return complement(mesh2)
    # elif mesh2 is None:
    #     return mesh1
    # else:
    #     return complement(mesh2.difference(mesh1))

    mesh1 = None
    if len(meshes1) > 1:
        mesh1 = OpenSCADUtils.meshoptempfile('union', meshes1)
    elif len(meshes1) == 1:
        mesh1 = meshes1[0]
    mesh2 = None
    if len(meshes2) > 1:
        mesh2 = OpenSCADUtils.meshoptempfile('intersection', meshes2)
    elif len(meshes2) == 1:
        mesh2 = meshes2[0]

    if mesh1 is None and mesh2 is None:
        return None
    elif mesh1 is None:
        return complement(mesh2)
    elif mesh2 is None:
        return mesh1
    else:
        return complement(OpenSCADUtils.meshoptempfile('difference', [mesh2, mesh1]))

def compound(meshes):
    comp = Mesh.Mesh()
    for mesh in meshes:
        comp.addMesh(remesh(mesh))
    return comp

def transform(mesh, trans):
    mesh = remesh(mesh)
    mesh.Placement = spexpr2fcexpr(trans)
    return mesh

