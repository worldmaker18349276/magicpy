import math
from symplus.affine import AffineTransformation, rmat_k2d
import symplus.euclid as euclid
import FreeCAD, Mesh
from MagicPart.Basic import fuzzyCompare, spexpr2fcexpr


def createConicalFrustum(radius1, radius2, height, pnt=FreeCAD.Vector(), fn=50):
    if fuzzyCompare(radius1, radius2):
        mesh = Mesh.createCylinder(abs(radius1), abs(height), 1, 0.5/fn, int(fn))
        mesh.transform(FreeCAD.Placement(pnt, FreeCAD.Rotation(0,-90,0)).toMatrix())
        return mesh

    elif radius1*radius2 >= 0:
        mesh = Mesh.createCone(abs(radius1), abs(radius2), abs(height), 1, 0.5/fn, int(fn))
        mesh.transform(FreeCAD.Placement(pnt, FreeCAD.Rotation(0,-90,0)).toMatrix())
        return mesh

    else:
        height1 = abs(height)*abs(radius1/(radius1-radius2))
        height2 = abs(height)*abs(radius2/(radius1-radius2))
        pnt1 = pnt
        pnt2 = pnt + FreeCAD.Vector(0, 0, height1)

        mesh1 = Mesh.createCone(abs(radius1), 0, height1, 1, 0.5/fn, int(fn))
        mesh1.transform(FreeCAD.Placement(pnt1, FreeCAD.Rotation(0,-90,0)).toMatrix())
        mesh2 = Mesh.createCone(0, abs(radius2), height2, 1, 0.5/fn, int(fn))
        mesh2.transform(FreeCAD.Placement(pnt2, FreeCAD.Rotation(0,-90,0)).toMatrix())
        mesh = mesh1.unite(mesh2)
        return mesh

def primitive(zet, mbb, margin=1e-03, fn=50):
    if isinstance(zet, euclid.WholeSpace):
        mesh = Mesh.createSphere(mbb.DiagonalLength/2 + margin, int(fn))
        mesh.translate(*mbb.Center)
        return mesh

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
        mesh = createConicalFrustum(radius, radius, height, fn=fn)
        mesh.Placement = placement
        return mesh

    elif isinstance(zet, euclid.InfiniteCylinder):
        direction = spexpr2fcexpr(zet.direction)
        center = spexpr2fcexpr(zet.center)
        dist = mbb.Center.distanceToLine(center, direction)
        radius = spexpr2fcexpr(zet.radius)
        mbb_radius = mbb.DiagonalLength/2
        if radius + mbb_radius < dist:
            return False
        elif radius - mbb_radius > dist:
            return True

        rot = rmat_k2d(zet.direction)
        placement = spexpr2fcexpr(AffineTransformation(matrix=rot, vector=zet.center))

        mbb_ = mbb.transformed(placement.inverse().toMatrix())
        height = mbb_.ZLength + 2*margin
        bottom = FreeCAD.Vector(0, 0, mbb_.ZMin-margin)
        mesh = createConicalFrustum(radius, radius, height, bottom, fn=fn)
        mesh.Placement = placement
        return mesh

    elif isinstance(zet, euclid.SemiInfiniteCone):
        pnt = mbb.Center - spexpr2fcexpr(zet.center)
        mbb_radius = mbb.DiagonalLength/2
        if pnt.Length > mbb_radius:
            direction = spexpr2fcexpr(zet.direction)
            ang = abs(math.acos(direction*pnt/pnt.Length))
            ang_cone = math.atan(spexpr2fcexpr(zet.slope))
            ang_ball = math.asin(mbb_radius/pnt.Length)
            if ang_cone + ang_ball < ang:
                return False
            elif ang_cone - ang_ball > ang:
                return True

        rot = rmat_k2d(zet.direction)
        placement = spexpr2fcexpr(AffineTransformation(matrix=rot, vector=zet.center))

        mbb_ = mbb.transformed(placement.inverse().toMatrix())
        height = mbb_.ZLength + margin
        radius = height*spexpr2fcexpr(zet.slope)
        mesh = createConicalFrustum(0, radius, height, fn=fn)
        mesh.Placement = placement
        return mesh

    elif isinstance(zet, euclid.Sphere):
        radius = spexpr2fcexpr(zet.radius)
        mesh = Mesh.createSphere(radius, int(fn))

        placement = spexpr2fcexpr(AffineTransformation(vector=zet.center))
        mesh.Placement = placement
        return mesh

    elif isinstance(zet, euclid.Box):
        size = spexpr2fcexpr(zet.size)
        mesh = Mesh.createBox(size.x, size.y, size.z)

        rot = zet.orientation
        placement = spexpr2fcexpr(AffineTransformation(matrix=rot, vector=zet.center))
        mesh.Placement = placement

        return mesh

    elif isinstance(zet, euclid.Cylinder):
        radius = spexpr2fcexpr(zet.radius)
        height = spexpr2fcexpr(zet.height)
        pnt = FreeCAD.Vector(0, 0, -height/2)
        mesh = createConicalFrustum(radius, radius, height, pnt, fn=fn)

        rot = rmat_k2d(zet.direction)
        placement = spexpr2fcexpr(AffineTransformation(matrix=rot, vector=zet.center))
        mesh.Placement = placement

        return mesh

    elif isinstance(zet, euclid.Cone):
        radius = spexpr2fcexpr(zet.radius)
        height = spexpr2fcexpr(zet.height)
        mesh = createConicalFrustum(0, radius, height, fn=fn)

        rot = rmat_k2d(zet.direction)
        placement = spexpr2fcexpr(AffineTransformation(matrix=rot, vector=zet.center))
        mesh.Placement = placement

        return mesh

    else:
        raise TypeError

