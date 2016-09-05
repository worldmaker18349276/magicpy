from sympy.core import Ne, Eq, Symbol, Lambda, Tuple, pi, Dummy
from sympy.core.compatibility import with_metaclass
from sympy.core.singleton import Singleton
from sympy.simplify import simplify
from sympy.sets import Set, Intersection, Union, Complement, EmptySet, ImageSet
from sympy.sets.sets import UniversalSet
from sympy.matrices import (eye, zeros, diag, det, trace, ShapeError, Matrix,
                            MatrixSymbol, Identity, ZeroMatrix)
from sympy.functions import cos, sin, acos, sign, sqrt
from symplus.typlus import is_Tuple, is_Function
from symplus.symbplus import free_symbols
from symplus.funcplus import Functor, compose, inverse
from symplus.setplus import AbstractSet, Image
from symplus.matplus import Mat, norm, normalize, dot, cross, project, i, j, k, x, y, z, r
from symplus.path import PathMonoid, TransformationPath
from symplus.euclid import (WholeSpace, Halfspace, Sphere, InfiniteCylinder, InfiniteCone,
                            Revolution, Box, Cylinder, Cone)


# algorithm for affine transformation
# ref: https://github.com/matthew-brett/transforms3d

eye3 = eye(3)
zeros3 = Mat([0,0,0])
ones3 = Mat([1,1,1])

def augment(m=eye3, v=zeros3):
    if m.shape != (3,3):
        raise ValueError("shape of matrix m must be (3,3); got %s"%str(m.shape))
    if v.shape != (3,1):
        raise ValueError("shape of matrix v must be (3,1); got %s"%str(v.shape))
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
    tvec = affmat[:-1,-1]
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

def rmat_k2d(d):
    d = normalize(d)
    if d == k:
        rot = eye(3)
    elif d == -k:
        rot = diag(1,-1,-1)
    else:
        rot = rquat2rmat(rquat(acos(dot(k, d)), cross(k, d)))
    return rot


# general transformation

class Transformation(Functor):
    def __new__(cls, variables, expr):
        if not is_Tuple(variables) or len(variables) != 3:
            raise TypeError('variables is not a 3-Tuple: %s'%variables)
        if not is_Tuple(expr) or len(expr) != 3:
            raise TypeError('expr is not a 3-Tuple: %s'%expr)

        return Functor.__new__(cls, variables, expr)

    @property
    def variables(self):
        return self.args[0]

    @property
    def expr(self):
        return self.args[1]

    narg = 3
    nres = 3

    def as_lambda(cls):
        return Lambda(variables, expr)

    def call(self, *args):
        return self.as_lambda()(*args)

    def transform(self, st):
        """
        >>> from sympy import *
        >>> m = translation([2,3,5])
        >>> m.transform((1,2,3))
        (3, 5, 8)
        >>> s = shearing(2*j,sqrt(3)*i)
        >>> m.transform(s)
        AffineTransformation([[1, 0, 0], [2*sqrt(3), 1, 0], [0, 0, 1]], [0, -4*sqrt(3), 0])
        >>> import symplus.setplus
        >>> x, y, z = symbols('x,y,z')
        >>> m.transform(AbstractSet((x,y,z), x**2+y**2+z**2<1))
        Image(EuclideanTransformation(Matrix([
        [2],
        [3],
        [5]]), Matrix([
        [1],
        [0],
        [0],
        [0]]), 1), AbstractSet((x, y, z), x**2 + y**2 + z**2 < 1))
        """
        if is_Tuple(st) and len(st) == 3:
            return self(*st)

        elif is_Function(st):
            return compose(self, st, inverse(self))

        elif isinstance(st, Set):
            return Image(self, st)

        else:
            raise ValueError

    @property
    def free_symbols(self):
        return free_symbols(self.as_lambda())

