from itertools import *
from sympy.core import S, Symbol, Dummy
from sympy.logic import true, false, And, Or, Not
from sympy.logic.boolalg import BooleanFunction
from sympy.simplify import simplify

from symplus.typlus import is_Matrix


# sqrt
# Ref: http://mathforum.org/library/drmath/view/65302.html

def sqrtsimp(expr):
    """
    >>> from sympy import *
    >>> from symplus.strplus import init_mprinting
    >>> init_mprinting()
    >>> expand((2+sqrt(3))**2)
    4*sqrt(3) + 7
    >>> sqrtsimp(sqrt(_))
    sqrt(3) + 2
    >>> expand((6+sqrt(17))**(-2))
    1/(12*sqrt(17) + 53)
    >>> sqrtsimp(sqrt(_))
    1/(sqrt(17) + 6)
    """
    from sympy.functions import sqrt, sign
    from sympy.core import Wild

    def sqrtofsqrtsimp(a=0, b=0, c=0): # sqrt(a + b*sqrt(c))
        q = sqrt(a**2 - b**2*c)
        if not q.is_Rational:
            return None
        return sqrt((a+q)/2) + sign(b)*sqrt((a-q)/2)

    def sqrtofsqrtsimp_(a=0, b=0, c=0): # 1/sqrt(a + b*sqrt(c))
        q = sqrt(a**2 - b**2*c)
        if not q.is_Rational:
            return None
        return 1/(sqrt((a+q)/2) + sign(b)*sqrt((a-q)/2))

    a, b, c = Wild('a'), Wild('b'), Wild('c')
    expr = expr.replace(sqrt(a + b*sqrt(c)), sqrtofsqrtsimp, exact=True)
    expr = expr.replace(1/sqrt(a + b*sqrt(c)), sqrtofsqrtsimp_, exact=True)
    return expr

def with_sqrtsimp(*simplifies):
    def simplify_with_sqrtsimp(expr, *args, **kwargs):
        while True:
            for simp in simplifies:
                expr = simp(expr, *args, **kwargs)
            expr_ = sqrtsimp(expr)
            if expr_ == expr:
                return expr
            expr = expr_

    return simplify_with_sqrtsimp


# relational
from sympy.assumptions import Q, ask
from sympy.core import Pow, Mul, Rel, Eq, Ne, Gt, Lt, Ge, Le
from sympy.polys import factor, LC, Poly, PolynomialError

def ask_is_positive(term):
    return ask(Q.positive(term), And(*map(Q.real, term.free_symbols)))

def ask_is_negative(term):
    return ask(Q.negative(term), And(*map(Q.real, term.free_symbols)))

def _is_positive(term):
    if getattr(term, 'is_number', False):
        return term > 0
    elif isinstance(term, Pow):
        if term.args[1]%2==1:
            return _is_positive(term.args[0])
        else:
            return _is_positive(term.args[0]) or _is_negative(term.args[0])

    l = len(term.free_symbols)
    t = Poly(term).as_dict()
    if (all(c > 0 for c in t.values()) and
        all(i % 2 == 0 for d in t.keys() for i in d) and
        (0,)*l in t.keys()):
        return True
    return ask_is_positive(term)

def _is_negative(term):
    if getattr(term, 'is_number', False):
        return term < 0
    elif isinstance(term, Pow):
        if term.args[1]%2==1:
            return _is_negative(term.args[0])
        else:
            return False

    l = len(term.free_symbols)
    t = Poly(term).as_dict()
    if (all(c < 0 for c in t.values()) and
        all(i % 2 == 0 for d in t.keys() for i in d) and
        (0,)*l in t.keys()):
        return True
    return ask_is_negative(term)

def _is_positive_or_zero(term):
    if getattr(term, 'is_number', False):
        return term >= 0
    elif isinstance(term, Pow):
        if term.args[1]%2==1:
            return _is_positive_or_zero(term.args[0])
        else:
            return True

    t = Poly(term).as_dict()
    if (all(c > 0 for c in t.values()) and
        all(i % 2 == 0 for d in t.keys() for i in d)):
        return True
    return ask_is_positive(term)

def _is_negative_or_zero(term):
    if getattr(term, 'is_number', False):
        return term <= 0
    elif isinstance(term, Pow):
        if term.args[1]%2==1:
            return _is_negative_or_zero(term.args[0])

    t = Poly(term).as_dict()
    if (all(c < 0 for c in t.values()) and
        all(i % 2 == 0 for d in t.keys() for i in d)):
        return True
    return ask_is_negative(term)


def is_polynomial(expr):
    try:
        Poly(expr, expr.free_symbols)
    except PolynomialError:
        return False
    else:
        return True

