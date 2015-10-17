from sympy.printing.str import StrPrinter
from sympy.core import Atom
from sympy.logic import Not, And, Xor, Or, Implies, Equivalent
from sympy.sets import Complement, Intersection, Union, Contains, Interval
from magicball.symplus.setplus import AbstractSet


class SymplusPrinter(StrPrinter):
    def _print_Not(self, expr):
        if isinstance(expr.args[0], (Atom, Not)):
            return '~'+self._print(expr.args[0])
        else:
            return '~(%s)'%self._print(expr.args[0])

    def _print_And(self, expr):
        argstr = []
        for a in expr.args:
            if isinstance(a, (Atom, Not, And)):
                argstr.append(self._print(a))
            else:
                argstr.append('(%s)'%self._print(a))
        return ' & '.join(sorted(argstr))

    def _print_Xor(self, expr):
        argstr = []
        for a in expr.args:
            if isinstance(a, (Atom, Not, And, Xor)):
                argstr.append(self._print(a))
            else:
                argstr.append('(%s)'%self._print(a))
        return ' ^ '.join(sorted(argstr))

    def _print_Or(self, expr):
        argstr = []
        for a in expr.args:
            if isinstance(a, (Atom, Not, And, Xor, Or)):
                argstr.append(self._print(a))
            else:
                argstr.append('(%s)'%self._print(a))
        return ' | '.join(sorted(argstr))

    def _print_Implies(self, expr):
        if isinstance(expr.args[0], (Atom, Not, And, Xor, Or)):
            argstr0 = self._print(expr.args[0])
        else:
            argstr0 = '(%s)'%self._print(expr.args[0])
        if isinstance(expr.args[1], (Atom, Not, And, Xor, Or, Implies)):
            argstr1 = self._print(expr.args[1])
        else:
            argstr1 = '(%s)'%self._print(expr.args[1])
        return '%s => %s'%(argstr0, argstr1)

    def _print_Equivalent(self, expr):
        argstr = []
        for a in expr.args:
            if isinstance(a, (Atom, Not, And, Xor, Or, Implies, Equivalent)):
                argstr.append(self._print(a))
            else:
                argstr.append('(%s)'%self._print(a))
        return ' == '.join(sorted(argstr))

    def is_AtomSet(self, expr):
        return isinstance(expr, (Interval, AbstractSet))

    def _print_Complement(self, expr):
        if self.is_AtomSet(expr.args[0]) or isinstance(expr.args[0], Complement):
            argstr0 = self._print(expr.args[0])
        else:
            argstr0 = '(%s)'%self._print(expr.args[0])
        if self.is_AtomSet(expr.args[1]):
            argstr1 = self._print(expr.args[1])
        else:
            argstr1 = '(%s)'%self._print(expr.args[1])
        return '%s \ %s'%(argstr0, argstr1)

    def _print_Intersection(self, expr):
        argstr = []
        for a in expr.args:
            if self.is_AtomSet(a) or isinstance(a, (Complement, Intersection)):
                argstr.append(self._print(a))
            else:
                argstr.append('(%s)'%self._print(a))
        return ' n '.join(sorted(argstr))

    def _print_Union(self, expr):
        argstr = []
        for a in expr.args:
            if self.is_AtomSet(a) or isinstance(a, (Complement, Intersection, Union)):
                argstr.append(self._print(a))
            else:
                argstr.append('(%s)'%self._print(a))
        return ' u '.join(sorted(argstr))

    def _print_AbstractSet(self, expr):
        return '{{{0} : {1}}}'.format(*[self._print(arg) for arg in expr.args])

    def _print_ImageSet(self, expr):
        if isinstance(expr.args[1], AbstractSet):
            varstr = self._print(expr.args[0](*expr.args[1].variables))
            exprstr = self._print(expr.args[1].expr)
            return '{%s : %s}'%(varstr, exprstr)
        else:
            if len(expr.args[0].variables) == 1:
                varstr = self._print(expr.args[0].variables[0])
            else:
                varstr = self._print(expr.args[0].variables)
            elemstr = self._print(expr.args[0].expr)
            setstr = self._print(expr.args[1])
            return '{%s : %s in %s}'%(elemstr, varstr, setstr)

    def _print_Contains(self, expr):
        return '%s in %s'%(expr.args[0], expr.args[1])

    def _print_EmptySet(self, expr):
        return '{}'

    def _print_UniversalSet(self, expr):
        return 'V'

    def _print_Lambda(self, obj):
        args = obj.variables
        expr = obj.expr
        if len(args) == 1:
            return '(%s |-> %s)'%(args[0], expr)
        else:
            arg_string = ', '.join(self._print(arg) for arg in args)
            return '(%s |-> %s)'%(arg_string, expr)

    def _print_MatrixBase(self, expr):
        if expr.rows == 0 or expr.cols == 0:
            return '[]'
        elif expr.rows == 1:
            return expr.table(self)
        else:
            return '\n'+expr.table(self)
    _print_SparseMatrix = \
        _print_MutableSparseMatrix = \
        _print_ImmutableSparseMatrix = \
        _print_Matrix = \
        _print_DenseMatrix = \
        _print_MutableDenseMatrix = \
        _print_ImmutableMatrix = \
        _print_ImmutableDenseMatrix = \
        _print_MatrixBase

pr = SymplusPrinter()
def mprint(expr):
    """
    >>> from sympy import *
    >>> x, y, z = symbols('x y z')
    >>> mprint((x&y)|(y&~z))
    x & y | y & ~z
    >>> mprint((x|y)&~(y|z))
    (x | y) & ~(y | z)
    >>> mprint(((x>0) & y) >> z)
    (x > 0) & y => z
    >>> mprint((x>0) & y >> z)
    (x > 0) & (y => z)
    >>> from magicball.symplus.setplus import *
    >>> mprint(St({x : x>y}))
    {x : x > y}
    >>> mprint(St({(x,y) : (x<1)&(y>0)}))
    {(x, y) : (x < 1) & (y > 0)}
    >>> mprint(St({(x,y) : (x<1)&(y>0)}))
    {(x, y) : (x < 1) & (y > 0)}
    >>> mprint(St({x : x<1}, {x : x>0}, evaluate=False) | S.Reals)
    (-oo, oo) u {x : x < 1} n {x : x > 0}
    >>> mprint(St({x : x>0}) | Interval(-1,1))
    [-1, 1] u {x : x > 0}
    >>> mprint(St({x : x<1}) - S.Reals)
    {x : x < 1} \ (-oo, oo)
    >>> mprint(imageset(Lambda(x, x**2), St({x : x>y})))
    {x**2 : x > y}
    >>> mprint(imageset(Lambda(x, x*y), S.Naturals))
    {x*y : x in Naturals()}
    """
    print(pr.doprint(expr))

def mstr(expr):
    return pr.doprint(expr)