class AffineTransformation(Transformation):
    def __new__(cls, matrix=eye(3), vector=zeros3):
        matrix = Mat(matrix)
        vector = Mat(vector)
        return Functor.__new__(cls, matrix, vector)

    @property
    def matrix(self):
        return self.args[0]

    @property
    def vector(self):
        return self.args[1]

    def _sympystr(self, printer):
        matrix = list(list(self.matrix[i,j] for j in range(self.matrix.shape[1]))
                                            for i in range(self.matrix.shape[0]))
        return "%s(%s, %s)"%(
            type(self).__name__,
            printer.doprint(matrix),
            printer.doprint(list(self.vector)))

    @classmethod
    def from_augmented_matrix(cls, augmat):
        return cls(augmat[:-1,:-1], augmat[-1,:-1])

    def as_lambda(self):
        pos = Mat([Dummy('x'), Dummy('y'), Dummy('z')])
        res = self.matrix * pos + self.vector
        return Lambda(Tuple(*pos), Tuple(*res))

    def call(self, *args):
        pos = Mat(args)
        res = self.matrix * pos + self.vector
        return Tuple(*res)

    @property
    def free_symbols(cls):
        return free_symbols(cls.matrix) + free_symbols(cls.vector)

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
    def __new__(cls, tvec=zeros3, rquat=Mat([1,0,0,0]), parity=1):
        tvec = Mat(tvec)
        rquat = Mat(rquat)
        parity = sign(parity)
        return Functor.__new__(cls, tvec, rquat, parity)

    @property
    def tvec(self):
        return self.args[0]

    @property
    def rquat(self):
        return self.args[1]

    @property
    def parity(self):
        return self.args[2]

    def _sympystr(self, printer):
        return "%s(%s, %s, %s)"%(
            type(self).__name__,
            printer.doprint(list(self.tvec)),
            printer.doprint(list(self.rquat)),
            printer.doprint(self.parity))

    @property
    def matrix(self):
        return rquat2rmat(self.rquat) * self.parity

    @property
    def vector(self):
        return self.tvec

    def as_lambda(self):
        vec = Mat([Dummy('x'), Dummy('y'), Dummy('z')])
        res = simplify(qrotate(self.rquat, self.parity*vec) + self.tvec)
        return Tuple(*res)

    def call(self, *args):
        vec = Mat(args)
        res = simplify(qrotate(self.rquat, self.parity*vec) + self.tvec)
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

    def _image(self, zet):
        """
        >>> from sympy import *
        >>> t = EuclideanTransformation([0,1,-1], rquat(pi/3, [1,0,1]))
        >>> t._image(WholeSpace())
        WholeSpace()
        >>> t._image(Halfspace(2, [2,1,4]))
        Halfspace(-sqrt(21)/7 - 3*sqrt(14)/28 + 2, [-sqrt(14)/28 + 5*sqrt(21)/42,\
 -sqrt(14)/14 + sqrt(21)/42, sqrt(14)/28 + sqrt(21)/6], False)
        >>> t._image(Sphere(3, [2,0,1]))
        Sphere(3, [7/4, sqrt(6)/4 + 1, 1/4], False)
        >>> t._image(InfiniteCylinder(3, [1,1,0], [0,1,4]))
        InfiniteCylinder(3, [-27*sqrt(6)/136 + 99/136, 27*sqrt(6)/136 + 75/68,\
 -3/8 + 67*sqrt(6)/136], [-sqrt(102)/68 + sqrt(17)/17, -sqrt(102)/17 + sqrt(17)/34,\
 sqrt(102)/68 + 3*sqrt(17)/17], False)
        >>> t._image(InfiniteCone(1, [2,1,0], [2,3,1]))
        InfiniteCone(1, [-sqrt(6)/4 + 3/2, sqrt(6)/2 + 3/2, -1/2 + sqrt(6)/4],\
 [-sqrt(14)/8 + 3*sqrt(21)/28, -3*sqrt(14)/28 - sqrt(21)/28, -3*sqrt(21)/28\
 - 5*sqrt(14)/56], False)
        """
        if isinstance(zet, WholeSpace):
            return zet

        elif isinstance(zet, Halfspace):
            direction = simplify(qrotate(self.rquat, self.parity*zet.direction))
            offset = simplify(zet.offset + dot(self.tvec, direction))
            closed = zet.closed
            return Halfspace(
                offset=offset,
                direction=direction,
                closed=closed,
                normalization=False)

        elif isinstance(zet, Sphere):
            radius = zet.radius
            center = self.call(*zet.center)
            closed = zet.closed
            return Sphere(
                radius=radius,
                center=center,
                closed=closed,
                normalization=False)

        elif isinstance(zet, InfiniteCylinder):
            radius = zet.radius
            direction = simplify(qrotate(self.rquat, self.parity*zet.direction))
            center = simplify(qrotate(self.rquat, self.parity*zet.center))
            center = simplify(center + self.tvec - project(self.tvec, direction))
            closed = zet.closed
            return InfiniteCylinder(
                radius=radius,
                center=center,
                direction=direction,
                closed=closed,
                normalization=False)

        elif isinstance(zet, InfiniteCone):
            slope = zet.slope
            center = self.call(*zet.center)
            direction = simplify(qrotate(self.rquat, self.parity*zet.direction))
            closed = zet.closed
            return InfiniteCone(
                slope=slope,
                center=center,
                direction=direction,
                closed=closed,
                normalization=False)

        elif isinstance(zet, Revolution):
            func = zet.func
            center = self.call(*zet.center)
            direction = simplify(qrotate(self.rquat, self.parity*zet.direction))
            return Revolution(
                func=func,
                center=center,
                direction=direction,
                normalization=False)

        elif isinstance(zet, Box):
            size = zet.size
            center = self.call(*zet.center)
            orientation = simplify(rquat2rmat(self.rquat)*self.parity*zet.orientation)
            closed = zet.closed
            return Box(
                size=size,
                center=center,
                orientation=orientation,
                closed=closed,
                normalization=False)

        elif isinstance(zet, Cylinder):
            radius = zet.radius
            height = zet.height
            center = self.call(*zet.center)
            direction = simplify(qrotate(self.rquat, self.parity*zet.direction))
            closed = zet.closed
            return Cylinder(
                radius=radius,
                height=height,
                center=center,
                direction=direction,
                closed=closed,
                normalization=False)

        elif isinstance(zet, Cone):
            radius = zet.radius
            height = zet.height
            center = self.call(*zet.center)
            direction = simplify(qrotate(self.rquat, self.parity*zet.direction))
            closed = zet.closed
            return Cone(
                radius=radius,
                height=height,
                center=center,
                direction=direction,
                closed=closed,
                normalization=False)

