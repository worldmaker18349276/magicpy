from sympy.sets import Intersection, Union
from symplus.funcplus import Image
from symplus.pathplus import IdentityPath


class Engine:
    def intersection(self, *zets):
        return Intersection(*zets)

    def union(self, *zets):
        return Union(*zets)

    def transform_by(self, zet, op):
        if isinstance(op, IdentityPath):
            return zet
        else:
            return Image(op.call(), zet)

    def simp(self, zet):
        return zet

    def is_disjoint(self, zet1, zet2):
        raise NotImplementedError

    def is_subset(self, zet1, zet2):
        raise NotImplementedError

    def equal(self, zet1, zet2):
        raise NotImplementedError