def is_simplerel(expr):
    from sympy.logic.boolalg import _find_predicates

    variables = _find_predicates(expr)
    relations = tuple(v for v in variables if isinstance(v, Rel))
    if any(rel.args[1] != 0 for rel in relations):
        return False
    simple_form = {Eq: Eq, Ne: Eq,
                   Gt: Gt, Le: Gt,
                   Lt: Lt, Ge: Lt}
    return all(len(set(simple_form[rel.func] for rel in rels)) == 1
               for _, rels in groupby(relations, lambda r: r.args[0]))


def expand_polyeq(eq):
    if not isinstance(eq, Rel):
        return eq
    rel = eq.func
    expr = factor(eq.args[0]-eq.args[1])
    if expr.is_number:
        return rel(expr, 0, evaluate=True)
    elif isinstance(expr, Mul):
        terms = expr.args
    else:
        terms = (expr,)

    # eliminate positive/negative terms
    terms = tuple(t for t in terms if not _is_positive(t))
    sign = len(terms)
    terms = tuple(t for t in terms if not _is_negative(t))
    sign -= len(terms)

    # reduce power terms
    terms1 = (t for t in terms if not isinstance(t, Pow))
    termspow = tuple(t for t in terms if isinstance(t, Pow))
    terms2 = (t.args[0] for t in termspow if t.args[1]%2==0)
    terms3 = (t.args[0] for t in termspow if t.args[1]%2==1)

    # find positive-or-zero terms
    termsp_ = list(terms2)
    termsn = []
    for term in chain(terms1, terms3):
        if _is_positive_or_zero(term):
            termsp_.append(term)
        elif _is_negative_or_zero(term):
            termsp_.append(-term)
            sign += 1
        else:
            termsn.append(term)

    # reduce polynomial positive-or-zero terms
    termsp = []
    for term in termsp_:
        if is_polynomial(term):
            termsp.extend(term.free_symbols)
        else:
            termsp.append(term)

    # normalize leading coeff
    for i in range(len(termsn)):
        lc = LC(termsn[i], sorted(termsn[i].free_symbols, key=lambda x: x.name))
        if lc < 0:
            sign += 1
        termsn[i] = termsn[i]/lc
    for i in range(len(termsp)):
        lc = LC(termsp[i], sorted(termsp[i].free_symbols, key=lambda x: x.name))
        termsp[i] = termsp[i]/lc

    # swap relation
    if sign % 2 == 1:
        swap = {Eq: Eq, Ne: Ne,
                Lt: Gt, Le: Ge,
                Gt: Lt, Ge: Le}
        rel = swap[rel]

    # construct expression
    eqs = []
    if rel == Ne:
        eqs.append(And(*[Ne(term,0) for term in termsn+termsp]))
    elif rel == Gt:
        eq0 = And(*[Ne(term,0) for term in termsp])
        for i in range(0, len(termsn)+1, 2):
            for neg in combinations(termsn, i):
                pos = tuple(set(termsn)-set(neg))
                eqp = And(*[Gt(p,0) for p in pos])
                eqn = And(*[Lt(n,0) for n in neg])
                eqs.append(And(eq0, eqp, eqn))
    elif rel == Ge:
        for i in range(0, len(termsn)+1, 2):
            for neg in combinations(termsn, i):
                pos = tuple(set(termsn)-set(neg))
                eqp = And(*[Gt(p,0) for p in pos])
                eqn = And(*[Lt(n,0) for n in neg])
                eqs.append(And(eqp, eqn))
    elif rel == Lt:
        eq0 = And(*[Ne(term,0) for term in termsp])
        for i in range(1, len(termsn)+1, 2):
            for neg in combinations(termsn, i):
                pos = tuple(set(termsn)-set(neg))
                eqp = And(*[Gt(p,0) for p in pos])
                eqn = And(*[Lt(n,0) for n in neg])
                eqs.append(And(eq0, eqp, eqn))
    elif rel == Le:
        for i in range(1, len(termsn)+1, 2):
            for neg in combinations(termsn, i):
                pos = tuple(set(termsn)-set(neg))
                eqp = And(*[Gt(p,0) for p in pos])
                eqn = And(*[Lt(n,0) for n in neg])
                eqs.append(And(eqp, eqn))
    if rel in (Eq, Ge, Le):
        for term in termsn+termsp:
            eqs.append(Eq(term,0))

    return Or(*eqs)

