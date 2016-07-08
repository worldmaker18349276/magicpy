"""
>>> print(str(ball2x2x2))
SymbolicSO3PhysicalPuzzle(
    [Halfspace([-1, 0, 0]', 0, False) n Halfspace([0, -1, 0]', 0, False) n Halfspace([0, 0, -1]', 0, False) n Sphere(1, [0, 0, 0]', False),
     Halfspace([-1, 0, 0]', 0, False) n Halfspace([0, -1, 0]', 0, False) n Halfspace([0, 0, 1]', 0, False) n Sphere(1, [0, 0, 0]', False),
     Halfspace([-1, 0, 0]', 0, False) n Halfspace([0, 0, -1]', 0, False) n Halfspace([0, 1, 0]', 0, False) n Sphere(1, [0, 0, 0]', False),
     Halfspace([-1, 0, 0]', 0, False) n Halfspace([0, 0, 1]', 0, False) n Halfspace([0, 1, 0]', 0, False) n Sphere(1, [0, 0, 0]', False),
     Halfspace([0, -1, 0]', 0, False) n Halfspace([0, 0, -1]', 0, False) n Halfspace([1, 0, 0]', 0, False) n Sphere(1, [0, 0, 0]', False),
     Halfspace([0, -1, 0]', 0, False) n Halfspace([0, 0, 1]', 0, False) n Halfspace([1, 0, 0]', 0, False) n Sphere(1, [0, 0, 0]', False),
     Halfspace([0, 0, -1]', 0, False) n Halfspace([0, 1, 0]', 0, False) n Halfspace([1, 0, 0]', 0, False) n Sphere(1, [0, 0, 0]', False),
     Halfspace([0, 0, 1]', 0, False) n Halfspace([0, 1, 0]', 0, False) n Halfspace([1, 0, 0]', 0, False) n Sphere(1, [0, 0, 0]', False)])
>>> rot = rotate(pi/4, i); rot
TransformationPath(1, t, EuclideanTransformation(Matrix([
[0],
[0],
[0]]), Matrix([
[cos(pi*t/8)],
[sin(pi*t/8)],
[          0],
[          0]]), 1))
>>> op = SymbolicPartitionalOperation({Halfspace(i): rot, Halfspace(-i): identity()})
>>> ball2x2x2 = ball2x2x2.apply(op); print(str(ball2x2x2))
SymbolicSO3PhysicalPuzzle(
    [Halfspace([-1, 0, 0]', 0, False) n Halfspace([0, -1, 0]', 0, False) n Halfspace([0, 0, -1]', 0, False) n Sphere(1, [0, 0, 0]', False),
     Halfspace([-1, 0, 0]', 0, False) n Halfspace([0, -1, 0]', 0, False) n Halfspace([0, 0, 1]', 0, False) n Sphere(1, [0, 0, 0]', False),
     Halfspace([-1, 0, 0]', 0, False) n Halfspace([0, 0, -1]', 0, False) n Halfspace([0, 1, 0]', 0, False) n Sphere(1, [0, 0, 0]', False),
     Halfspace([-1, 0, 0]', 0, False) n Halfspace([0, 0, 1]', 0, False) n Halfspace([0, 1, 0]', 0, False) n Sphere(1, [0, 0, 0]', False),
     Halfspace([0, -sqrt(2)/2, -sqrt(2)/2]', 0, False) n Halfspace([0, sqrt(2)/2, -sqrt(2)/2]', 0, False) n Halfspace([1, 0, 0]', 0, False) n Sphere(1, [0, 0, 0]', False),
     Halfspace([0, -sqrt(2)/2, -sqrt(2)/2]', 0, False) n Halfspace([0, -sqrt(2)/2, sqrt(2)/2]', 0, False) n Halfspace([1, 0, 0]', 0, False) n Sphere(1, [0, 0, 0]', False),
     Halfspace([0, sqrt(2)/2, -sqrt(2)/2]', 0, False) n Halfspace([0, sqrt(2)/2, sqrt(2)/2]', 0, False) n Halfspace([1, 0, 0]', 0, False) n Sphere(1, [0, 0, 0]', False),
     Halfspace([0, -sqrt(2)/2, sqrt(2)/2]', 0, False) n Halfspace([0, sqrt(2)/2, sqrt(2)/2]', 0, False) n Halfspace([1, 0, 0]', 0, False) n Sphere(1, [0, 0, 0]', False)])
"""
from magicpy.model.affine import *
from magicpy.model.euclid import *
from magicpy.puzzle.sym import *

ball2x2x2 = SymbolicSO3PhysicalPuzzle([sphere()])
ball2x2x2 = ball2x2x2.cut_by(
    (Halfspace(-i), Halfspace(i)),
    (Halfspace(-j), Halfspace(j)),
    (Halfspace(-k), Halfspace(k)))

