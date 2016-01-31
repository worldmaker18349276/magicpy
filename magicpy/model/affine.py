from sympy.core import Ne, Eq, Symbol, Lambda, Tuple, pi, Dummy
from sympy.sets import Set, Intersection, Union, Complement, EmptySet, ImageSet
from sympy.sets.sets import UniversalSet
from sympy.matrices import (eye, zeros, diag, det, trace, ShapeError, Matrix,
                            MatrixSymbol, Identity, ZeroMatrix)
from sympy.matrices.immutable import ImmutableMatrix as Mat
from sympy.functions import cos, sin, acos, sign
from symplus.util import *
from symplus.setplus import AbstractSet
from symplus.funcplus import VariableFunctionClass, compose, inverse, Image
from symplus.matplus import *
from magicpy.model.path import Path


eye3 = eye(3)
zeros3 = ZeroMatrix(3,1)
ones3 = Mat([1,1,1])


# ref: https://github.com/matthew-brett/transforms3d

def augment(m=eye3, v=zeros3):
    return m.row_join(v).col_join(eye(4)[-1,:])

def rquat(th, axis):
    axis = Mat(axis)
    return Mat([cos(th/2)]).col_join(sin(th/2)*normalize(axis))

def qmult(q1, q2):
    """
    >>> from sympy import *
    >>> q1 = rquat(pi/2, i)
    >>> q2 = rquat(pi/3, j)
    >>> rquat2rmat(q1) * rquat2rmat(q2)
    Matrix([
    [      1/2, 0, sqrt(3)/2],
    [sqrt(3)/2, 0,      -1/2],
    [        0, 1,         0]])
    >>> rquat2rmat(qmult(q1, q2))
    Matrix([
    [      1/2, 0, sqrt(3)/2],
    [sqrt(3)/2, 0,      -1/2],
    [        0, 1,         0]])
    """
    w1 = q1[0]
    xyz1 = Mat(q1[1:])
    w2 = q2[0]
    xyz2 = Mat(q2[1:])
    w = w1*w2 - dot(xyz1, xyz2)
    xyz = w1*xyz2 + w2*xyz1 + cross(xyz1, xyz2)
    return Mat([w] + xyz[:])

def qinv(q):
    """
    >>> from sympy import *
    >>> q = rquat(pi/3, j)
    >>> rquat2rmat(q).inv()
    Matrix([
    [      1/2, 0, -sqrt(3)/2],
    [        0, 1,          0],
    [sqrt(3)/2, 0,        1/2]])
    >>> rquat2rmat(qinv(q))
    Matrix([
    [      1/2, 0, -sqrt(3)/2],
    [        0, 1,          0],
    [sqrt(3)/2, 0,        1/2]])
    """
    return Mat([q[0], -q[1], -q[2], -q[3]]) # assume norm(q) == 1

def qrotate(q, v):
    """
    >>> from sympy import *
    >>> q = rquat(pi/3, j)
    >>> v = Mat([1,sqrt(2),3])
    >>> simplify(qrotate(q, v))
    Matrix([
    [1/2 + 3*sqrt(3)/2],
    [          sqrt(2)],
    [ -sqrt(3)/2 + 3/2]])
    >>> rquat2rmat(q)*v
    Matrix([
    [1/2 + 3*sqrt(3)/2],
    [          sqrt(2)],
    [ -sqrt(3)/2 + 3/2]])
    """
    v = Mat([0, v[0], v[1], v[2]])
    v_ = qmult(q, qmult(v, qinv(q)))
    return Mat(v_[1:])

def rquat2rmat(rquat):
    """
    >>> from sympy import *
    >>> t = Symbol('t', positive=True)
    >>> simplify(rquat2rmat(rquat(pi/3, i+j)))
    Matrix([
    [       3/4,       1/4,  sqrt(6)/4],
    [       1/4,       3/4, -sqrt(6)/4],
    [-sqrt(6)/4, sqrt(6)/4,        1/2]])
    >>> simplify(rquat2rmat(rquat(t, i)))
    Matrix([
    [1,      0,       0],
    [0, cos(t), -sin(t)],
    [0, sin(t),  cos(t)]])
    >>> simplify(rquat2rmat(rquat(t, i+k)))
    Matrix([
    [     cos(t/2)**2, -sqrt(2)*sin(t)/2,       sin(t/2)**2],
    [sqrt(2)*sin(t)/2,            cos(t), -sqrt(2)*sin(t)/2],
    [     sin(t/2)**2,  sqrt(2)*sin(t)/2,       cos(t/2)**2]])
    """
    w = rquat[0]
    xyz = Mat(rquat[1:])
    return (1-2*norm(xyz)**2)*eye3 + 2*xyz*xyz.T + 2*w*cross(xyz)

