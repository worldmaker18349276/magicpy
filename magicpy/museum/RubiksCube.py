"""
>>> print(str(RubiksCube))
SymbolicSO3PhysicalPuzzle(
    [Halfspace([-1, 0, 0]', -1, False) n Halfspace([0, -1, 0]', 1/3, False) n Halfspace([0, 0, -1]', -1, False) n Halfspace([0, 0, 1]', 1/3, False) n Halfspace([0, 1, 0]', -1, False) n Halfspace([1, 0, 0]', 1/3, False),
     Halfspace([-1, 0, 0]', 1/3, False) n Halfspace([0, -1, 0]', 1/3, False) n Halfspace([0, 0, -1]', -1, False) n Halfspace([0, 0, 1]', 1/3, False) n Halfspace([0, 1, 0]', -1, False) n Halfspace([1, 0, 0]', -1, False),
     Halfspace([-1, 0, 0]', -1/3, False) n Halfspace([0, -1, 0]', 1/3, False) n Halfspace([0, 0, -1]', -1, False) n Halfspace([0, 0, 1]', 1/3, False) n Halfspace([0, 1, 0]', -1, False) n Halfspace([1, 0, 0]', -1/3, False),
     Halfspace([-1, 0, 0]', -1, False) n Halfspace([0, -1, 0]', 1/3, False) n Halfspace([0, 0, -1]', 1/3, False) n Halfspace([0, 0, 1]', -1, False) n Halfspace([0, 1, 0]', -1, False) n Halfspace([1, 0, 0]', 1/3, False),
     Halfspace([-1, 0, 0]', 1/3, False) n Halfspace([0, -1, 0]', 1/3, False) n Halfspace([0, 0, -1]', 1/3, False) n Halfspace([0, 0, 1]', -1, False) n Halfspace([0, 1, 0]', -1, False) n Halfspace([1, 0, 0]', -1, False),
     Halfspace([-1, 0, 0]', -1/3, False) n Halfspace([0, -1, 0]', 1/3, False) n Halfspace([0, 0, -1]', 1/3, False) n Halfspace([0, 0, 1]', -1, False) n Halfspace([0, 1, 0]', -1, False) n Halfspace([1, 0, 0]', -1/3, False),
     Halfspace([-1, 0, 0]', -1, False) n Halfspace([0, -1, 0]', 1/3, False) n Halfspace([0, 0, -1]', -1/3, False) n Halfspace([0, 0, 1]', -1/3, False) n Halfspace([0, 1, 0]', -1, False) n Halfspace([1, 0, 0]', 1/3, False),
     Halfspace([-1, 0, 0]', 1/3, False) n Halfspace([0, -1, 0]', 1/3, False) n Halfspace([0, 0, -1]', -1/3, False) n Halfspace([0, 0, 1]', -1/3, False) n Halfspace([0, 1, 0]', -1, False) n Halfspace([1, 0, 0]', -1, False),
     Halfspace([-1, 0, 0]', -1/3, False) n Halfspace([0, -1, 0]', 1/3, False) n Halfspace([0, 0, -1]', -1/3, False) n Halfspace([0, 0, 1]', -1/3, False) n Halfspace([0, 1, 0]', -1, False) n Halfspace([1, 0, 0]', -1/3, False),
     Halfspace([-1, 0, 0]', -1, False) n Halfspace([0, -1, 0]', -1, False) n Halfspace([0, 0, -1]', -1, False) n Halfspace([0, 0, 1]', 1/3, False) n Halfspace([0, 1, 0]', 1/3, False) n Halfspace([1, 0, 0]', 1/3, False),
     Halfspace([-1, 0, 0]', 1/3, False) n Halfspace([0, -1, 0]', -1, False) n Halfspace([0, 0, -1]', -1, False) n Halfspace([0, 0, 1]', 1/3, False) n Halfspace([0, 1, 0]', 1/3, False) n Halfspace([1, 0, 0]', -1, False),
     Halfspace([-1, 0, 0]', -1/3, False) n Halfspace([0, -1, 0]', -1, False) n Halfspace([0, 0, -1]', -1, False) n Halfspace([0, 0, 1]', 1/3, False) n Halfspace([0, 1, 0]', 1/3, False) n Halfspace([1, 0, 0]', -1/3, False),
     Halfspace([-1, 0, 0]', -1, False) n Halfspace([0, -1, 0]', -1/3, False) n Halfspace([0, 0, -1]', -1, False) n Halfspace([0, 0, 1]', 1/3, False) n Halfspace([0, 1, 0]', -1/3, False) n Halfspace([1, 0, 0]', 1/3, False),
     Halfspace([-1, 0, 0]', 1/3, False) n Halfspace([0, -1, 0]', -1/3, False) n Halfspace([0, 0, -1]', -1, False) n Halfspace([0, 0, 1]', 1/3, False) n Halfspace([0, 1, 0]', -1/3, False) n Halfspace([1, 0, 0]', -1, False),
     Halfspace([-1, 0, 0]', -1/3, False) n Halfspace([0, -1, 0]', -1/3, False) n Halfspace([0, 0, -1]', -1, False) n Halfspace([0, 0, 1]', 1/3, False) n Halfspace([0, 1, 0]', -1/3, False) n Halfspace([1, 0, 0]', -1/3, False),
     Halfspace([-1, 0, 0]', -1, False) n Halfspace([0, -1, 0]', -1, False) n Halfspace([0, 0, -1]', 1/3, False) n Halfspace([0, 0, 1]', -1, False) n Halfspace([0, 1, 0]', 1/3, False) n Halfspace([1, 0, 0]', 1/3, False),
     Halfspace([-1, 0, 0]', 1/3, False) n Halfspace([0, -1, 0]', -1, False) n Halfspace([0, 0, -1]', 1/3, False) n Halfspace([0, 0, 1]', -1, False) n Halfspace([0, 1, 0]', 1/3, False) n Halfspace([1, 0, 0]', -1, False),
     Halfspace([-1, 0, 0]', -1/3, False) n Halfspace([0, -1, 0]', -1, False) n Halfspace([0, 0, -1]', 1/3, False) n Halfspace([0, 0, 1]', -1, False) n Halfspace([0, 1, 0]', 1/3, False) n Halfspace([1, 0, 0]', -1/3, False),
     Halfspace([-1, 0, 0]', -1, False) n Halfspace([0, -1, 0]', -1, False) n Halfspace([0, 0, -1]', -1/3, False) n Halfspace([0, 0, 1]', -1/3, False) n Halfspace([0, 1, 0]', 1/3, False) n Halfspace([1, 0, 0]', 1/3, False),
     Halfspace([-1, 0, 0]', 1/3, False) n Halfspace([0, -1, 0]', -1, False) n Halfspace([0, 0, -1]', -1/3, False) n Halfspace([0, 0, 1]', -1/3, False) n Halfspace([0, 1, 0]', 1/3, False) n Halfspace([1, 0, 0]', -1, False),
     Halfspace([-1, 0, 0]', -1/3, False) n Halfspace([0, -1, 0]', -1, False) n Halfspace([0, 0, -1]', -1/3, False) n Halfspace([0, 0, 1]', -1/3, False) n Halfspace([0, 1, 0]', 1/3, False) n Halfspace([1, 0, 0]', -1/3, False),
     Halfspace([-1, 0, 0]', -1, False) n Halfspace([0, -1, 0]', -1/3, False) n Halfspace([0, 0, -1]', 1/3, False) n Halfspace([0, 0, 1]', -1, False) n Halfspace([0, 1, 0]', -1/3, False) n Halfspace([1, 0, 0]', 1/3, False),
     Halfspace([-1, 0, 0]', 1/3, False) n Halfspace([0, -1, 0]', -1/3, False) n Halfspace([0, 0, -1]', 1/3, False) n Halfspace([0, 0, 1]', -1, False) n Halfspace([0, 1, 0]', -1/3, False) n Halfspace([1, 0, 0]', -1, False),
     Halfspace([-1, 0, 0]', -1/3, False) n Halfspace([0, -1, 0]', -1/3, False) n Halfspace([0, 0, -1]', 1/3, False) n Halfspace([0, 0, 1]', -1, False) n Halfspace([0, 1, 0]', -1/3, False) n Halfspace([1, 0, 0]', -1/3, False),
     Halfspace([-1, 0, 0]', -1, False) n Halfspace([0, -1, 0]', -1/3, False) n Halfspace([0, 0, -1]', -1/3, False) n Halfspace([0, 0, 1]', -1/3, False) n Halfspace([0, 1, 0]', -1/3, False) n Halfspace([1, 0, 0]', 1/3, False),
     Halfspace([-1, 0, 0]', 1/3, False) n Halfspace([0, -1, 0]', -1/3, False) n Halfspace([0, 0, -1]', -1/3, False) n Halfspace([0, 0, 1]', -1/3, False) n Halfspace([0, 1, 0]', -1/3, False) n Halfspace([1, 0, 0]', -1, False),
     Halfspace([-1, 0, 0]', -1/3, False) n Halfspace([0, -1, 0]', -1/3, False) n Halfspace([0, 0, -1]', -1/3, False) n Halfspace([0, 0, 1]', -1/3, False) n Halfspace([0, 1, 0]', -1/3, False) n Halfspace([1, 0, 0]', -1/3, False)])
"""
from sympy import S
from magicpy.model.affine import *
from magicpy.model.euclid import *
from magicpy.puzzle.sym import *
from magicpy.model.poly import vertices_octa


RubiksCube = SymbolicSO3PhysicalPuzzle([cube()])
RubiksCube = RubiksCube.cut_by(*[(Halfspace(v, S.One/3), Halfspace(-v, -S.One/3)) for v in vertices_octa])
RubiksCube = RubiksCube.simp()