def canonicalize_polyeq(eq):
    if not isinstance(eq, Rel):
        return eq
    rel = eq.func
    expr = eq.args[0]-eq.args[1]
    if expr.is_number:
        return rel(expr, 0, evaluate=True)

    # normalize leading coeff
    sign = 0
    lc = LC(expr, sorted(expr.free_symbols, key=lambda x: x.name))
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

def polyrelsimp(expr):
    """expand (polynomial) equation/inequation and canonicalize it
    >>> from sympy import *
    >>> from symplus.strplus import init_mprinting
    >>> init_mprinting()
    >>> x, y, z = symbols('x, y, z')
    >>> Eq(x**2+y, 2*y-1)
    2*y - 1 == x**2 + y
    >>> polyrelsimp(_)
    0 == x**2 - y + 1
    >>> -x**2+x+1 > 0
    -x**2 + x + 1 > 0
    >>> polyrelsimp(_)
    x**2 - x - 1 < 0
    >>> 2*x**2+6*y**2-4 > 0
    2*x**2 + 6*y**2 - 4 > 0
    >>> polyrelsimp(_)
    x**2 + 3*y**2 - 2 > 0
    >>> 2*x**2+6*y**2+4 > 0
    2*x**2 + 6*y**2 + 4 > 0
    >>> polyrelsimp(_)
    True
    >>> x**4+3*x**2*y**3 > 0
    x**4 + 3*x**2*y**3 > 0
    >>> polyrelsimp(_)
    (0 =/= x) /\ (x**2 + 3*y**3 > 0)
    >>> (x**2+1)*(2*x-y) > 0
    (2*x - y)*(x**2 + 1) > 0
    >>> polyrelsimp(_)
    x - y/2 > 0
    >>> eq = Gt((x**2+y**2)*(2*x-y), 0); eq
    (2*x - y)*(x**2 + y**2) > 0
    >>> polyrelsimp(eq)
    (0 =/= x) /\ (0 =/= y) /\ (x - y/2 > 0)
    >>> polyrelsimp(Gt(1,1, evaluate=False))
    False
    """
    return expr.replace(lambda rel: isinstance(rel, Rel),
                        lambda rel: expand_polyeq(rel))

# WARNING: it is unstable
def logicrelsimp(expr, form='dnf', deep=True):
    """ logically simplify relations using totality (WARNING: it is unstable)
    >>> from sympy import *
    >>> from symplus.strplus import init_mprinting
    >>> init_mprinting()
    >>> x, y, z = symbols('x y z')
    >>> logicrelsimp((x>0) >> ((x<=0)&(y<0)))
    x =< 0
    >>> logicrelsimp((x>0) >> (x>=0))
    True
    >>> logicrelsimp((x<0) & (x>0))
    False
    >>> logicrelsimp(((x<0) | (y>0)) & ((x>0) | (y<0)))
    (x < 0) /\ (y < 0) \/ (x > 0) /\ (y > 0)
    >>> logicrelsimp(((x<0) & (y>0)) | ((x>0) & (y<0)))
    (x < 0) /\ (y > 0) \/ (x > 0) /\ (y < 0)
    """
    from sympy.core.symbol import Wild
    from sympy.core import sympify
    from sympy.logic.boolalg import (SOPform, POSform, to_nnf,
                                     _find_predicates, simplify_logic)
    Nt = lambda x: Not(x, evaluate=False)

    if form not in ('cnf', 'dnf'):
        raise ValueError("form can be cnf or dnf only")
    expr = sympify(expr)
    if not isinstance(expr, BooleanFunction):
        return expr

    # canonicalize relations
    expr = expr.replace(lambda rel: isinstance(rel, Rel),
                        lambda rel: canonicalize_polyeq(rel))

    # to nnf
    w = Wild('w')
    expr = to_nnf(expr)
    expr = expr.replace(Not(w), lambda w: Not(w, evaluate=True))

    if is_simplerel(expr):
        # standardize relation
        expr = expr.replace(Ne(w,0), Nt(Eq(w,0)))
        expr = expr.replace(Ge(w,0), Nt(Lt(w,0)))
        expr = expr.replace(Le(w,0), Nt(Gt(w,0)))

        expr = simplify_logic(expr, form, deep)

        return expr

    else:
        # standardize relation
        expr = expr.replace(Ne(w,0), Or(Gt(w,0), Lt(w,0)))
        expr = expr.replace(Ge(w,0), Or(Gt(w,0), Eq(w,0)))
        expr = expr.replace(Le(w,0), Or(Lt(w,0), Eq(w,0)))

        # make totality
        variables = _find_predicates(expr)
        relations = (v for v in variables if isinstance(v, Rel) and v.args[1] == 0)
        totalities = []
        for a in set(rel.args[0] for rel in relations):
            totalities.append(
                Or(And(Gt(a,0), Nt(Eq(a,0)), Nt(Lt(a,0))),
                   And(Nt(Gt(a,0)), Eq(a,0), Nt(Lt(a,0))),
                   And(Nt(Gt(a,0)), Nt(Eq(a,0)), Lt(a,0))))
        totality = And(*totalities)

        # make truth table, don't care table
        truthtable = []
        dontcares = []
        for t in product([0, 1], repeat=len(variables)):
            t = list(t)
            if totality.xreplace(dict(zip(variables, t))) == False:
                dontcares.append(t)
            elif expr.xreplace(dict(zip(variables, t))) == True:
                truthtable.append(t)

        if deep:
            variables = [simplify(v) for v in variables]
        if form == 'dnf':
            expr = SOPform(variables, truthtable, dontcares)
        elif form == 'cnf':
            expr = POSform(variables, truthtable, dontcares)

        return expr


