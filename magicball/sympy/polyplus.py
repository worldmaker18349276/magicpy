from itertools import *
from sympy.core import Pow, Mul, Rel, Eq, Ne, Gt, Lt, Ge, Le
from sympy.assumptions import Q, ask
from sympy.logic import true, false, And, Or, Not
from sympy.polys import factor, LC, Poly


def _is_positive(term):
    return ask(Q.positive(term), And(*map(Q.real, term.free_symbols)))

def _is_negative(term):
    return ask(Q.negative(term), And(*map(Q.real, term.free_symbols)))

def _is_positive_or_zero(term):
    res = _is_positive(term)
    if res in (True, False):
        return res
    t = Poly(term).as_dict()
    if (all(c > 0 for c in t.values()) and
        all(i % 2 == 0 for d in t.keys() for i in d)):
        return True
    else:
        return None

def _is_negative_or_zero(term):
    res = _is_negative(term)
    if res in (True, False):
        return res
    t = Poly(term).as_dict()
    if (all(c < 0 for c in t.values()) and
        all(i % 2 == 0 for d in t.keys() for i in d)):
        return True
    else:
        return None

def polyeqsimp(eq, filling=False):
    """simplify poly equation/inequation and canonicalize it
    >>> from sympy import *
    >>> x, y, z = symbols('x, y, z')
    >>> Eq(x**2+y, 2*y-1)
    x**2 + y == 2*y - 1
    >>> polyeqsimp(_)
    x**2 - y + 1 == 0
    >>> -x**2+x+1 > 0
    -x**2 + x + 1 > 0
    >>> polyeqsimp(_)
    x**2 - x - 1 < 0
    >>> 2*x**2+6*y**2+4 > 0
    2*x**2 + 6*y**2 + 4 > 0
    >>> polyeqsimp(_)
    x**2 + 3*y**2 + 2 > 0
    >>> x**4+3*x**2*y**2 > 0
    x**4 + 3*x**2*y**2 > 0
    >>> polyeqsimp(_)
    x**2 + 3*y**2 > 0
    >>> (x**2+1)*(2*x-y) > 0
    (2*x - y)*(x**2 + 1) > 0
    >>> polyeqsimp(_)
    x - y/2 > 0
    >>> eq = Gt((x**2+y**2)*(2*x-y), 0); eq
    (2*x - y)*(x**2 + y**2) > 0
    >>> polyeqsimp(eq)
    x**3 - x**2*y/2 + x*y**2 - y**3/2 > 0
    >>> polyeqsimp(eq, filling=True)
    x - y/2 > 0
    """
    if not isinstance(eq, Rel):
        raise TypeError
    rel = eq.func
    expr = factor(eq.args[0]-eq.args[1])
    if isinstance(expr, Mul):
        terms = expr.args
    else:
        terms = (expr,)

    # eliminate positive/negative terms
    if not filling:
        terms = tuple(filterfalse(_is_positive, terms))
        sign = len(terms)
        terms = tuple(filterfalse(_is_negative, terms))
        sign -= len(terms)
    else:
        terms = tuple(filterfalse(_is_positive_or_zero, terms))
        sign = len(terms)
        terms = tuple(filterfalse(_is_negative_or_zero, terms))
        sign -= len(terms)

    # reduce power terms
    terms0 = filterfalse(lambda t: isinstance(t, Pow), terms)
    termspow = filter(lambda t: isinstance(t, Pow), terms)
    terms1 = filter(lambda t: t.args[1]%2==1, termspow)
    terms1 = map(lambda t: t.args[0], terms1)
    if not filling:
        terms2 = filter(lambda t: t.args[1]%2==0, termspow)
        terms2 = map(lambda t: Pow(t.args[0], 2), terms2)
    else:
        terms2 = ()
    expr = Mul(*tuple(chain(terms0, terms1, terms2)))

    # normalize leading coeff
    expr = expr.expand()
    lc = LC(expr)
    if lc < 0:
        sign += 1
    expr = expr/lc

    # swap relation
    if sign % 2 == 1:
        swap = {Eq: Eq, Ne: Ne,
                Lt: Gt, Le: Ge,
                Gt: Lt, Ge: Le}
        rel = swap[rel]

    return rel(expr, 0)

def _find_relations(expr):
    from sympy.logic import BooleanFunction
    if isinstance(expr, BooleanFunction):
        return set.union(*(_find_relations(i) for i in expr.args))
    elif isinstance(expr, Rel):
        return set([expr])
    else:
        return set()

def onesiderelsimp(expr, filling=False):
    """logic simplify for one side relation Rel(w, 0)
    >>> from sympy import *
    >>> x, y, z = symbols('x, y, z')
    """
    from sympy.core.evaluate import evaluate
    from sympy.core.symbols import Wild
    from sympy.logic import to_nnf, simplify_logic

    # to nnf
    w = Wild('w')
    expr = to_nnf(expr)
    expr = expr.replace(Not(w), ~w)

    # standardize relation
    with evaluate(False):
        if not filling:
            expr = expr.replace(Ne(w,0), Not(Eq(w,0)))
            expr = expr.replace(w>=0, Or(w>0, Eq(w,0)))
            expr = expr.replace(w<=0, Or(w<0, Eq(w,0)))
            relations = _find_relations(expr)
            assumptions = []
            for a in set(rel.args[0] for rel in relations):
                assumptions.append(SOPform((a>0, Eq(a,0), a<0), [[1,0,0],[0,1,0],[0,0,1]]))
            expr = And(*assumptions) & expr
        else:
            expr = expr.replace(Eq(w,0), false)
            expr = expr.replace(Ne(w,0), true)
            expr = expr.replace(w>=0, w>0)
            expr = expr.replace(w<=0, Not(w>0))
            expr = expr.replace(w<0,  Not(w>0))

    return simplify_logic(expr)


if __name__ == '__main__':
    import doctest
    doctest.testmod()

