"""
>>> print(str(RubiksCube))
SymbolicSO3PhysicalPuzzle(
    {{(x, y, z) : (x + 1 >= 0) & (x + 1/3 < 0) & (y + 1 >= 0) & (y + 1/3 < 0) & (z + 1 >= 0) & (z + 1/3 < 0)},
     {(x, y, z) : (x + 1 >= 0) & (x + 1/3 < 0) & (y + 1 >= 0) & (y + 1/3 < 0) & (z + 1/3 >= 0) & (z - 1/3 <= 0)},
     {(x, y, z) : (x + 1 >= 0) & (x + 1/3 < 0) & (y + 1 >= 0) & (y + 1/3 < 0) & (z - 1 <= 0) & (z - 1/3 > 0)},
     {(x, y, z) : (x + 1 >= 0) & (x + 1/3 < 0) & (y + 1/3 >= 0) & (y - 1/3 <= 0) & (z + 1 >= 0) & (z + 1/3 < 0)},
     {(x, y, z) : (x + 1 >= 0) & (x + 1/3 < 0) & (y + 1/3 >= 0) & (y - 1/3 <= 0) & (z + 1/3 >= 0) & (z - 1/3 <= 0)},
     {(x, y, z) : (x + 1 >= 0) & (x + 1/3 < 0) & (y + 1/3 >= 0) & (y - 1/3 <= 0) & (z - 1 <= 0) & (z - 1/3 > 0)},
     {(x, y, z) : (x + 1 >= 0) & (x + 1/3 < 0) & (y - 1 <= 0) & (y - 1/3 > 0) & (z + 1 >= 0) & (z + 1/3 < 0)},
     {(x, y, z) : (x + 1 >= 0) & (x + 1/3 < 0) & (y - 1 <= 0) & (y - 1/3 > 0) & (z + 1/3 >= 0) & (z - 1/3 <= 0)},
     {(x, y, z) : (x + 1 >= 0) & (x + 1/3 < 0) & (y - 1 <= 0) & (y - 1/3 > 0) & (z - 1 <= 0) & (z - 1/3 > 0)},
     {(x, y, z) : (x + 1/3 >= 0) & (x - 1/3 <= 0) & (y + 1 >= 0) & (y + 1/3 < 0) & (z + 1 >= 0) & (z + 1/3 < 0)},
     {(x, y, z) : (x + 1/3 >= 0) & (x - 1/3 <= 0) & (y + 1 >= 0) & (y + 1/3 < 0) & (z + 1/3 >= 0) & (z - 1/3 <= 0)},
     {(x, y, z) : (x + 1/3 >= 0) & (x - 1/3 <= 0) & (y + 1 >= 0) & (y + 1/3 < 0) & (z - 1 <= 0) & (z - 1/3 > 0)},
     {(x, y, z) : (x + 1/3 >= 0) & (x - 1/3 <= 0) & (y + 1/3 >= 0) & (y - 1/3 <= 0) & (z + 1 >= 0) & (z + 1/3 < 0)},
     {(x, y, z) : (x + 1/3 >= 0) & (x - 1/3 <= 0) & (y + 1/3 >= 0) & (y - 1/3 <= 0) & (z + 1/3 >= 0) & (z - 1/3 <= 0)},
     {(x, y, z) : (x + 1/3 >= 0) & (x - 1/3 <= 0) & (y + 1/3 >= 0) & (y - 1/3 <= 0) & (z - 1 <= 0) & (z - 1/3 > 0)},
     {(x, y, z) : (x + 1/3 >= 0) & (x - 1/3 <= 0) & (y - 1 <= 0) & (y - 1/3 > 0) & (z + 1 >= 0) & (z + 1/3 < 0)},
     {(x, y, z) : (x + 1/3 >= 0) & (x - 1/3 <= 0) & (y - 1 <= 0) & (y - 1/3 > 0) & (z + 1/3 >= 0) & (z - 1/3 <= 0)},
     {(x, y, z) : (x + 1/3 >= 0) & (x - 1/3 <= 0) & (y - 1 <= 0) & (y - 1/3 > 0) & (z - 1 <= 0) & (z - 1/3 > 0)},
     {(x, y, z) : (x - 1 <= 0) & (x - 1/3 > 0) & (y + 1 >= 0) & (y + 1/3 < 0) & (z + 1 >= 0) & (z + 1/3 < 0)},
     {(x, y, z) : (x - 1 <= 0) & (x - 1/3 > 0) & (y + 1 >= 0) & (y + 1/3 < 0) & (z + 1/3 >= 0) & (z - 1/3 <= 0)},
     {(x, y, z) : (x - 1 <= 0) & (x - 1/3 > 0) & (y + 1 >= 0) & (y + 1/3 < 0) & (z - 1 <= 0) & (z - 1/3 > 0)},
     {(x, y, z) : (x - 1 <= 0) & (x - 1/3 > 0) & (y + 1/3 >= 0) & (y - 1/3 <= 0) & (z + 1 >= 0) & (z + 1/3 < 0)},
     {(x, y, z) : (x - 1 <= 0) & (x - 1/3 > 0) & (y + 1/3 >= 0) & (y - 1/3 <= 0) & (z + 1/3 >= 0) & (z - 1/3 <= 0)},
     {(x, y, z) : (x - 1 <= 0) & (x - 1/3 > 0) & (y + 1/3 >= 0) & (y - 1/3 <= 0) & (z - 1 <= 0) & (z - 1/3 > 0)},
     {(x, y, z) : (x - 1 <= 0) & (x - 1/3 > 0) & (y - 1 <= 0) & (y - 1/3 > 0) & (z + 1 >= 0) & (z + 1/3 < 0)},
     {(x, y, z) : (x - 1 <= 0) & (x - 1/3 > 0) & (y - 1 <= 0) & (y - 1/3 > 0) & (z + 1/3 >= 0) & (z - 1/3 <= 0)},
     {(x, y, z) : (x - 1 <= 0) & (x - 1/3 > 0) & (y - 1 <= 0) & (y - 1/3 > 0) & (z - 1 <= 0) & (z - 1/3 > 0)}},
    actions=PathMonoid(SO3))
"""
from magicpy.puzzle.phy import *
from magicpy.model.euclid import *
from magicpy.model.poly import *
from magicpy.model.affine import *


RubiksCube = SymbolicSO3PhysicalPuzzle({cube})
RubiksCube = RubiksCube.cut_by(*[with_complement(halfspace(v, ri_cube/3))
                                 for v in vertices_octa])
RubiksCube = RubiksCube.simp()

