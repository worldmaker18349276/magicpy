import math
import FreeCAD, Units

Vec = FreeCAD.Vector
Plc = FreeCAD.Placement

k = Vec(0,0,1)

def k2d(d):
    return Plc(Vec(), FreeCAD.Rotation(k,d))

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

    else:
        return v1 == v2