def rmat2rquat(rmat):
    """
    >>> from sympy import *
    >>> t = Symbol('t', positive=True)
    >>> list(rquat(pi/3, i+j))
    [sqrt(3)/2, sqrt(2)/4, sqrt(2)/4, 0]
    >>> list(simplify(rmat2rquat(rquat2rmat(rquat(pi/3, i+j)))))
    [sqrt(3)/2, sqrt(2)/4, sqrt(2)/4, 0]
    >>> list(rquat(t, i))
    [cos(t/2), sin(t/2), 0, 0]
    >>> list(simplify(rmat2rquat(rquat2rmat(rquat(t, i)))))
    [Abs(cos(t/2)), sin(t)/(2*Abs(cos(t/2))), 0, 0]
    >>> list(rquat(t, i+k))
    [cos(t/2), sqrt(2)*sin(t/2)/2, 0, sqrt(2)*sin(t/2)/2]
    >>> list(simplify(rmat2rquat(rquat2rmat(rquat(t, i+k)))))
    [Abs(cos(t/2)), sqrt(2)*sin(t)/(4*Abs(cos(t/2))), 0, sqrt(2)*sin(t)/(4*Abs(cos(t/2)))]
    """
    w = sqrt(1+trace(rmat))/2
    if w != 0:
        x = (rmat[2,1]-rmat[1,2])/(4*w)
        y = (rmat[0,2]-rmat[2,0])/(4*w)
        z = (rmat[1,0]-rmat[0,1])/(4*w)
        return Mat([w,x,y,z])
    else:
        x = sqrt(1+rmat[0,0]-rmat[1,1]-rmat[2,2])/2
        y = (rmat[0,1]+rmat[1,0])/(4*x)
        z = (rmat[0,2]+rmat[2,0])/(4*x)
        w = (rmat[2,1]-rmat[1,2])/(4*x)
        return Mat([w,x,y,z])

def zfac2zmat(zfac):
    """
    >>> from sympy import *
    >>> zfac2zmat([5,2,sqrt(3)])
    Matrix([
    [5, 0,       0],
    [0, 2,       0],
    [0, 0, sqrt(3)]])
    """
    return Mat(diag(*zfac))

def zmat2zfac(zmat):
    """
    >>> from sympy import *
    >>> list(zmat2zfac(zfac2zmat([5,2,sqrt(3)])))
    [5, 2, sqrt(3)]
    """
    return Mat([zmat[0,0], zmat[1,1], zmat[2,2]])

def stri2smat(stri):
    """
    >>> from sympy import *
    >>> stri2smat([5,2,sqrt(3)])
    Matrix([
    [1, 5,       2],
    [0, 1, sqrt(3)],
    [0, 0,       1]])
    """
    return Mat([[1, stri[0], stri[1]],
                [0, 1      , stri[2]],
                [0, 0      , 1      ]])

def smat2stri(smat):
    """
    >>> from sympy import *
    >>> list(smat2stri(stri2smat([5,2,sqrt(3)])))
    [5, 2, sqrt(3)]
    """
    return Mat([smat[0,1], smat[0,2], smat[1,2]])

def trpzs2aff(tvec=zeros3, rquat=Mat([1,0,0,0]), parity=1, zfac=ones3, stri=zeros3):
    mat = rquat2rmat(rquat) * sign(parity) * zfac2zmat(zfac) * stri2smat(stri)
    return augment(mat, tvec)

def aff2trpzs(affmat):
    tvec = affmat[-1,:-1]
    rpzsmat = affmat[:-1,:-1]
    zsmat = (rpzsmat.T*rpzsmat).cholesky().T
    zfac = Mat([zsmat[0,0], zsmat[1,1], zsmat[2,2]])
    zmat = zfac2zmat(zfac)
    smat = zmat.inv() * zsmat
    stri = smat2stri(smat)
    rpmat = rpzsmat * zsmat.inv()
    parity = det(rpmat)
    rquat = rmat2rquat(rpmat*parity)
    return tvec, rquat, parity, zfac, stri


