from sympy.matrices.expressions.matexpr import MatrixElement, MatrixSymbol
from sympy.matrices.ImmutableMatrix import ImmutableMatrix as Mat
from sympy.logic.boolalg import And, Or


def matsimp(expr):
    """
    >>> from sympy import *
    >>> A, B, C = MatrixSymbol('A', 2, 2), MatrixSymbol('B', 2, 2), MatrixSymbol('C', 2, 2)
    >>> A[1,1].xreplace({A: B*C})
    B*C[1, 1]
    >>> matsimp(_)
    B[1, 0]*C[0, 1] + B[1, 1]*C[1, 1]
    >>> Eq(Trace(A), 0).xreplace({A: B+C})
    Trace(B+C)
    >>> matsimp(_)
    B[1, 0]*C[0, 1] + B[1, 1]*C[1, 1]
    """
    # expand MatrixSymbol as Matrix: A -> [ A[0,0] ,..]
    matsym = filter(lambda s: s.is_Matrix, expr.free_symbols)
    expr = expr.xreplace((mat, Mat(mat)) for mat in matsym)

    # evaluate indexing: [.., aij ,..][i,j] -> aij
    expr = expr.replace(MatrixElement, lambda parent, i, j: parent[i,j])
    expr = expr.doit(deep=True)

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


if __name__ == '__main__':
    import doctest
    doctest.testmod()

