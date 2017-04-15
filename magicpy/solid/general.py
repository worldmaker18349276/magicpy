from itertools import combinations, product, starmap
from sympy.sets import Intersection, Union
from symplus.setplus import Image, AbsoluteComplement
from symplus.path import IdentityPath
from magicpy.util import map, filterfalse


class SolidEngine(object):
    def is_null(self, obj):
        raise NotImplementedError

    def is_outside(self, obj, reg):
        raise self.is_null(self.common([obj, reg]))

    def is_inside(self, obj, reg):
        return self.is_outside(obj, self.complement(reg))

    def side_of(self, obj, reg, err=False):
        res = self.is_inside(obj, reg) - self.is_outside(obj, reg)
        if err and res == 0:
            raise ValueError
        return res

    def located_in(self, obj, regs, err=False):
        return next((i for i, reg in enumerate(regs)
                       if self.side_of(obj, reg, err=err) == 1), None)

    def divide_into(self, objs, regs, err=False):
        regs = tuple(regs)
        groups = [[] for _ in range(len(regs))]
        remaining = []
        for obj in objs:
            i = self.located_in(obj, regs, err=err)
            if i is None:  remaining.appand(obj)
            else:          groups[i].appand(obj)
        return groups, remaining

    def no_collision(self, objs):
        return all(starmap(self.is_outside, combinations(tuple(objs), 2)))

    def no_cross_collision(self, cols):
        return all(map(self.no_collision, product(*map(tuple, cols))))

    def common(self, objs):
        raise NotImplementedError

    def cross_common(self, cols):
        return tuple(map(self.common, product(*map(tuple, cols))))

    def fuse(self, objs):
        raise NotImplementedError

    def partial_fuse(self, col, glues=None, remain=True, err=False):
        if glues is None:
            return (self.fuse(col),)
        targets, remaining = self.divide_into(col, glues, err=err)
        fused = tuple(map(self.fuse, targets))
        if remain:
            fused = fused + tuple(remaining)
        return fused

    def complement(self, obj):
        raise NotImplementedError

    def cut(self, obj1, obj2):
        return self.common([obj1, self.complement(obj2)])

    def partition(self, *objs):
        knives = zip(objs, map(self.complement, objs))
        return tuple(map(self.common, product(*knives)))

    def partition_by(self, col, *objs):
        knives = zip(objs, map(self.complement, objs))
        return tuple(map(self.common, product(col, *knives)))

    def transform(self, obj, trans):
        raise NotImplementedError

    def simp(self, obj):
        return obj

    def simplify(self, col):
        return tuple(filterfalse(self.is_null, map(self.simp, col)))


class SolidDisplayer(object):
    def show(self, document):
        raise NotImplementedError

    def clear(self):
        raise NotImplementedError

class OpenSCADDisplayer(SolidDisplayer):

    def __init__(self):
        self.fn = 50
        self.proc = None
        self.temp = None

        self.settings = {}
        self.settings["$fa"] = 1
        self.settings["$fs"] = 0.1
        self.settings["$fn"] = 50
        self.settings["$t"] = 0.1
        self.settings["$vpt"] = [0, 0, 0]
        self.settings["$vpr"] = [55.0, 0.0, 25.0]
        self.settings["$vpd"] = 10

        import atexit
        atexit.register(self.clear)

    def __enter__(self):
        return self

    def __exit__(self, typ, msg, traceback):
        self.clear()
        return False

    def clear(self):
        if self.proc is not None and self.proc.poll() is None:
            self.proc.terminate()
        if self.temp is not None and not self.temp.closed:
            self.temp.close()

    def show(self, document):
        scad = ""
        for k, v in self.settings.items():
            scad += "{}={!s};".format(k,v)
        for k, v in document.items():
            scad += self.interpret(v)

        import subprocess, tempfile
        self.clear()
        self.temp = tempfile.NamedTemporaryFile(suffix=".scad", prefix="tmp", dir=".")
        self.temp.write(scad.encode("UTF-8"))
        self.temp.flush()
        self.proc = subprocess.Popen(["openscad", self.temp.name])

