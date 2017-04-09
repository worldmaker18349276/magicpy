import math
from symplus.affine import AffineTransformation, rmat_k2d
from symplus.setplus import Intersection, Union, Complement, AbsoluteComplement, Image
import symplus.euclid as euclid
import FreeCAD, Part
from MagicPart.Basic import fuzzyCompare, spexpr2fcexpr, P
from MagicPart.Shapes.Operation import complement, common, fuse, transform


def makeConicalFrustum(radius1, radius2, height, pnt=FreeCAD.Vector()):
    if fuzzyCompare(radius1, radius2):
        return Part.makeCylinder(abs(radius1), abs(height), pnt)

    elif radius1*radius2 >= 0:
        return Part.makeCone(abs(radius1), abs(radius2), abs(height), pnt)

    else:
        height1 = abs(height)*abs(radius1/(radius1-radius2))
        height2 = abs(height)*abs(radius2/(radius1-radius2))
        pnt1 = pnt
        pnt2 = pnt + FreeCAD.Vector(0, 0, height1)
        shape1 = Part.makeCone(abs(radius1), 0, height1, pnt1)
        shape2 = Part.makeCone(0, abs(radius2), height2, pnt2)
        shape = shape1.fuse(shape2)
        return shape

# to avoid OCC bugs
def perturb(v):
    if not P.pert:
        return v
    import random
    if isinstance(v, FreeCAD.Placement):
        rot = FreeCAD.Rotation(random.random()*0.1, random.random()*0.1, random.random()*0.1)
        return FreeCAD.Placement(FreeCAD.Vector(0,0,0), rot).multiply(v)
    elif isinstance(v, FreeCAD.Vector):
        return v + FreeCAD.Vector(perturb(0), perturb(0), perturb(0))
    else:
        return v + random.random()*1e-03

