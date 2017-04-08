from sympy import Matrix
from sympy.combinatorics import Permutation
from sympy.printing.str import StrPrinter
from magicpy.puzzle.basic import *


class FifteenPuzzle(Puzzle):
    def __init__(self, arg=list(range(1,16))+[0]):
        self.mat = Matrix(4,4, list(arg))

    def is_valid_state(self):
        return list(sorted(self.mat)) == list(range(16))

    def is_valid_operation(self, op):
        if not (isinstance(op, PermutationOperation) and
                len(op.perm.array_form) == 16):
            return False
        cyc = op.perm.cyclic_form
        if len(cyc) == 0:
            return True
        if not (len(cyc) == 1 and len(cyc[0]) == 2):
            return False
        a = divmod(cyc[0][0], 4)
        b = divmod(cyc[0][1], 4)
        if not (self.mat[a] == 0 or self.mat[b] == 0):
            return False
        dm = a[0]-b[0]
        dn = a[1]-b[1]
        return dm*dn == 0 and abs(dm+dn) == 1

    def __str__(self):
        return self.mat.table(StrPrinter())

    def __repr__(self):
        return str(self)

pzl = FifteenPuzzle()


class PermutationOperation(Operation):
    def __init__(self, *args):
        self.perm = Permutation(*args, size=16)

    def transform(self, pzl):
        flat = list(pzl.mat)
        moved = list(flat)
        for i, e in enumerate(flat):
            moved[self.perm(i)] = e
        return pzl.new(moved)

    def __str__(self):
        return str(self.perm)

    def __repr__(self):
        return str(self)

class MoveDownOperation(WrappedOperation):
    def interpret_for(self, pzl):
        a = list(pzl.mat).index(0)
        if divmod(a,4)[0] == 3:
            return PermutationOperation()
        else:
            return PermutationOperation(a, a+4)

    def __str__(self):
        return "[v]"

    def __repr__(self):
        return str(self)

class MoveUpOperation(WrappedOperation):
    def interpret_for(self, pzl):
        a = list(pzl.mat).index(0)
        if divmod(a,4)[0] == 0:
            return PermutationOperation()
        else:
            return PermutationOperation(a, a-4)

    def __str__(self):
        return "[^]"

    def __repr__(self):
        return str(self)

class MoveLeftOperation(WrappedOperation):
    def interpret_for(self, pzl):
        a = list(pzl.mat).index(0)
        if divmod(a,4)[1] == 0:
            return PermutationOperation()
        else:
            return PermutationOperation(a, a-1)

    def __str__(self):
        return "[<]"

    def __repr__(self):
        return str(self)

class MoveRightOperation(WrappedOperation):
    def interpret_for(self, pzl):
        a = list(pzl.mat).index(0)
        if divmod(a,4)[1] == 3:
            return PermutationOperation()
        else:
            return PermutationOperation(a, a+1)

    def __str__(self):
        return "[>]"

    def __repr__(self):
        return str(self)

up = MoveUpOperation()
down = MoveDownOperation()
left = MoveLeftOperation()
right = MoveRightOperation()
