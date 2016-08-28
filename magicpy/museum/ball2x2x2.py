"""
>>> print(str(ball2x2x2))
SymbolicSO3PhysicalPuzzle(
    [Halfspace(0, [-1, 0, 0], False) n Halfspace(0, [0, -1, 0], False) n Halfspace(0, [0, 0, -1], False) n Sphere(1, [0, 0, 0], False),
     Halfspace(0, [-1, 0, 0], False) n Halfspace(0, [0, -1, 0], False) n Halfspace(0, [0, 0, 1], False) n Sphere(1, [0, 0, 0], False),
     Halfspace(0, [-1, 0, 0], False) n Halfspace(0, [0, 0, -1], False) n Halfspace(0, [0, 1, 0], False) n Sphere(1, [0, 0, 0], False),
     Halfspace(0, [-1, 0, 0], False) n Halfspace(0, [0, 0, 1], False) n Halfspace(0, [0, 1, 0], False) n Sphere(1, [0, 0, 0], False),
     Halfspace(0, [0, -1, 0], False) n Halfspace(0, [0, 0, -1], False) n Halfspace(0, [1, 0, 0], False) n Sphere(1, [0, 0, 0], False),
     Halfspace(0, [0, -1, 0], False) n Halfspace(0, [0, 0, 1], False) n Halfspace(0, [1, 0, 0], False) n Sphere(1, [0, 0, 0], False),
     Halfspace(0, [0, 0, -1], False) n Halfspace(0, [0, 1, 0], False) n Halfspace(0, [1, 0, 0], False) n Sphere(1, [0, 0, 0], False),
     Halfspace(0, [0, 0, 1], False) n Halfspace(0, [0, 1, 0], False) n Halfspace(0, [1, 0, 0], False) n Sphere(1, [0, 0, 0], False)])
>>> rot = rotate(pi/4, i); rot
TransformationPath(1, t, EuclideanTransformation([0, 0, 0], [cos(pi*t/8), sin(pi*t/8), 0, 0], 1))
>>> op = SymbolicPartitionalOperation({Halfspace(0, i): rot, Halfspace(0,-i): identity()})
>>> ball2x2x2 = ball2x2x2.apply(op); print(str(ball2x2x2))
SymbolicSO3PhysicalPuzzle(
    [Halfspace(0, [-1, 0, 0], False) n Halfspace(0, [0, -1, 0], False) n Halfspace(0, [0, 0, -1], False) n Sphere(1, [0, 0, 0], False),
     Halfspace(0, [-1, 0, 0], False) n Halfspace(0, [0, -1, 0], False) n Halfspace(0, [0, 0, 1], False) n Sphere(1, [0, 0, 0], False),
     Halfspace(0, [-1, 0, 0], False) n Halfspace(0, [0, 0, -1], False) n Halfspace(0, [0, 1, 0], False) n Sphere(1, [0, 0, 0], False),
     Halfspace(0, [-1, 0, 0], False) n Halfspace(0, [0, 0, 1], False) n Halfspace(0, [0, 1, 0], False) n Sphere(1, [0, 0, 0], False),
     Halfspace(0, [0, -sqrt(2)/2, -sqrt(2)/2], False) n Halfspace(0, [0, sqrt(2)/2, -sqrt(2)/2], False) n Halfspace(0, [1, 0, 0], False) n Sphere(1, [0, 0, 0], False),
     Halfspace(0, [0, -sqrt(2)/2, -sqrt(2)/2], False) n Halfspace(0, [0, -sqrt(2)/2, sqrt(2)/2], False) n Halfspace(0, [1, 0, 0], False) n Sphere(1, [0, 0, 0], False),
     Halfspace(0, [0, sqrt(2)/2, -sqrt(2)/2], False) n Halfspace(0, [0, sqrt(2)/2, sqrt(2)/2], False) n Halfspace(0, [1, 0, 0], False) n Sphere(1, [0, 0, 0], False),
     Halfspace(0, [0, -sqrt(2)/2, sqrt(2)/2], False) n Halfspace(0, [0, sqrt(2)/2, sqrt(2)/2], False) n Halfspace(0, [1, 0, 0], False) n Sphere(1, [0, 0, 0], False)])
"""
from symplus.affine import *
from symplus.euclid import *
from magicpy.puzzle.phy import *

ball2x2x2 = SymbolicSO3PhysicalPuzzle([Sphere()])
ball2x2x2 = ball2x2x2.cross_common([
    (Halfspace(0,-i), Halfspace(0, i)),
    (Halfspace(0,-j), Halfspace(0, j)),
    (Halfspace(0,-k), Halfspace(0, k))])

