from sympy.sets import Intersection, Union
from magicpy.model.affine import transform


class Engine:
    def intersection(self, *zets):
        return Intersection(*zets)

    def union(self, *zets):
        return Union(*zets)

    def transform(self, zet, trans):
        return transform(trans, zet)

    def simp(self, zet):
        return zet

    def is_disjoint(self, zet1, zet2):
        raise NotImplementedError

    def is_subset(self, zet1, zet2):
        raise NotImplementedError

    def equal(self, zet1, zet2):
        raise NotImplementedError

