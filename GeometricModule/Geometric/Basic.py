import math
import FreeCAD, Units

Vec = FreeCAD.Vector
Plc = FreeCAD.Placement
Rot = FreeCAD.Rotation

o = Vec()
k = Vec(0,0,1)
bb = FreeCAD.BoundBox(-1.5,-1.5,-1.5, 1.5, 1.5, 1.5)

def k2d(d):
    return Plc(Vec(), FreeCAD.Rotation(k,d))

def mirror(base, norm):
    m = FreeCAD.Matrix()
    m.move(base*(-1))
    m.scale(-1,-1,-1)
    m.move(base)
    return m.multiply(Plc(Vec(), FreeCAD.Rotation(norm, 180)).toMatrix())

def fuzzyCompare(v1, v2):
    if isinstance(v1, Units.Quantity):
        if not isinstance(v2, Units.Quantity):
            return False

        return abs((v1 - v2).Value) < 1e-7

    elif isinstance(v1, (int, long, float)):
        if not isinstance(v2, (int, long, float)):
            return False

        return abs(v1 - v2) < 1e-7

    elif isinstance(v1, (tuple, list)):
        if not isinstance(v2, (tuple, list)):
            return False

        if len(v1) != len(v2):
            return False

        return all(fuzzyCompare(e1, e2) for e1, e2 in zip(v1, v2))

    elif isinstance(v1, dict):
        if not isinstance(v2, dict):
            return False

        if set(v1.keys()) != set(v2.keys()):
            return False

        return all(fuzzyCompare(v1[k], v2[k]) for k in v1.keys())

    elif isinstance(v1, Vec):
        if not isinstance(v2, Vec):
            return False

        return (v1 - v2).Length < 1e-7

    elif isinstance(v1, FreeCAD.Rotation):
        if not isinstance(v2, FreeCAD.Rotation):
            return False

        q1 = v1.Q
        q2 = v2.Q
        return abs(q1[0]*q2[0] + q1[1]*q2[1] + q1[2]*q2[2] + q1[3]*q2[3]) >= math.cos(1e-12/2)

    elif isinstance(v1, Plc):
        if not isinstance(v2, Plc):
            return False

        if not fuzzyCompare(v1.Base, v2.Base):
            return False

        return fuzzyCompare(v1.Rotation, v2.Rotation)

    elif isinstance(v1, FreeCAD.BoundBox):
        if not isinstance(v2, FreeCAD.BoundBox):
            return False

        return (fuzzyCompare(v1.getPoint(4), v2.getPoint(4)) and
                fuzzyCompare(v1.getPoint(2), v2.getPoint(2)))

    else:
        return v1 == v2