def construct(zet, mbb, margin=1e-03):
    if zet is None:
        return Part.Shape()

    elif isinstance(zet, Intersection):
        return common(construct(arg, mbb, margin) for arg in zet.args)

    elif isinstance(zet, Union):
        return fuse(construct(arg, mbb, margin) for arg in zet.args)

    elif isinstance(zet, Complement):
        return common([construct(zet.arg[0], mbb, margin),
                       complement(construct(zet.arg[1], mbb, margin))])

    elif isinstance(zet, AbsoluteComplement):
        return complement(construct(zet.arg[0], mbb, margin))

    elif isinstance(zet, Image):
        placement = spexpr2fcexpr(zet.function)
        mbb_ = mbb.transformed(placement.inverse().toMatrix())
        return transform(construct(zet.set, mbb_, margin), zet.function)

    elif isinstance(zet, euclid.EmptySpace):
        return Part.Shape()

    elif isinstance(zet, euclid.WholeSpace):
        shape = Part.makeSphere(mbb.DiagonalLength/2 + margin, mbb.Center)
        return shape

    elif isinstance(zet, euclid.Halfspace):
        direction = spexpr2fcexpr(zet.direction)
        offset = spexpr2fcexpr(zet.offset)
        if not mbb.isCutPlane(direction*offset, direction):
            return direction*mbb.Center > offset

        rot = rmat_k2d(zet.direction)
        center = zet.direction*zet.offset
        placement = perturb(spexpr2fcexpr(AffineTransformation(matrix=rot)))
        placement.move(perturb(spexpr2fcexpr(center)))

        mbb_ = mbb.transformed(placement.inverse().toMatrix())
        height = mbb_.ZMax + margin
        xm = max(abs(mbb_.XMax), abs(mbb_.XMin))
        ym = max(abs(mbb_.YMax), abs(mbb_.YMin))
        radius = math.sqrt(xm**2 + ym**2) + margin
        shape = makeConicalFrustum(radius, radius, height)
        shape.Placement = placement
        return shape

    elif isinstance(zet, euclid.InfiniteCylinder):
        direction = spexpr2fcexpr(zet.direction)
        center = spexpr2fcexpr(zet.center)
        dist = mbb.Center.distanceToLine(center, direction)
        radius = spexpr2fcexpr(zet.radius)
        mbb_radius = mbb.DiagonalLength/2
        if radius + mbb_radius < dist:
            return Part.Shape()
        elif radius - mbb_radius > dist:
            return construct(euclid.WholeSpace(), mbb, margin)

        rot = rmat_k2d(zet.direction)
        placement = perturb(spexpr2fcexpr(AffineTransformation(matrix=rot)))
        placement.move(perturb(spexpr2fcexpr(zet.center)))

        mbb_ = mbb.transformed(placement.inverse().toMatrix())
        height = mbb_.ZLength + 2*margin
        bottom = FreeCAD.Vector(0, 0, mbb_.ZMin-margin)
        shape = makeConicalFrustum(radius, radius, height, bottom)
        shape.Placement = placement
        return shape

    elif isinstance(zet, euclid.SemiInfiniteCone):
        pnt = mbb.Center - spexpr2fcexpr(zet.center)
        mbb_radius = mbb.DiagonalLength/2
        if pnt.Length > mbb_radius:
            direction = spexpr2fcexpr(zet.direction)
            ang = math.acos(direction*pnt/pnt.Length)
            ang_cone = math.atan(spexpr2fcexpr(zet.slope))
            ang_ball = math.asin(mbb_radius/pnt.Length)
            if ang_cone + ang_ball < ang:
                return Part.Shape()
            elif ang_cone - ang_ball > ang:
                return construct(euclid.WholeSpace(), mbb, margin)

        rot = rmat_k2d(zet.direction)
        placement = perturb(spexpr2fcexpr(AffineTransformation(matrix=rot)))
        placement.move(perturb(spexpr2fcexpr(zet.center)))

        mbb_ = mbb.transformed(placement.inverse().toMatrix())
        height = mbb_.ZMax+margin
        radius = height*spexpr2fcexpr(zet.slope)
        shape = makeConicalFrustum(0, radius, height)
        shape.Placement = placement
        return shape

    elif isinstance(zet, euclid.Sphere):
        radius = spexpr2fcexpr(zet.radius)
        shape = Part.makeSphere(radius)

        placement = perturb(spexpr2fcexpr(AffineTransformation(vector=zet.center)))
        shape.Placement = placement
        return shape

    elif isinstance(zet, euclid.Box):
        size = spexpr2fcexpr(zet.size)
        pnt = size*(-0.5)
        shape = Part.makeBox(size.x, size.y, size.z, pnt)

        rot = zet.orientation
        placement = perturb(spexpr2fcexpr(AffineTransformation(matrix=rot)))
        placement.move(perturb(spexpr2fcexpr(zet.center)))
        shape.Placement = placement

        return shape

    elif isinstance(zet, euclid.Cylinder):
        radius = spexpr2fcexpr(zet.radius)
        height = spexpr2fcexpr(zet.height)
        pnt = FreeCAD.Vector(0, 0, -height/2)
        shape = makeConicalFrustum(radius, radius, height, pnt)

        rot = rmat_k2d(zet.direction)
        placement = perturb(spexpr2fcexpr(AffineTransformation(matrix=rot)))
        placement.move(perturb(spexpr2fcexpr(zet.center)))
        shape.Placement = placement

        return shape

    elif isinstance(zet, euclid.Cone):
        radius = spexpr2fcexpr(zet.radius)
        height = spexpr2fcexpr(zet.height)
        shape = makeConicalFrustum(0, radius, height)

        rot = rmat_k2d(zet.direction)
        placement = perturb(spexpr2fcexpr(AffineTransformation(matrix=rot)))
        placement.move(perturb(spexpr2fcexpr(zet.center)))
        shape.Placement = placement

        return shape

    else:
        raise TypeError