def fvec2fmat(fvec):
    """
    >>> from sympy import *
    >>> fvec2fmat(i)
    Matrix([
    [-1, 0, 0],
    [ 0, 1, 0],
    [ 0, 0, 1]])
    >>> fvec2fmat(i-sqrt(2)*j)
    Matrix([
    [        1/3, 2*sqrt(2)/3, 0],
    [2*sqrt(2)/3,        -1/3, 0],
    [          0,           0, 1]])
    >>> t,r,p,z,s = aff2trpzs(augment(m=_))
    >>> list(r)
    [0, sqrt(3)/3, -sqrt(6)/3, 0]
    >>> p
    -1
    """
    fvec = normalize(Mat(fvec))
    return eye3 - fvec*fvec.T*2

def mn2smat(mvec, nvec):
    """
    >>> from sympy import *
    >>> mn2smat(i,j)
    Matrix([
    [1, 1, 0],
    [0, 1, 0],
    [0, 0, 1]])
    >>> mn2smat(i-j+2*k,2*j+k)
    Matrix([
    [1,  2,  1],
    [0, -1, -1],
    [0,  4,  3]])
    >>> t,r,p,z,s = aff2trpzs(augment(m=_))
    >>> list(simplify(r))
    [sqrt(-34*sqrt(17) + 578)/34, 2*sqrt(2)/sqrt(-sqrt(17) + 17), 0, 0]
    >>> list(simplify(z))
    [1, sqrt(17), sqrt(17)/17]
    >>> list(simplify(s))
    [2, 1, 13/17]
    """
    mvec = Mat(mvec)
    nvec = Mat(nvec)
    mvec = mvec - dot(mvec, normalize(nvec)) * normalize(nvec)
    return eye3 + mvec*nvec.T

def zvec2zmat(zvec):
    """
    >>> from sympy import *
    >>> zvec2zmat(j*3)
    Matrix([
    [1, 0, 0],
    [0, 3, 0],
    [0, 0, 1]])
    >>> zvec2zmat(i-j)
    Matrix([
    [ 1/2 + sqrt(2)/2, -sqrt(2)/2 + 1/2, 0],
    [-sqrt(2)/2 + 1/2,  1/2 + sqrt(2)/2, 0],
    [               0,                0, 1]])
    >>> t,r,p,z,s = aff2trpzs(augment(m=_))
    >>> list(simplify(r))
    [2**(1/4)*3**(3/4)*sqrt(1 + sqrt(2) + sqrt(6))/6, 0, 0, (-6**(3/4) + 54**(1/4))/(6*sqrt(1 + sqrt(2) + sqrt(6)))]
    >>> list(simplify(z))
    [sqrt(6)/2, 2*sqrt(3)/3, 1]
    >>> list(simplify(s))
    [-1/3, 0, 0]
    """
    zvec = Mat(zvec)
    nvec = normalize(zvec)
    zfac = norm(zvec)
    return eye3 + nvec*nvec.T*(zfac-1)


class Transformation(VariableFunctionClass):
    def __new__(mcl, variables, expr):
        if not is_Tuple(variables) or len(variables) != 3:
            raise TypeError('variables is not a 3-Tuple: %s'%variables)
        if not is_Tuple(expr) or len(expr) != 3:
            raise TypeError('expr is not a 3-Tuple: %s'%expr)

        name = '(%s |-> %s)' % (variables, expr)
        fields = {}
        fields['lambda_form'] = Lambda(variables, expr)
        return VariableFunctionClass.__new__(mcl, name, 3, 3, fields)

    @classmethod
    def from_lambda(mcl, func):
        return mcl(func.variables, func.expr)

    def as_lambda(cls):
        return cls.lambda_form

    def call(cls, *args):
        return cls.as_lambda()(*args)

    @property
    def func_free_symbols(cls):
        return cls.as_lambda().free_symbols

