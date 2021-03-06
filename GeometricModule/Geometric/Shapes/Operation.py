import FreeCAD, Part


def reshape(shape):
    if shape.isNull():
        return shape.copy()
    plc = shape.Placement.toMatrix()
    shape = shape.copy()
    shape.Placement = FreeCAD.Placement()
    return shape.transformGeometry(plc)

def transform(shp, *plcs):
    shp = reshape(shp)
    shp.Placement = FreeCAD.Placement()
    for plc in plcs:
        shp.Placement = plc.multiply(shp.Placement)
    return shp

def complement(shp):
    shp = reshape(shp)
    shp.complement()
    return shp

def common(shps):
    shps = list(shps)
    if any(shp.isNull() for shp in shps):
        return Part.Shape()

    shps1 = [shp for shp in shps if shp.Orientation == "Forward"]
    shps2 = [complement(shp) for shp in shps if shp.Orientation == "Reversed"]

    shps3 = [shp for shp in shps if shp.Orientation not in ("Forward", "Reversed")]
    if len(shps3) != 0:
        raise TypeError(shps3)

    shp1 = None
    if len(shps1) > 1:
        shp1 = reduce(Part.Shape.common, shps1)
    elif len(shps1) == 1:
        shp1 = shps1[0]
    shp2 = None
    if len(shps2) > 1:
        shp2 = shps2[0].multiFuse(shps2[1:])
    elif len(shps2) == 1:
        shp2 = shps2[0]

    if shp1 is None and shp2 is None:
        return None
    elif shp1 is None:
        return complement(shp2)
    elif shp2 is None:
        return shp1
    else:
        return shp1.cut(shp2)

def fuse(shps):
    shps = list(shp for shp in shps if not shp.isNull())

    shps1 = [shp for shp in shps if shp.Orientation == "Forward"]
    shps2 = [complement(shp) for shp in shps if shp.Orientation == "Reversed"]

    shps3 = [shp for shp in shps if shp.Orientation not in ("Forward", "Reversed")]
    if len(shps3) != 0:
        raise TypeError(shps3)

    shp1 = None
    if len(shps1) > 1:
        shp1 = shps1[0].multiFuse(shps1[1:])
    elif len(shps1) == 1:
        shp1 = shps1[0]
    shp2 = None
    if len(shps2) > 1:
        shp2 = reduce(Part.Shape.common, shps2)
    elif len(shps2) == 1:
        shp2 = shps2[0]

    if shp1 is None and shp2 is None:
        return None
    elif shp1 is None:
        return complement(shp2)
    elif shp2 is None:
        return shp1
    else:
        return complement(shp2.cut(shp1))

