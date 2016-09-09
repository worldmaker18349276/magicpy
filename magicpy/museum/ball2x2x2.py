"""
>>> from symplus.strplus import init_mprinting
>>> init_mprinting()
>>> print(ball2x2x2)
SymbolicPhysicalPuzzle(
    [Halfspace(0, [-1 0 0]', False) n Halfspace(0, [0 -1 0]', False) n Halfspace(0, [0 0 -1]', False) n Sphere(1, [0 0 0]', False),
     Halfspace(0, [-1 0 0]', False) n Halfspace(0, [0 -1 0]', False) n Halfspace(0, [0 0 1]', False) n Sphere(1, [0 0 0]', False),
     Halfspace(0, [-1 0 0]', False) n Halfspace(0, [0 0 -1]', False) n Halfspace(0, [0 1 0]', False) n Sphere(1, [0 0 0]', False),
     Halfspace(0, [-1 0 0]', False) n Halfspace(0, [0 0 1]', False) n Halfspace(0, [0 1 0]', False) n Sphere(1, [0 0 0]', False),
     Halfspace(0, [0 -1 0]', False) n Halfspace(0, [0 0 -1]', False) n Halfspace(0, [1 0 0]', False) n Sphere(1, [0 0 0]', False),
     Halfspace(0, [0 -1 0]', False) n Halfspace(0, [0 0 1]', False) n Halfspace(0, [1 0 0]', False) n Sphere(1, [0 0 0]', False),
     Halfspace(0, [0 0 -1]', False) n Halfspace(0, [0 1 0]', False) n Halfspace(0, [1 0 0]', False) n Sphere(1, [0 0 0]', False),
     Halfspace(0, [0 0 1]', False) n Halfspace(0, [0 1 0]', False) n Halfspace(0, [1 0 0]', False) n Sphere(1, [0 0 0]', False)],
    T_RR3, SE3^*)
>>> rot = rotate(pi/4, i); rot
[t ~ 1 |-> EuclideanTransformation([0 0 0]', [cos(pi*t/8) sin(pi*t/8) 0 0]', 1)]
>>> op = SymbolicPartitionalOperation({Halfspace(0, i): rot, Halfspace(0,-i): identity()})
>>> ball2x2x2 = op.apply(ball2x2x2); print(ball2x2x2)
SymbolicPhysicalPuzzle(
    [Halfspace(0, [-1 0 0]', False) n Halfspace(0, [0 -1 0]', False) n Halfspace(0, [0 0 -1]', False) n Sphere(1, [0 0 0]', False),
     Halfspace(0, [-1 0 0]', False) n Halfspace(0, [0 -1 0]', False) n Halfspace(0, [0 0 1]', False) n Sphere(1, [0 0 0]', False),
     Halfspace(0, [-1 0 0]', False) n Halfspace(0, [0 0 -1]', False) n Halfspace(0, [0 1 0]', False) n Sphere(1, [0 0 0]', False),
     Halfspace(0, [-1 0 0]', False) n Halfspace(0, [0 0 1]', False) n Halfspace(0, [0 1 0]', False) n Sphere(1, [0 0 0]', False),
     Halfspace(0, [0 -sqrt(2)/2 -sqrt(2)/2]', False) n Halfspace(0, [0 sqrt(2)/2 -sqrt(2)/2]', False) n Halfspace(0, [1 0 0]', False) n Sphere(1, [0 0 0]', False),
     Halfspace(0, [0 -sqrt(2)/2 -sqrt(2)/2]', False) n Halfspace(0, [0 -sqrt(2)/2 sqrt(2)/2]', False) n Halfspace(0, [1 0 0]', False) n Sphere(1, [0 0 0]', False),
     Halfspace(0, [0 sqrt(2)/2 -sqrt(2)/2]', False) n Halfspace(0, [0 sqrt(2)/2 sqrt(2)/2]', False) n Halfspace(0, [1 0 0]', False) n Sphere(1, [0 0 0]', False),
     Halfspace(0, [0 -sqrt(2)/2 sqrt(2)/2]', False) n Halfspace(0, [0 sqrt(2)/2 sqrt(2)/2]', False) n Halfspace(0, [1 0 0]', False) n Sphere(1, [0 0 0]', False)],
    T_RR3, SE3^*)
"""
from symplus.affine import *
from symplus.euclid import *
from magicpy.puzzle.phy import *

ball2x2x2 = SymbolicPhysicalPuzzle([Sphere()])
ball2x2x2 = ball2x2x2.cross_common([
    (Halfspace(0,-i), Halfspace(0, i)),
    (Halfspace(0,-j), Halfspace(0, j)),
    (Halfspace(0,-k), Halfspace(0, k))])

