from sympy.matrices import MatrixExpr
from sympy.matrices.immutable import ImmutableMatrix as Mat
from sympy.functions import sqrt
from sympy.core import Ne, Eq, Dummy
from sympy.logic import And, Or
from sympy.simplify import simplify
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

def simplify_with_mat(expr, *args, **kwargs):
    """
    >>> from sympy import *
    >>> A = MatrixSymbol('A', 2, 2)
    >>> Eq(det(A), 0)
    Determinant(A) == 0
    >>> simplify_with_mat(_)
    A[0, 0]*A[1, 1] - A[0, 1]*A[1, 0] == 0
    >>> Eq(A.T*A, Identity(2))
    A'*A == I
    >>> simplify_with_mat(_)
    And(A[0, 0]**2 + A[1, 0]**2 == 1, A[0, 0]*A[0, 1] + \
A[1, 0]*A[1, 1] == 0, A[0, 1]**2 + A[1, 1]**2 == 1)
    """
    # expand MatrixSymbol as Matrix: A -> [ A[0,0] ,..]
    mats = expr.atoms(MatrixSymbol)
    expr = expr.xreplace(dict((mat, mat.as_explicit()) for mat in mats))

    # replace MatrixElement as Symbol: A[i,j] -> Aij
    elems = tuple(elem for mat in mats for elem in mat)
    syms = tuple(map(lambda e: Dummy(str(e)), elems))
    expr = expr.xreplace(dict(zip(elems, syms)))

    # simplify expression
    expr = matsimp(expr)
    expr = simplify(expr, *args, **kwargs)

    # replace Symbol as MatrixElement: Aij -> A[i,j]
    expr = expr.xreplace(dict(zip(syms, elems)))

    return expr


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


class MatrixLambda(MatrixExpr):
    def __new__(cls, variables, expr):
        variables = Tuple(*variables) if is_Tuple(variables) else Tuple(variables)
        for v in variables:
            if not is_Symbol(v):
                raise TypeError('variable is not a Symbol or MatrixSymbol: %s' % v)
        if not is_Matrix(expr):
            raise TypeError('expression is not a Matrix: %s' % expr)

        return MatrixExpr.__new__(cls, variables, expr)

    @property
    def variables(self):
        """The variables used in the internal representation of the function"""
        return self._args[0]

    @property
    def expr(self):
        """The return value of the function"""
        return self._args[1]

    @property
    def free_symbols(self):
        return self.expr.free_symbols - set(self.variables)

    def __call__(self, *args):
        n = len(args)
        if n != len(self.args):
            temp = ('%(name)s takes exactly %(args)s '
                   'argument%(plural)s (%(given)s given)')
            raise TypeError(temp % {
                'name': self,
                'args': len(self.args),
                'plural': 's'*(len(self.args) != 1),
                'given': n})
        return self.expr.xreplace(dict(zip(self.variables, args)))

    def __eq__(self, other):
        if not isinstance(other, MatrixLambda):
            return False
        if len(self.args) != len(other.args):
            return False

        selfexpr = self.args[1]
        otherexpr = other.args[1]
        otherexpr = otherexpr.xreplace(dict(zip(other.args[0], self.args[0])))
        return selfexpr == otherexpr

    def __ne__(self, other):
        return not(self == other)

    def _hashable_content(self):
        return (self.expr.xreplace(self.canonical_variables),)

    @property
    def shape(self):
        return self.expr.shape

    def _eval_conjugate(self):
        from sympy.matrices.expressions.adjoint import Adjoint
        from sympy.matrices.expressions.transpose import Transpose
        return self.func(self.variables, Adjoint(Transpose(self.expr)))

    def _eval_inverse(self):
        from sympy.matrices.expressions.inverse import Inverse
        return self.func(self.variables, Inverse(self.expr))

    def _eval_transpose(self):
        return self.func(self.variables, Transpose(self.expr))

    def _eval_power(self, exp):
        return self.func(self.variables, MatPow(self.expr, exp))

    def _eval_simplify(self, **kwargs):
        return self.func(self.variables, simplify(self.expr))

    def _eval_adjoint(self):
        from sympy.matrices.expressions.adjoint import Adjoint
        return self.func(self.variables, Adjoint(self.expr))

    def _entry(self, i, j):
        return Lambda(self.variables, self.expr[i,j])