class AffineTransformation(Transformation):
    def __new__(mcl, matrix=eye(4), vector=zeros3):
        vector = Mat(vector)
        name = 'Aff(%s, %s)' % (matrix, list(vector))
        fields = {}
        fields['matrix'] = matrix
        fields['vector'] = vector
        return VariableFunctionClass.__new__(mcl, name, 3, 3, fields)

    def from_augmented_matrix(cls, augmat):
        return cls(augmat[:-1,:-1], augmat[-1,:-1])

    def as_lambda(cls):
        pos = Mat([Dummy('x'), Dummy('y'), Dummy('z')])
        res = cls.matrix * pos + cls.vector
        return Lambda(Tuple(*pos), Tuple(*res))

    def call(cls, *args):
        pos = Mat(args)
        res = cls.matrix * pos + cls.vector
        return Tuple(*res)

    @property
    def func_free_symbols(cls):
        return cls.matrix.free_symbols + cls.vector.free_symbols

    def _compose(trans1, trans2):
        if isinstance(trans2, AffineTransformation):
            matrix = trans1.matrix * trans2.matrix
            vector = trans1.matrix * trans2.vector + trans1.vector
            return AffineTransformation(matrix, vector)

    def _inv(trans):
        matrix = trans.matrix.inv()
        vector = -trans.matrix.inv() * trans.vector
        return AffineTransformation(matrix, vector)

class EuclideanTransformation(AffineTransformation):
    def __new__(mcl, tvec=zeros3, rquat=Mat([1,0,0,0]), parity=1):
        tvec = Mat(tvec)
        rquat = Mat(rquat)
        parity = sign(parity)
        name = 'E(%s, %s, %s)' % (list(tvec), list(rquat), parity)
        fields = {}
        fields['tvec'] = tvec
        fields['rquat'] = rquat
        fields['parity'] = parity
        return VariableFunctionClass.__new__(mcl, name, 3, 3, fields)

    def as_lambda(cls):
        return Lambda((x,y,z), cls(x,y,z))

    @property
    def matrix(cls):
        return rquat2rmat(cls.rquat) * cls.parity

    @property
    def vector(cls):
        return cls.tvec

    def call(cls, *args):
        vec = Mat(args)
        res = simplify(qrotate(cls.rquat, cls.parity*vec) + cls.tvec)
        return Tuple(*res)

    def _compose(trans1, trans2):
        if isinstance(trans2, EuclideanTransformation):
            tvec = trans1(trans2.tvec)
            rquat = qmult(trans1.rquat, trans2.rquat)
            parity = trans1.parity * trans2.parity
            return EuclideanTransformation(tvec, rquat, parity)

        elif isinstance(trans2, AffineTransformation):
            matrix = trans1.matrix * trans2.matrix
            vector = trans1.matrix * trans2.vector + trans1.vector
            return AffineTransformation(matrix, vector)

    def _inv(trans):
        tvec = qrotate(qinv(trans.rquat), -trans.parity*trans.tvec)
        rquat = qinv(trans.rquat)
        parity = trans.parity
        return EuclideanTransformation(tvec, rquat, parity)

def translation(tvec):
    return EuclideanTransformation(tvec=tvec)

def rotation(th, axis):
    return EuclideanTransformation(rquat=rquat(th, axis))

def reflection(fvec):
    t,r,p,z,s = aff2trpzs(augment(m=fvec2fmat(fvec)))
    return EuclideanTransformation(rquat=r, parity=p)

def shearing(mvec, nvec):
    return AffineTransformation(matrix=mn2smat(mvec, nvec))

def scaling(zvec):
    return AffineTransformation(matrix=zvec2zmat(zvec))


def transform(trans, st):
    """
    >>> from sympy import *
    >>> m = translation([2,3,5])
    >>> transform(m, (1,2,3))
    (3, 5, 8)
    >>> s = shearing(2*j,sqrt(3)*i)
    >>> transform(m, s)
    Aff(Matrix([
    [        1, 0, 0],
    [2*sqrt(3), 1, 0],
    [        0, 0, 1]]), [0, -4*sqrt(3), 0])
    >>> import symplus.setplus
    >>> x, y, z = symbols('x,y,z')
    >>> transform(m, AbstractSet((x,y,z), x**2+y**2+z**2<1))
    Image(E([2, 3, 5], [1, 0, 0, 0], 1), AbstractSet((x, y, z), x**2 + y**2 + z**2 < 1))
    """
    if is_Tuple(st) and len(st) == 3:
        return trans(*st)

    elif is_Function(st):
        return compose(trans, st, inverse(trans))

    elif isinstance(st, Set):
        return Image(trans, st)

    else:
        raise ValueError
