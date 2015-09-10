from sympy.sets import Intersection, Union
from magicball.model.affine import transform


class Engine:
    def __init__(self, sample):
        self.sample = sample

    def intersection(self, *asets):
        return Intersection(*asets)

    def union(self, *asets):
        return Union(*asets)

    def transform(self, aset, mat):
        return transform(aset, mat)

    def simp(self, aset):
        return aset

    def is_disjoint(self, aset1, aset2):
        raise NotImplementedError

    def is_subset(self, aset1, aset2):
        raise NotImplementedError

    def equal(self, aset1, aset2):
        raise NotImplementedError

