from sympy import sympify
from symplus.affine import *
from symplus.euclid import *
from magicpy.puzzle.phy import *

unit = sympify(2)/3
offset = unit/7
MirrorCube = SymbolicSO3PhysicalPuzzle([Box(center=[offset, 3*offset, 5*offset])])
MirrorCube = MirrorCube.cross_common([
     (Halfspace( unit, d), Halfspace(-unit, d)&Halfspace(-unit,-d), Halfspace( unit,-d))
     for d in [i,j,k]])

