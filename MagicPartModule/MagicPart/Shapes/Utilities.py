import FreeCAD, Part


def reshape(shape):
    if shape.isNull():
        return shape.copy()
    plc = shape.Placement.toMatrix()
    shape = shape.copy()
    shape.Placement = FreeCAD.Placement()
    return shape.transformGeometry(plc)

def mass(shape):
    M = 0.0
    for sld in shape.Solids:
        M += sld.Mass
    return M

def center(shape):
    R = FreeCAD.Vector()
    M = 0.0
    for sld in shape.Solids:
        R += sld.CenterOfMass*sld.Mass
        M += sld.Mass
    if M == 0.0:
        return None
    else:
        return R*(1/M)

