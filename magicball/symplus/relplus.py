from itertools import *
from sympy.core import S, Pow, Mul, Rel, Eq, Ne, Gt, Lt, Ge, Le
from sympy.logic import true, false, And, Or, Not
from sympy.logic.boolalg import BooleanFunction
from sympy.polys import factor, LC, Poly, PolynomialError
from sympy.assumptions import Q, ask


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
    relations = tuple(filter(lambda v: isinstance(v, Rel), variables))
    if any(rel.args[1] != 0 for rel in relations):
        return False
    simple_form = {Eq: Eq, Ne: Eq,
                   Gt: Gt, Le: Gt,
                   Lt: Lt, Ge: Lt}
    return all(len(set(simple_form[rel.func] for rel in rels)) == 1
               for _, rels in groupby(relations, lambda r: r.args[0]))


def expand_polyeq(eq):
    """expand (polynomial) equation/inequation and canonicalize it
    >>> from sympy import *
    >>> x, y, z = symbols('x, y, z')
    >>> Eq(x**2+y, 2*y-1)
    x**2 + y == 2*y - 1
    >>> expand_polyeq(_)
    x**2 - y + 1 == 0
    >>> -x**2+x+1 > 0
    -x**2 + x + 1 > 0
    >>> expand_polyeq(_)
    x**2 - x - 1 < 0
    >>> 2*x**2+6*y**2-4 > 0
    2*x**2 + 6*y**2 - 4 > 0
    >>> expand_polyeq(_)
    x**2 + 3*y**2 - 2 > 0
    >>> 2*x**2+6*y**2+4 > 0
    2*x**2 + 6*y**2 + 4 > 0
    >>> expand_polyeq(_)
    True
    >>> x**4+3*x**2*y**3 > 0
    x**4 + 3*x**2*y**3 > 0
    >>> expand_polyeq(_)
    And(x != 0, x**2 + 3*y**3 > 0)
    >>> (x**2+1)*(2*x-y) > 0
    (2*x - y)*(x**2 + 1) > 0
    >>> expand_polyeq(_)
    x - y/2 > 0
    >>> eq = Gt((x**2+y**2)*(2*x-y), 0); eq
    (2*x - y)*(x**2 + y**2) > 0
    >>> expand_polyeq(eq)
    And(x != 0, x - y/2 > 0, y != 0)
    >>> expand_polyeq(Gt(1,1, evaluate=False))
    False
    """
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
    terms = tuple(filterfalse(_is_positive, terms))
    sign = len(terms)
    terms = tuple(filterfalse(_is_negative, terms))
    sign -= len(terms)

    # reduce power terms
    terms1 = filterfalse(lambda t: isinstance(t, Pow), terms)
    termspow = tuple(filter(lambda t: isinstance(t, Pow), terms))
    terms2 = filter(lambda t: t.args[1]%2==0, termspow)
    terms2 = map(lambda t: t.args[0], terms2)
    terms3 = filter(lambda t: t.args[1]%2==1, termspow)
    terms3 = map(lambda t: t.args[0], terms3)

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
    return expr.replace(lambda rel: isinstance(rel, Rel),
                        lambda rel: expand_polyeq(rel))

def logicrelsimp(expr, form='dnf', deep=True):
    """logic simplify for relation
    >>> from sympy import *
    >>> x, y, z = symbols('x y z')
    >>> logicrelsimp((x>0) >> ((x<=0)&(y<0)))
    x <= 0
    >>> logicrelsimp((x>0) >> (x>=0))
    True
    >>> logicrelsimp((x<0) & (x>0))
    False
    >>> logicrelsimp(((x<0) | (y>0)) & ((x>0) | (y<0)))
    Or(And(x < 0, y < 0), And(x > 0, y > 0))
    >>> logicrelsimp(((x<0) & (y>0)) | ((x>0) & (y<0)))
    Or(And(x < 0, y > 0), And(x > 0, y < 0))
    """
    from sympy.core.symbol import Wild
    from sympy.core import sympify
    from sympy.simplify import simplify
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
        relations = filter(lambda v: isinstance(v, Rel) and v.args[1] == 0, variables)
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

