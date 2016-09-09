from sympy.printing.str import StrPrinter
from sympy.printing.precedence import precedence
from sympy.interactive.printing import init_printing
from sympy.core import Atom, Basic
from sympy.logic import Not, And, Xor, Or, Implies, Equivalent
from sympy.sets import Complement, Intersection, Union, Contains, Interval


class MathPrinter(StrPrinter):
    printmethod = "_mathstr"

    def emptyPrinter(self, expr):
        if isinstance(expr, str):
            return expr
        elif isinstance(expr, Basic):
            if hasattr(expr, "_sympystr"):
                return expr._sympystr()
            else:
                return repr(expr)
        else:
            return str(expr)

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
        return ' /\ '.join(sorted(argstr))

    def _print_Xor(self, expr):
        argstr = []
        for a in expr.args:
            if isinstance(a, (Atom, Not, And, Xor)):
                argstr.append(self._print(a))
            else:
                argstr.append('(%s)'%self._print(a))
        return ' (+) '.join(sorted(argstr))

    def _print_Or(self, expr):
        argstr = []
        for a in expr.args:
            if isinstance(a, (Atom, Not, And, Xor, Or)):
                argstr.append(self._print(a))
            else:
                argstr.append('(%s)'%self._print(a))
        return ' \/ '.join(sorted(argstr))

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
        return ' <=> '.join(sorted(argstr))

    def is_ComposedSet(self, expr):
        return isinstance(expr, (Complement, Intersection, Union))

    def _print_Complement(self, expr):
        if not self.is_ComposedSet(expr.args[0]) or isinstance(expr.args[0], Complement):
            argstr0 = self._print(expr.args[0])
        else:
            argstr0 = '(%s)'%self._print(expr.args[0])
        if not self.is_ComposedSet(expr.args[1]):
            argstr1 = self._print(expr.args[1])
        else:
            argstr1 = '(%s)'%self._print(expr.args[1])
        return '%s \ %s'%(argstr0, argstr1)

    def _print_Intersection(self, expr):
        argstr = []
        for a in expr.args:
            if not self.is_ComposedSet(a) or isinstance(a, (Complement, Intersection)):
                argstr.append(self._print(a))
            else:
                argstr.append('(%s)'%self._print(a))
        return ' n '.join(sorted(argstr))

    def _print_Union(self, expr):
        argstr = []
        for a in expr.args:
            if not self.is_ComposedSet(a) or isinstance(a, (Complement, Intersection, Union)):
                argstr.append(self._print(a))
            else:
                argstr.append('(%s)'%self._print(a))
        return ' u '.join(sorted(argstr))

    def _print_Contains(self, expr):
        return '%s in %s'%(expr.args[0], expr.args[1])

    def _print_EmptySet(self, expr):
        return '(/)'

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

    def _print_Piecewise(self, expr):
        return "({0})".format("; ".join(
            "{0} if {1}".format(self._print(val), self._print(cond))
            for val, cond in expr.args))

    def _print_MatrixBase(self, expr):
        from sympy import eye
        if expr.rows == 0 or expr.cols == 0:
            return '[]'
        elif expr.rows == 1:
            return expr.table(self, colsep=' ')
        elif expr.cols == 1:
            return expr.T.table(self, colsep=' ')+'\''
        elif expr.rows == expr.cols and expr == eye(expr.cols):
            return 'eye(%s)'%expr.cols
        else:
            return '\n'+expr.table(self, colsep=' ')
    _print_SparseMatrix = \
        _print_MutableSparseMatrix = \
        _print_ImmutableSparseMatrix = \
        _print_Matrix = \
        _print_DenseMatrix = \
        _print_MutableDenseMatrix = \
        _print_ImmutableMatrix = \
        _print_ImmutableDenseMatrix = \
        _print_MatrixBase

    def _print_Equality(self, expr):
        return ' == '.join(sorted(map(self._print, expr.args)))

    def _print_Unequality(self, expr):
        return ' =/= '.join(sorted(map(self._print, expr.args)))

    def _print_LessThan(self, expr):
        return '{0} =< {1}'.format(
            self.parenthesize(expr.lhs, precedence(expr)),
            self.parenthesize(expr.rhs, precedence(expr)))

    def _print_Abs(self, expr):
        return '|{0}|'.format(self._print(expr.args[0]))

    def _print_Determinant(self, expr):
        return '||{0}||'.format(self._print(expr.args[0]))

pr = MathPrinter()
def mprint(expr):
    """
    >>> from sympy import *
    >>> x, y, z = symbols('x y z')
    >>> mprint((x&y)|(y&~z))
    x /\ y \/ y /\ ~z
    >>> mprint((x|y)&~(y|z))
    (x \/ y) /\ ~(y \/ z)
    >>> mprint(((x>0) & y) >> z)
    (x > 0) /\ y => z
    >>> mprint((x>0) & y >> z)
    (x > 0) /\ (y => z)
    >>> from symplus.setplus import *
    >>> mprint(St({x : x>y}))
    {x | x > y}
    >>> mprint(St({(x,y) : (x<1)&(y>0)}))
    {(x, y) | (x < 1) /\ (y > 0)}
    >>> mprint(St({(x,y) : (x<1)&(y>0)}))
    {(x, y) | (x < 1) /\ (y > 0)}
    >>> mprint(St({x : x<1}, {x : x>0}, evaluate=False) | S.Reals)
    (-oo, oo) u {x | x < 1} n {x | x > 0}
    >>> mprint(St({x : x>0}) | Interval(-1,1))
    [-1, 1] u {x | x > 0}
    >>> mprint(St({x : x<1}) - S.Reals)
    {x | x < 1} \ (-oo, oo)
    >>> mprint(Image(Lambda(x, x**2), St({x : x>y}), evaluate=False))
    {x**2 | x > y}
    >>> mprint(Image(Lambda(x, x*y), S.Naturals))
    {x*y | x in Naturals()}
    >>> from symplus.funcplus import *
    >>> mprint(FunctionCompose(exp, sin))
    (exp o sin)
    >>> mprint(Image(FunctionCompose(exp, sin), St({x : x>y}), evaluate=False))
    {exp(sin(x)) | x > y}
    >>> mprint(Apply(Lambda(x, x*y), 3))
    (x |-> x*y)(3)
    """
    print(pr.doprint(expr))

def mstr(expr):
    return pr.doprint(expr)

def init_mprinting():
    init_printing(pretty_print=False, str_printer=mstr)