# transformation group

class TransformationGroup(with_metaclass(Singleton, Set)):
    def _contains(self, other):
        return isinstance(other, Transformation)
    def is_subset(self, other):
        return issubclass(type(other), type(self))

class AffineGroup(TransformationGroup):
    def _contains(self, other):
        return isinstance(other, AffineTransformation)

class EuclideanGroup(AffineGroup):
    def _contains(self, other):
        return isinstance(other, EuclideanTransformation)

class SpecialEuclideanGroup(EuclideanGroup):
    def _contains(self, other):
        return (isinstance(other, EuclideanTransformation) and
                other.parity == 1)

class RotationGroup(SpecialEuclideanGroup):
    def _contains(self, other):
        return (isinstance(other, EuclideanTransformation) and
                other.parity == 1 and
                other.tvec == zeros3)

class TranslationGroup(SpecialEuclideanGroup):
    def _contains(self, other):
        return (isinstance(other, EuclideanTransformation) and
                other.parity == 1 and
                other.rquat == Mat([1,0,0,0]))

Trans = TransformationGroup()
Aff4 = AffineGroup()
E3 = EuclideanGroup()
SE3 = SpecialEuclideanGroup()
SO3 = RotationGroup()
T3 = TranslationGroup()

SE3_star = PathMonoid(SE3)
SO3_star = PathMonoid(SO3)
T3_star = PathMonoid(T3)


# useful constructor

def translation(tvec):
    return EuclideanTransformation(tvec=tvec)

def rotation(th, axis):
    return EuclideanTransformation(rquat=rquat(th, axis))

def reflection(fvec):
    t,r,p,z,s = aff2trpzs(augment(m=fvec2fmat(fvec)))
    return EuclideanTransformation(rquat=r, parity=p)

def scaling(zvec):
    return AffineTransformation(matrix=zvec2zmat(zvec))

def shearing(mvec, nvec):
    return AffineTransformation(matrix=mn2smat(mvec, nvec))

t = Symbol('t')

def identity(flen=1):
    return TransformationPath(flen, t, EuclideanTransformation())

def translate(tvec, flen=1):
    return TransformationPath(flen, t, EuclideanTransformation(tvec=tvec*t/flen))

def rotate(th, axis, flen=1):
    return TransformationPath(flen, t, EuclideanTransformation(rquat=rquat(th*t/flen, axis)))
