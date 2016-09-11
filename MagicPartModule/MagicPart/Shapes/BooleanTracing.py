from itertools import islice


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

def trace(shp, outshps=[], N=4):
    if len(outshps) == 0:
        return [None]*len(shp.Faces)

    inds = [(i, j) for i, outshp in enumerate(outshps) for j in range(len(outshp.Faces))]
    outinds = []
    for subface in shp.Faces:
        points = list(islice(innerPointsOf(subface), N))
        for i, j in inds:
            face = outshps[i].Faces[j]
            if all(face.isInside(p, face.Tolerance, True) for p in points):
                outinds.append((i, j))
                break
        else:
            outinds.append(None)
    return outinds

