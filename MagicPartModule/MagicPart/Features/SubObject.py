from itertools import islice
from MagicPart.Features.Utilities import *


def subFaceLinksOf(obj):
    return [(obj, "Face%s"%(i+1)) for i in range(len(obj.Shape.Faces))]

def subShapeOf(link):
    if link is None:
        return None

    if link[1].startswith("Face") or link[1].startswith("Edge") or link[1].startswith("Vertex"):
        return getattr(link[0].Shape, link[1])
    elif link[1] == "Shape":
        return link[0].Shape
    else:
        raise TypeError

def subColorOf(link, default=(0.8,0.8,0.8,0.0)):
    if link is None:
        return default

    if link[1].startswith("Face"):
        return diffuseColorOf(link[0])[int(link[1][4:])-1]
    else:
        raise TypeError


def biter(u0, u1, v0, v1):
    """
    (n, m) iterate like that:
    m
    ^
    | 10 12 14 15
    | 05 07 08 13
    | 02 03 06 11
    | 00 01 04 09
    +-------------> n

    (u, v) iterate like that:
    v
    ^
    | -- -- -- -- -- -- --
    | -- 06 -- 04 -- 08 --
    | -- -- -- -- -- -- --
    | -- 01 -- 00 -- 02 --
    | -- -- -- -- -- -- --
    | -- 05 -- 03 -- 07 --
    | -- -- -- -- -- -- --
    +----------------------> u
    """
    n = 0
    m = 0
    while True:
        du = (u1-u0)/2**n
        for i in xrange(2**n):
            dv = (v1-v0)/2**m
            for j in xrange(2**m):
                yield (u0 + du*(i+0.5), v0 + dv*(j+0.5))

        if n == m:
            n += 1
            m = 0
        elif n > m:
            m, n = n, m
        elif m > n:
            m, n = n+1, m

def innerPointsOf(face):
    return (face.valueAt(u, v) for u, v in biter(*face.ParameterRange) if face.isPartOfDomain(u, v))

def _trace(obj, outobjs=None, N=4):
    if outobjs is None:
        outobjs = ftrlist(obj.OutList)

    if len(outobjs) == 0:
        return [None]*len(obj.Shape.Faces)

    links = [link for outobj in outobjs for link in subFaceLinksOf(outobj)]
    outlinks = []
    for subface in obj.Shape.Faces:
        points = list(islice(innerPointsOf(subface), N))
        for link in links:
            face = subShapeOf(link)
            if all(face.isInside(p, face.Tolerance, True) for p in points):
                outlinks.append(link)
                break
        else:
            outlinks.append(None)
    return outlinks

def trace(obj):
    if isDerivedFrom(obj, "Part::Compound"):
        return [link for outobj in obj.Links for link in subFaceLinksOf(outobj)]

    elif isDerivedFrom(obj, "Part::FeaturePython") and hasattr(obj.Proxy, "_trace"):
        return obj.Proxy._trace(obj)

    else:
        return _trace(obj)

def outFaceLinksOf(obj, traced=True):
    if "Outfaces" in obj.PropertiesList:
        if obj.Outfaces == []:
            if traced:
                obj.Outfaces = trace(obj)
            else:
                return []

        return obj.Outfaces

    else:
        if traced:
            return trace(obj)
        else:
            return []

def outOf(link):
    if link is None:
        return None
    if not link[1].startswith("Face"):
        raise TypeError
    outlinks = outFaceLinksOf(link[0])
    if len(outlinks) == 0:
        raise ValueError
    return outlinks[int(link[1][4:])-1]

