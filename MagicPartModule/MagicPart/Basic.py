import math
from sympy import sympify
from symplus.typlus import is_Matrix, is_Number
from symplus.matplus import Mat
from symplus.affine import EuclideanTransformation, AffineTransformation, augment
import FreeCAD, Units


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

    elif isinstance(v1, FreeCAD.Vector):
        if not isinstance(v2, FreeCAD.Vector):
            return False

        return (v1 - v2).Length < 1e-7

    elif isinstance(v1, FreeCAD.Rotation):
        if not isinstance(v2, FreeCAD.Rotation):
            return False

        q1 = v1.Q
        q2 = v2.Q
        return abs(q1[0]*q2[0] + q1[1]*q2[1] + q1[2]*q2[2] + q1[3]*q2[3]) >= math.cos(1e-12/2)

    elif isinstance(v1, FreeCAD.Placement):
        if not isinstance(v2, FreeCAD.Placement):
            return False

        if not fuzzyCompare(v1.Base, v2.Base):
            return False

        return fuzzyCompare(v1.Rotation, v2.Rotation)

    else:
        return v1 == v2


# SymPy

def spstr2spexpr(spstr):
    from sympy.parsing.sympy_parser import parse_expr
    from sympy.core.compatibility import exec_
    global_dict = {}
    exec_("from symplus import *", global_dict)
    return parse_expr(spstr, global_dict=global_dict, evaluate=False)

def spexpr2spstr(spexpr):
    from sympy.printing import sstr
    if is_Matrix(spexpr) and spexpr.shape == (3, 1):
        return sstr(list(spexpr))
    else:
        return sstr(spexpr)

def fcexpr2spexpr(expr):
    if isinstance(expr, (int, long, float)):
        return sympify(expr)

    elif isinstance(expr, FreeCAD.Matrix):
        return Mat(4, 4, expr.A)

    elif isinstance(expr, FreeCAD.Vector):
        return Mat([expr.x, expr.y, expr.z])

    elif isinstance(expr, FreeCAD.Placement):
        tvec = fcexpr2spexpr(expr.Base)
        q = expr.Rotation.Q
        rquat = Mat([q[-1], q[0], q[1], q[2]])
        trans = EuclideanTransformation(tvec=tvec, rquat=rquat)
        return trans

    else:
        raise TypeError

def spexpr2fcexpr(expr):
    if is_Number(expr):
        return float(expr.evalf())

    elif is_Matrix(expr):
        if expr.shape == (3, 1):
            return FreeCAD.Vector(*expr.evalf())
        elif expr.shape == (4, 4):
            return FreeCAD.Matrix(*expr.evalf())
        else:
            TypeError

    elif isinstance(expr, AffineTransformation):
        return FreeCAD.Placement(spexpr2fcexpr(augment(m=expr.matrix, v=expr.vector).evalf()))

    elif isinstance(expr, AffineTransformation):
        return FreeCAD.Placement(spexpr2fcexpr(augment(m=expr.matrix, v=expr.vector).evalf()))

    else:
        raise TypeError


# ParameterGroup

class Param(object):
    def __init__(self):
        self.group = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/MagicPart")

    def setDefault(self):
        self.group.Clear()

    @property
    def cached(self):
        return self.group.GetBool("boolean_cached", False)

    @cached.setter
    def cached(self, val):
        return self.group.SetBool("boolean_cached", val)

    @property
    def autosel(self):
        return self.group.GetBool("boolean_auto_select", True)

    @autosel.setter
    def autosel(self, val):
        return self.group.SetBool("boolean_auto_select", val)

    @property
    def originop(self):
        return self.group.GetBool("boolean_use_original", False)

    @originop.setter
    def originop(self, val):
        return self.group.SetBool("boolean_use_original", val)

    @property
    def autorecomp(self):
        return self.group.GetBool("boolean_auto_recompute", False)

    @autorecomp.setter
    def autorecomp(self, val):
        return self.group.SetBool("boolean_auto_recompute", val)

    @property
    def autotrace(self):
        return self.group.GetBool("boolean_auto_tracing", True)

    @autotrace.setter
    def autotrace(self, val):
        return self.group.SetBool("boolean_auto_tracing", val)

    @property
    def rep(self):
        return self.group.GetString("solid_representation", "Shape")

    @rep.setter
    def rep(self, val):
        return self.group.SetString("solid_representation", val)

    @property
    def hard(self):
        return self.group.GetBool("solid_hard_construct", True)

    @hard.setter
    def hard(self, val):
        return self.group.SetBool("solid_hard_construct", val)

    @property
    def pert(self):
        return self.group.GetBool("solid_perturbation", False)

    @pert.setter
    def pert(self, val):
        return self.group.SetBool("solid_perturbation", val)

    @property
    def incmdline(self):
        return self.group.GetBool("tool_in_commandline", True)

    @incmdline.setter
    def incmdline(self, val):
        return self.group.SetBool("tool_in_commandline", val)

P = Param()
