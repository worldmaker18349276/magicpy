from setplus import AbstractSet
from matplus import DummyMatrixSymbol
from sympy.core.relational import Ne, Eq
from sympy.core.numbers import pi
from sympy.core.basic import Basic
from sympy.matrices.dense import eye, zeros, diag, Matrix
from sympy.matrices.immutable import ImmutableMatrix as Mat
from sympy.matrices.matrices import ShapeError
from sympy.matrices.expressions.matexpr import MatrixSymbol, Identity, ZeroMatrix
from sympy.matrices.expressions.determinant import det
from sympy.matrices.expressions.trace import trace
from sympy.functions.elementary.trigonometric import cos, sin, acos
from sympy.functions.elementary.miscellaneous import sqrt


m = MatrixSymbol('m', 4, 4)
eye3 = Identity(3)
eye4 = Identity(4)
eye4row3 = eye4[3,:]
zeros3 = ZeroMatrix(3,1)
i, j, k = e = Mat([1,0,0]), Mat([0,1,0]), Mat([0,0,1])
def augment(mat=eye3, vec=zeros3):
    if mat.shape != (3, 3):
        raise ShapeError("Matrices size mismatch.")
    if vec.shape != (3, 1):
        raise ShapeError("Matrices size mismatch.")
    return Mat(mat).row_join(vec).col_join(eye4row3)


GL4 = GeneralLinearGroup4 = AbstractSet(m,
    Ne(det(m), 0))
Aff3 = AffineGroup3 = AbstractSet(m,
    Ne(det(m), 0) &
    Eq(m[3,:], eye4row3))
SE3 = SpecialEuclideanGroup3 = AbstractSet(m,
    Eq(det(m), 1) &
    Eq(m[3,:], eye4row3) &
    Eq(m[:3,:3].T*m[:3,:3], eye3))
SO3 = SpecialOrthogonalGroup3 = AbstractSet(m,
    Eq(det(m), 1) &
    Eq(m[3,:], eye4row3) &
    Eq(m[:3,:3].T*m[:3,:3], eye3) &
    Eq(m[:3,3], zeros3))
T3 = TranslationGroup3 = AbstractSet(m,
    Eq(m[3,:], eye4row3) &
    Eq(m[:3,:3], eye3))


def norm(vec):
    return sqrt(sum(v**2 for v in vec))

def normalize(vec):
    return vec/norm(vec)

def rvec2rmat(rvec):
    x, y, z = axis = normalize(rvec)
    angle = norm(rvec)
    cpm = Mat([[ 0,-z, y],
               [ z, 0,-x],
               [-y, x, 0]])
    return eye3*cos(angle) + cpm*sin(angle) + axis*axis.T*(1-cos(angle))

def rmat2rvec(rmat):
    angle = acos((trace(rmat)-1)/2)
    factor = angle/(2*sin(angle))
    axis = Mat([rmat[2,1] - rmat[1,2],
                rmat[0,2] - rmat[2,0],
                rmat[1,0] - rmat[0,1]])
    return axis*factor


def rotation(rvec):
    """
    >>> from sympy import *
    >>> from matplus import matsimp
    >>> t = Symbol('t', positive=True)
    >>> rotation(t*i)
    Matrix([
    [1,      0,       0, 0],
    [0, cos(t), -sin(t), 0],
    [0, sin(t),  cos(t), 0],
    [0,      0,       0, 1]])
    >>> rotation(t*(i/sqrt(2)+k/sqrt(2)))
    Matrix([
    [  cos(t)/2 + 1/2, -sqrt(2)*sin(t)/2,   -cos(t)/2 + 1/2, 0],
    [sqrt(2)*sin(t)/2,            cos(t), -sqrt(2)*sin(t)/2, 0],
    [ -cos(t)/2 + 1/2,  sqrt(2)*sin(t)/2,    cos(t)/2 + 1/2, 0],
    [               0,                 0,                 0, 1]])
    >>> simplify(matsimp(SO3.contains(_)))
    True
    """
    return augment(mat=rvec2rmat(rvec))

def reflection(fvec):
    """
    >>> from sympy import *
    >>> from matplus import matsimp
    >>> reflection(i)
    Matrix([
    [-1, 0, 0, 0],
    [ 0, 1, 0, 0],
    [ 0, 0, 1, 0],
    [ 0, 0, 0, 1]])
    >>> reflection(i-sqrt(2)*j)
    Matrix([
    [        1/3, 2*sqrt(2)/3, 0, 0],
    [2*sqrt(2)/3,        -1/3, 0, 0],
    [          0,           0, 1, 0],
    [          0,           0, 0, 1]])
    >>> simplify(matsimp(Aff3.contains(_)))
    True
    """
    nvec = normalize(fvec)
    fmat = eye3 - nvec*nvec.T*2
    return augment(mat=fmat)

def translation(sh):
    """
    >>> from sympy import *
    >>> from matplus import matsimp
    >>> translation(Mat([2,3,5]))
    Matrix([
    [1, 0, 0, 2],
    [0, 1, 0, 3],
    [0, 0, 1, 5],
    [0, 0, 0, 1]])
    >>> simplify(matsimp(T3.contains(_)))
    True
    """
    return augment(vec=sh)

def scaling(fx, fy, fz):
    """
    >>> from sympy import *
    >>> from matplus import matsimp
    >>> scaling(2,sqrt(2),sqrt(2))
    Matrix([
    [2,       0,       0, 0],
    [0, sqrt(2),       0, 0],
    [0,       0, sqrt(2), 0],
    [0,       0,       0, 1]])
    >>> simplify(matsimp(Aff3.contains(_)))
    True
    """
    return diag(fx, fy, fz, 1, cls=Mat)

def shearing(a, b):
    """
    >>> from sympy import *
    >>> from matplus import matsimp
    >>> shearing(2,sqrt(3))
    Matrix([
    [1, 0,       2, 0],
    [0, 1, sqrt(3), 0],
    [0, 0,       1, 0],
    [0, 0,       0, 1]])
    >>> simplify(matsimp(Aff3.contains(_)))
    True
    """
    mat = eye(4, cls=Matrix)
    mat[0,2] = a
    mat[1,2] = b
    return Mat(mat)

if __name__ == '__main__':
    import doctest
    doctest.testmod()