# matrix

def do_indexing(expr):
    from sympy.matrices.expressions.matexpr import MatrixElement
    return expr.replace(MatrixElement, lambda parent, i, j: parent[i,j])

def matsimp(expr):
    """do indexing, Trace, Determinant and expand matrix equation
    >>> from sympy import *
    >>> from symplus.strplus import init_mprinting
    >>> init_mprinting()
    >>> A = ImmutableMatrix(2, 2, symbols('A(:2)(:2)'))
    >>> B = ImmutableMatrix(2, 2, symbols('B(:2)(:2)'))
    >>> C = ImmutableMatrix(2, 2, symbols('C(:2)(:2)'))
    >>> M = MatrixSymbol('M', 2, 2)
    >>> M[1,1].xreplace({M: B*C})
    <BLANKLINE>
    [B00*C00 + B01*C10 B00*C01 + B01*C11]
    [B10*C00 + B11*C10 B10*C01 + B11*C11][1, 1]
    >>> matsimp(_)
    B10*C01 + B11*C11
    >>> Eq(Trace(B+C), 0)
    0 == Trace(
    [B00 + C00 B01 + C01]
    [B10 + C10 B11 + C11])
    >>> matsimp(_)
    0 == B00 + B11 + C00 + C11
    >>> Eq(A.T-A, ZeroMatrix(2,2))
    <BLANKLINE>
    [        0 -A01 + A10]
    [A01 - A10          0] == 0
    >>> matsimp(_)
    (-A01 + A10 == 0) /\ (0 == A01 - A10)
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
    """expand MatrixSymbol as MatrixElement and simplify it
    >>> from sympy import *
    >>> from symplus.strplus import init_mprinting
    >>> init_mprinting()
    >>> A = MatrixSymbol('A', 2, 2)
    >>> Eq(det(A), 0)
    0 == ||A||
    >>> with_matsym(matsimp)(_)
    0 == A[0, 0]*A[1, 1] - A[0, 1]*A[1, 0]
    >>> Eq(A.T*A, Identity(2))
    A'*A == I
    >>> with_matsym(matsimp)(_)
    (0 == A[0, 0]*A[0, 1] + A[1, 0]*A[1, 1]) /\ (1 == A[0, 0]**2 + A[1, 0]**2) /\ (1 == A[0, 1]**2 + A[1, 1]**2)
    """
    from sympy.matrices import MatrixSymbol
    from symplus.setplus import AbstractSet
    def simplify_with_matsym(expr, *args, **kwargs):
        # expand MatrixSymbol as Matrix: A -> [ A[0,0] ,..]
        mats = list(expr.atoms(MatrixSymbol))
        agents = list(Dummy(str(mat)) for mat in mats)
        def protect_var(var, expr):
            return AbstractSet(var.xreplace(dict(zip(mats, agents))), expr)
        expr = expr.replace(AbstractSet, protect_var)
        expr = expr.xreplace(dict((mat, mat.as_explicit()) for mat in mats))
        expr = expr.xreplace(dict(zip(agents, mats)))

        # replace MatrixElement as Symbol: A[i,j] -> Aij
        elems = tuple(elem for mat in mats for elem in mat)
        syms = tuple(Dummy(str(e)) for e in elems)
        expr = expr.xreplace(dict(zip(elems, syms)))

        # simplify expression
        for simp in simplifies:
            expr = simp(expr, *args, **kwargs)

        # replace Symbol as MatrixElement: Aij -> A[i,j]
        expr = expr.xreplace(dict(zip(syms, elems)))

        return expr
    return simplify_with_matsym


simplify_all = with_matsym(matsimp, with_sqrtsimp(simplify, polyrelsimp, logicrelsimp))

