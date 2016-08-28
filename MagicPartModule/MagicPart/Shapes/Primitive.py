import math
from symplus.affine import AffineTransformation, rmat_k2d
import symplus.euclid as euclid
import FreeCAD, Part
from MagicPart.Basic import fuzzyCompare, spexpr2fcexpr


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

def primitive(zet, mbb, margin=1e-03):
    if isinstance(zet, euclid.WholeSpace):
        shape = Part.makeSphere(mbb.DiagonalLength/2 + margin, mbb.Center)
        return shape

    elif isinstance(zet, euclid.Halfspace):
        direction = spexpr2fcexpr(zet.direction)
        offset = spexpr2fcexpr(zet.offset)
        if not mbb.isCutPlane(direction*offset, direction):
            return direction*mbb.Center > offset

        rot = rmat_k2d(zet.direction)
        center = zet.direction*zet.offset
        placement = spexpr2fcexpr(AffineTransformation(matrix=rot, vector=center))

        mbb_ = mbb.transformed(placement.inverse().toMatrix())
        height = mbb_.ZMax + margin
        xm = max(abs(mbb_.XMax), abs(mbb_.XMin))
        ym = max(abs(mbb_.YMax), abs(mbb_.YMin))
        radius = math.sqrt(xm**2 + ym**2) + margin
        shape = makeConicalFrustum(radius, radius, height)
        shape.Placement = placement
        return shape

    elif isinstance(zet, (euclid.InfiniteCylinder, euclid.AntiInfiniteCylinder)):
        direction = spexpr2fcexpr(zet.direction)
        center = spexpr2fcexpr(zet.center)
        dist = mbb.Center.distanceToLine(center, direction)
        radius = spexpr2fcexpr(zet.radius)
        mbb_radius = mbb.DiagonalLength/2
        if radius + mbb_radius < dist:
            return isinstance(zet, euclid.AntiInfiniteCylinder)
        elif radius - mbb_radius > dist:
            return isinstance(zet, euclid.InfiniteCylinder)

        rot = rmat_k2d(zet.direction)
        placement = spexpr2fcexpr(AffineTransformation(matrix=rot, vector=zet.center))

        mbb_ = mbb.transformed(placement.inverse().toMatrix())
        height = mbb_.ZLength + 2*margin
        bottom = FreeCAD.Vector(0, 0, mbb_.ZMin-margin)
        shape = makeConicalFrustum(radius, radius, height, bottom)
        shape.Placement = placement
        if isinstance(zet, euclid.AntiInfiniteCylinder):
            shape.complement()
        return shape

    elif isinstance(zet, (euclid.InfiniteCone, euclid.AntiInfiniteCone)):
        pnt = mbb.Center - spexpr2fcexpr(zet.center)
        mbb_radius = mbb.DiagonalLength/2
        if pnt.Length > mbb_radius:
            direction = spexpr2fcexpr(zet.direction)
            ang = abs(math.acos(direction*pnt/pnt.Length))
            ang_cone = math.atan(spexpr2fcexpr(zet.slope))
            ang_ball = math.asin(mbb_radius/pnt.Length)
            if ang_cone + ang_ball < ang:
                return isinstance(zet, euclid.AntiInfiniteCone)
            elif ang_cone - ang_ball > ang:
                return isinstance(zet, euclid.InfiniteCone)

        rot = rmat_k2d(zet.direction)
        placement = spexpr2fcexpr(AffineTransformation(matrix=rot, vector=zet.center))

        mbb_ = mbb.transformed(placement.inverse().toMatrix())
        slope = spexpr2fcexpr(zet.slope)
        radius1 = (mbb_.ZMin-margin)*slope
        radius2 = (mbb_.ZMax+margin)*slope
        height = mbb_.ZLength + 2*margin
        bottom = FreeCAD.Vector(0, 0, mbb_.ZMin-margin)
        shape = makeConicalFrustum(radius1, radius2, height, bottom)
        shape.Placement = placement
        if isinstance(zet, euclid.AntiInfiniteCone):
            shape.complement()
        return shape

    elif isinstance(zet, (euclid.Sphere, euclid.AntiSphere)):
        radius = spexpr2fcexpr(zet.radius)
        shape = Part.makeSphere(radius)

        placement = spexpr2fcexpr(AffineTransformation(vector=zet.center))
        shape.Placement = placement
        if isinstance(zet, euclid.AntiSphere):
            shape.complement()
        return shape

    elif isinstance(zet, euclid.Box):
        size = spexpr2fcexpr(zet.size)
        pnt = size*(-0.5)
        shape = Part.makeBox(size.x, size.y, size.z, pnt)

        rot = zet.orientation
        placement = spexpr2fcexpr(AffineTransformation(matrix=rot, vector=zet.center))
        shape.Placement = placement

        return shape

    elif isinstance(zet, euclid.Cylinder):
        radius = spexpr2fcexpr(zet.radius)
        height = spexpr2fcexpr(zet.height)
        pnt = FreeCAD.Vector(0, 0, -height/2)
        shape = makeConicalFrustum(radius, radius, height, pnt)

        rot = rmat_k2d(zet.direction)
        placement = spexpr2fcexpr(AffineTransformation(matrix=rot, vector=zet.center))
        shape.Placement = placement

        return shape

    elif isinstance(zet, euclid.Cone):
        radius = spexpr2fcexpr(zet.radius)
        height = spexpr2fcexpr(zet.height)
        shape = makeConicalFrustum(0, radius, height)

        rot = rmat_k2d(zet.direction)
        placement = spexpr2fcexpr(AffineTransformation(matrix=rot, vector=zet.center))
        shape.Placement = placement

        return shape

    else:
        raise TypeError

