"""
>>> from symplus.strplus import init_mprinting
>>> init_mprinting()
>>> print(RubiksCube)
SymbolicPhysicalPuzzle(
    [Box([2 2 2]', [0 0 0]', eye(3), False) n Halfspace(2/3, [0 0 1]', False) n Halfspace(2/3, [0 1 0]', False) n Halfspace(2/3, [1 0 0]', False),
     Box([2 2 2]', [0 0 0]', eye(3), False) n Halfspace(2/3, [0 0 -1]', False) n Halfspace(2/3, [0 1 0]', False) n Halfspace(2/3, [1 0 0]', False),
     Box([2 2 2]', [0 0 0]', eye(3), False) n Halfspace(-2/3, [0 0 -1]', False) n Halfspace(-2/3, [0 0 1]', False) n Halfspace(2/3, [0 1 0]', False) n Halfspace(2/3, [1 0 0]', False),
     Box([2 2 2]', [0 0 0]', eye(3), False) n Halfspace(2/3, [0 -1 0]', False) n Halfspace(2/3, [0 0 1]', False) n Halfspace(2/3, [1 0 0]', False),
     Box([2 2 2]', [0 0 0]', eye(3), False) n Halfspace(2/3, [0 -1 0]', False) n Halfspace(2/3, [0 0 -1]', False) n Halfspace(2/3, [1 0 0]', False),
     Box([2 2 2]', [0 0 0]', eye(3), False) n Halfspace(-2/3, [0 0 -1]', False) n Halfspace(-2/3, [0 0 1]', False) n Halfspace(2/3, [0 -1 0]', False) n Halfspace(2/3, [1 0 0]', False),
     Box([2 2 2]', [0 0 0]', eye(3), False) n Halfspace(-2/3, [0 -1 0]', False) n Halfspace(-2/3, [0 1 0]', False) n Halfspace(2/3, [0 0 1]', False) n Halfspace(2/3, [1 0 0]', False),
     Box([2 2 2]', [0 0 0]', eye(3), False) n Halfspace(-2/3, [0 -1 0]', False) n Halfspace(-2/3, [0 1 0]', False) n Halfspace(2/3, [0 0 -1]', False) n Halfspace(2/3, [1 0 0]', False),
     Box([2 2 2]', [0 0 0]', eye(3), False) n Halfspace(-2/3, [0 -1 0]', False) n Halfspace(-2/3, [0 0 -1]', False) n Halfspace(-2/3, [0 0 1]', False) n Halfspace(-2/3, [0 1 0]', False) n Halfspace(2/3, [1 0 0]', False),
     Box([2 2 2]', [0 0 0]', eye(3), False) n Halfspace(2/3, [-1 0 0]', False) n Halfspace(2/3, [0 0 1]', False) n Halfspace(2/3, [0 1 0]', False),
     Box([2 2 2]', [0 0 0]', eye(3), False) n Halfspace(2/3, [-1 0 0]', False) n Halfspace(2/3, [0 0 -1]', False) n Halfspace(2/3, [0 1 0]', False),
     Box([2 2 2]', [0 0 0]', eye(3), False) n Halfspace(-2/3, [0 0 -1]', False) n Halfspace(-2/3, [0 0 1]', False) n Halfspace(2/3, [-1 0 0]', False) n Halfspace(2/3, [0 1 0]', False),
     Box([2 2 2]', [0 0 0]', eye(3), False) n Halfspace(2/3, [-1 0 0]', False) n Halfspace(2/3, [0 -1 0]', False) n Halfspace(2/3, [0 0 1]', False),
     Box([2 2 2]', [0 0 0]', eye(3), False) n Halfspace(2/3, [-1 0 0]', False) n Halfspace(2/3, [0 -1 0]', False) n Halfspace(2/3, [0 0 -1]', False),
     Box([2 2 2]', [0 0 0]', eye(3), False) n Halfspace(-2/3, [0 0 -1]', False) n Halfspace(-2/3, [0 0 1]', False) n Halfspace(2/3, [-1 0 0]', False) n Halfspace(2/3, [0 -1 0]', False),
     Box([2 2 2]', [0 0 0]', eye(3), False) n Halfspace(-2/3, [0 -1 0]', False) n Halfspace(-2/3, [0 1 0]', False) n Halfspace(2/3, [-1 0 0]', False) n Halfspace(2/3, [0 0 1]', False),
     Box([2 2 2]', [0 0 0]', eye(3), False) n Halfspace(-2/3, [0 -1 0]', False) n Halfspace(-2/3, [0 1 0]', False) n Halfspace(2/3, [-1 0 0]', False) n Halfspace(2/3, [0 0 -1]', False),
     Box([2 2 2]', [0 0 0]', eye(3), False) n Halfspace(-2/3, [0 -1 0]', False) n Halfspace(-2/3, [0 0 -1]', False) n Halfspace(-2/3, [0 0 1]', False) n Halfspace(-2/3, [0 1 0]', False) n Halfspace(2/3, [-1 0 0]', False),
     Box([2 2 2]', [0 0 0]', eye(3), False) n Halfspace(-2/3, [-1 0 0]', False) n Halfspace(-2/3, [1 0 0]', False) n Halfspace(2/3, [0 0 1]', False) n Halfspace(2/3, [0 1 0]', False),
     Box([2 2 2]', [0 0 0]', eye(3), False) n Halfspace(-2/3, [-1 0 0]', False) n Halfspace(-2/3, [1 0 0]', False) n Halfspace(2/3, [0 0 -1]', False) n Halfspace(2/3, [0 1 0]', False),
     Box([2 2 2]', [0 0 0]', eye(3), False) n Halfspace(-2/3, [-1 0 0]', False) n Halfspace(-2/3, [0 0 -1]', False) n Halfspace(-2/3, [0 0 1]', False) n Halfspace(-2/3, [1 0 0]', False) n Halfspace(2/3, [0 1 0]', False),
     Box([2 2 2]', [0 0 0]', eye(3), False) n Halfspace(-2/3, [-1 0 0]', False) n Halfspace(-2/3, [1 0 0]', False) n Halfspace(2/3, [0 -1 0]', False) n Halfspace(2/3, [0 0 1]', False),
     Box([2 2 2]', [0 0 0]', eye(3), False) n Halfspace(-2/3, [-1 0 0]', False) n Halfspace(-2/3, [1 0 0]', False) n Halfspace(2/3, [0 -1 0]', False) n Halfspace(2/3, [0 0 -1]', False),
     Box([2 2 2]', [0 0 0]', eye(3), False) n Halfspace(-2/3, [-1 0 0]', False) n Halfspace(-2/3, [0 0 -1]', False) n Halfspace(-2/3, [0 0 1]', False) n Halfspace(-2/3, [1 0 0]', False) n Halfspace(2/3, [0 -1 0]', False),
     Box([2 2 2]', [0 0 0]', eye(3), False) n Halfspace(-2/3, [-1 0 0]', False) n Halfspace(-2/3, [0 -1 0]', False) n Halfspace(-2/3, [0 1 0]', False) n Halfspace(-2/3, [1 0 0]', False) n Halfspace(2/3, [0 0 1]', False),
     Box([2 2 2]', [0 0 0]', eye(3), False) n Halfspace(-2/3, [-1 0 0]', False) n Halfspace(-2/3, [0 -1 0]', False) n Halfspace(-2/3, [0 1 0]', False) n Halfspace(-2/3, [1 0 0]', False) n Halfspace(2/3, [0 0 -1]', False),
     Halfspace(-2/3, [-1 0 0]', False) n Halfspace(-2/3, [0 -1 0]', False) n Halfspace(-2/3, [0 0 -1]', False) n Halfspace(-2/3, [0 0 1]', False) n Halfspace(-2/3, [0 1 0]', False) n Halfspace(-2/3, [1 0 0]', False)],
    T_RR3, SE3^*)
"""
from sympy import sympify
from symplus.affine import *
from symplus.euclid import *
from magicpy.puzzle.phy import *


unit = sympify(2)/3
directions = [ i,-i, j,-j, k,-k]
RubiksCube = SymbolicPhysicalPuzzle([Box()])
RubiksCube = RubiksCube.cross_common((Halfspace( unit, d), Halfspace(-unit,-d)) for d in directions)
RubiksCube = RubiksCube.simplify()

