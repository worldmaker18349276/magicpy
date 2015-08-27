from util import *
from sympy.matrices.expressions.matexpr import MatrixElement, MatrixSymbol, MatrixExpr
from sympy.matrices.immutable import ImmutableMatrix as Mat
from sympy.core.relational import Ne, Eq
from sympy.simplify.simplify import bottom_up
from sympy.logic.boolalg import And, Or


def do_indexing(expr):
    return expr.replace(MatrixElement, lambda parent, i, j: parent[i,j])

def matsimp(expr):
    """
    >>> from sympy import *
    >>> A, B, C = MatrixSymbol('A', 2, 2), MatrixSymbol('B', 2, 2), MatrixSymbol('C', 2, 2)
    >>> Eq(Trace(B+C), 0)
    Trace(B + C) == 0
    >>> matsimp(_)
    B[0, 0] + B[1, 1] + C[0, 0] + C[1, 1] == 0
    >>> A[1,1].xreplace({A: B*C})
    B*C[1, 1]
    >>> matsimp(_)
    B[1, 0]*C[0, 1] + B[1, 1]*C[1, 1]
    >>> Eq(A.T-A, ZeroMatrix(2,2))
    (-1)*A + A' == 0
    >>> matsimp(_)
    And(-A[0, 1] + A[1, 0] == 0, A[0, 1] - A[1, 0] == 0)
    """
    # expand MatrixSymbol as Matrix: A -> [ A[0,0] ,..]
    matsym = filter(lambda s: s.is_Matrix, expr.free_symbols)
    expr = expr.xreplace(dict((mat, mat.as_explicit()) for mat in matsym))

    # do indexing: [.., aij ,..][i,j] -> aij
    expr = do_indexing(expr)
    # deep doit
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


class DummyMatrixSymbol(MatrixSymbol):
    _count = 0
    __slots__ = ['dummy_index']
    is_Dummy = True
    def __new__(cls, name, n, m):
        obj = MatrixSymbol.__new__(cls, name, n, m)
        cls._count += 1
        obj.dummy_index = cls._count
        return obj
    def _hashable_content(self):
        return self.name, self.shape, self.dummy_index


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


if __name__ == '__main__':
    import doctest
    doctest.testmod()

