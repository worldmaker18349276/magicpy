from sympy.matrices import MatrixExpr
from sympy.matrices.immutable import ImmutableMatrix as Mat
from sympy.functions import sqrt
from sympy.core import Ne, Eq, Dummy
from sympy.logic import And, Or
from magicball.symplus.util import *


def do_indexing(expr):
    from sympy.matrices.expressions.matexpr import MatrixElement
    return expr.replace(MatrixElement, lambda parent, i, j: parent[i,j])

def matsimp(expr):
    """
    >>> from sympy import *
    >>> A = ImmutableMatrix(2, 2, symbols('A(:2)(:2)'))
    >>> B = ImmutableMatrix(2, 2, symbols('B(:2)(:2)'))
    >>> C = ImmutableMatrix(2, 2, symbols('C(:2)(:2)'))
    >>> M = MatrixSymbol('M', 2, 2)
    >>> M[1,1].xreplace({M: B*C})
    Matrix([
    [B00*C00 + B01*C10, B00*C01 + B01*C11],
    [B10*C00 + B11*C10, B10*C01 + B11*C11]])[1, 1]
    >>> matsimp(_)
    B10*C01 + B11*C11
    >>> Eq(Trace(B+C), 0)
    Trace(Matrix([
    [B00 + C00, B01 + C01],
    [B10 + C10, B11 + C11]])) == 0
    >>> matsimp(_)
    B00 + B11 + C00 + C11 == 0
    >>> Eq(A.T-A, ZeroMatrix(2,2))
    Matrix([
    [        0, -A01 + A10],
    [A01 - A10,          0]]) == 0
    >>> matsimp(_)
    And(-A01 + A10 == 0, A01 - A10 == 0)
    """
    from sympy.simplify.simplify import bottom_up

    # do indexing: [.., aij ,..][i,j] -> aij
    expr = do_indexing(expr)
    # deep doit: Trace([.., aij ,..]) -> ..+ aii +..
    expr = bottom_up(expr, lambda e: e.doit())

    def mateq_expand(m1, m2):
        if not is_Matrix(m1) and not is_Matrix(m2):
            return Eq(m1, m2)
        if not is_Matrix(m1) or not is_Matrix(m2):
            return false
        if m1.shape != m2.shape:
            return false
        return And(*[Eq(e1, e2) for e1, e2 in zip(m1, m2)])

    def matne_expand(m1, m2):
        if not is_Matrix(m1) and not is_Matrix(m2):
            return Ne(m1, m2)
        if not is_Matrix(m1) or not is_Matrix(m2):
            return true
        if m1.shape != m2.shape:
            return true
        return Or(*[Ne(e1, e2) for e1, e2 in zip(m1, m2)])

    # expand matrix equation: [.., aij ,..] == [.., bij ,..] -> ..& aij == bij &..
    #                         [.., aij ,..] != [.., bij ,..] -> ..| aij != bij |..
    expr = expr.replace(Eq, mateq_expand)
    expr = expr.replace(Ne, matne_expand)

    return expr

def with_matsym(*simplifies):
    """
    >>> from sympy import *
    >>> A = MatrixSymbol('A', 2, 2)
    >>> Eq(det(A), 0)
    Determinant(A) == 0
    >>> with_matsym(matsimp)(_)
    A[0, 0]*A[1, 1] - A[0, 1]*A[1, 0] == 0
    >>> Eq(A.T*A, Identity(2))
    A'*A == I
    >>> with_matsym(matsimp)(_)
    And(A[0, 0]**2 + A[1, 0]**2 == 1, A[0, 0]*A[0, 1] + \
A[1, 0]*A[1, 1] == 0, A[0, 1]**2 + A[1, 1]**2 == 1)
    """
    def simplify_with_matsym(expr, *args, **kwargs):
        # expand MatrixSymbol as Matrix: A -> [ A[0,0] ,..]
        mats = expr.atoms(MatrixSymbol)
        expr = expr.xreplace(dict((mat, mat.as_explicit()) for mat in mats))

        # replace MatrixElement as Symbol: A[i,j] -> Aij
        elems = tuple(elem for mat in mats for elem in mat)
        syms = tuple(map(lambda e: Dummy(str(e)), elems))
        expr = expr.xreplace(dict(zip(elems, syms)))

        # simplify expression
        for simp in simplifies:
            expr = simp(expr, *args, **kwargs)

        # replace Symbol as MatrixElement: Aij -> A[i,j]
        expr = expr.xreplace(dict(zip(syms, elems)))

        return expr
    return simplify_with_matsym


i, j, k = e = Mat([1,0,0]), Mat([0,1,0]), Mat([0,0,1])
x, y, z = Symbol('x', real=True), Symbol('y', real=True), Symbol('z', real=True)
r = Mat([x, y, z])

def norm(vec):
    return sqrt(sum(v**2 for v in vec))

def normalize(vec):
    return vec/norm(vec)

def dot(vec1, vec2):
    return (vec1.T*vec2)[0]

def cross(vec1, vec2=None):
    if vec2 is None:
        x, y, z = vec1
        return Mat([[ 0,-z, y],
                    [ z, 0,-x],
                    [-y, x, 0]])
    else:
        return cross(vec1)*vec2

