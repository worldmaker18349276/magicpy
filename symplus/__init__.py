import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), "../lib"))

from sympy import *
from symplus.typlus import (Functor, is_Tuple, is_Symbol, is_Number, is_Boolean, is_Matrix,
    is_Function, type_match)
from symplus.tuplus import pack_if_not, unpack_if_can, repack_if_can
from symplus.symbplus import free_symbols, rename_variables_in
from symplus.logicplus import Forall, Exist
from symplus.funcplus import (narg, nres, FunctionCompose, FunctionInverse, Apply,
    compose, inverse, solve_inv, as_lambda)
from symplus.setplus import (AbstractSet, St, as_abstract, Contains, Image, is_open, is_closed,
    Interior, Closure, AbsoluteComplement, Exterior, Topology, DiscreteTopology, NaturalTopology)

from symplus.strplus import mprint, mstr
from symplus.matplus import (Mat, i, j, k, x, y, z, r, norm, normalize, dot, cross, angle,
    project)
from symplus.simplus import (sqrtsimp, with_sqrtsimp, is_polynomial, is_simplerel,
    expand_polyeq, canonicalize_polyeq, polyrelsimp, logicrelsimp, do_indexing, matsimp,
    with_matsym, simplify_all)

from symplus.path import (Word, FreeMonoid, Path, IdentityPath, SlicedPath,
    ConcatenatedPath, TensorPath, LambdaPath, MultiplicativePath, AdditivePath,
    TransformationPath, PathMonoid)
from symplus.euclid import (EuclideanSpace, WholeSpace, Halfspace, Sphere, InfiniteCylinder,
    InfiniteCone, Revolution, Box, Cylinder, Cone, T_RR3)
from symplus.affine import (rquat, Transformation, AffineTransformation,
    EuclideanTransformation, Trans, Aff4, E3, SE3, SO3, T3, SE3_star, SO3_star, T3_star,
    translation, rotation, reflection, scaling, shearing, translate, rotate)

