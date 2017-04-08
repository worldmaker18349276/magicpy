magicball
=========

library for analyzing twisty puzzle

## Goal
Jumbling mechanism is too complex to find all state of puzzle, so it is rarely to find a jumbling twisty puzzle simulator. But if we use geometric analysis to check whether the operation is valid, rather than pre-define which operation we can use, that is possible to simulate the puzzle in jumbling state.
The main goal of this project is provide an API for jumbling twisty puzzle simulator.

## Inspiration
- [Ultimate Magic Cube](http://www.ultimatemagiccube.com/)
- [Interlocked](http://interlocked.wecreatestuff.com/)
- [Virtual Magic Polyhedra](http://users.skynet.be/moz071262/Applets/Magic%20Polyhedra/)

## Design
- ctrl/edit/view/analyze
- play & improve
- OpenSCAD-liked interface

## List
### symplus: (math model)
- [x] typlus:
    - [x] is_Tuple, is_Symbol, is_Number, is_Boolean, is_Matrix, is_Function
    - [x] type_match

- [x] tuplus:
    - [x] pack_if_not, unpack_if_can, repack_if_can

- [x] symbplus:
    - [x] free_symbols, rename_variables_in

- [x] funcplus:
    - [x] Functor
    - [x] Compose, Inverse, Apply

- [x] logicplus:
    - [x] Forall, Exist

- [x] setplus:
    - [x] AbstractSet, AbsoluteComplement
    - [x] as_abstract (Interval, ProductSet)
    - [x] Image, Contains
    - [x] simplify_boolean
    - [x] is_open, is_close
    - [x] Interior, Closure, Exterior
    - [x] regularize, Regularization, Regularized(AbsoluteComplement/Intersection/Union)
    - [x] Topology, DiscreteTopology, NaturalTopology

- [x] matplus:
    - [x] basic vector operation (norm, normalize, dot, cross, angle, project)

- [x] simplus:
    - [x] sqrt (sqrtsimp, with_sqrtsimp)
    - [x] matrix (matsimp, with_matsym)
    - [x] relational (polyrelsimp, logicrelsimp)

- [x] strplus:
    - [x] MathPrinter, pr, mprint, mstr, init_mprinting

- [x] path:
    - [x] FreeMonoid, Word
    - [x] PathMonoid, Path
    - [x] (Lambda/Additive/Multiplicative/Transformation)Path
    - [x] (Tensor/Concatenated/Sliced)Path

- [x] affine:
    - [x] tvec, rquat, parity, zfac, stri
    - [x] (/Affine/Euclidean)Transformation
    - [x] rotation, translation, reflection, scaling, shearing
    - [x] regular motion (rotate, shift)

- [ ] euclid:
    - [x] EuclideanSpace, WholeSpace
    - [x] Halfspace, Sphere, InfiniteCylinder, SemiInfiniteCone, Revolution
    - [x] Cube, Cylinder, Cone
    - [ ] EuclideanTopology (regular_open, interior, closure)

- [ ] poly:
    - [ ] vertices of 5 regular polyhedron
    - [ ] ConvexPolyhedron (from_hrepr, as_hrepr)
    - [ ] PointGroup
    - [ ] cut_by, is_disjoint, is_subset

### magicpy: (puzzle model)

##### solid:
- [x] general:
    - [x] SolidEngine

- [ ] sym:
    - [x] SymbolicSolidEngine
    - [x] SymbolicSolidEngineVolumeAlgo

- [x] marching:
    - [x] Voxels, VoxelEngine

- [ ] board:
    - [ ] Board(show, hide, animate, texture(color, transparent, highlight))


##### puzzle:
- [x] basic:
    - [x] Puzzle, (/Wrapped/Identity/Concatenated/Continuous)Operation
    - [x] TensorPuzzle, (Tensor/Parrallel)Operation
    - [x] CombinationalPuzzle, (Combinational/ContinuousCombinational/Selective)Operation

- [ ] phy:
    - [x] PhysicalPuzzle, (Physical/Partitional)Operation
    - [x] Symbolic(/SE3/SO3/T3)PhysicalPuzzle, Symbolic(Physical/Partitional)Operation
    - [ ] MagicBall/MagicShell/Interlock


##### museum:
- [x] FifteenPuzzle
- [x] RubiksCube
- [x] ball2x2x2
- [x] MirrorCube
- [ ] LightingGame


### MagicPart: (FreeCAD module)
- [x] Basic:
    - [x] fuzzyCompare(float, list, dict, Quantity, Vector, Rotation, Placement)
    - [x] spstr2spexpr, spexpr2spstr, fcexpr2spexpr, spexpr2fcexpr
    - [x] Param

##### Shapes:
- [x] Utilities
    - [x] reshape, mass, center

- [ ] Operation
    - [x] complement, common, fuse, compound, transform
    - [ ] is_null, is_outside, is_inside, no_collision

- [ ] Primitive
    - [x] makeConicalFrustum, construct
    - [ ] perturbation(to avoid OCC bugs)

- [ ] BooleanTracing
    - [x] biter, innerPointsOf, trace

##### Meshes:
- [x] Utilities
    - [x] asMesh, remesh, orientation, mass, center

- [ ] Operation
    - [x] complement, common, fuse, compound, transform
    - [ ] is_null, is_outside, is_inside, no_collision

- [x] Primitive
    - [x] makeConicalFrustum, construct

##### Features:
- [x] Utilities
    - [x] centerOf, massOf, meshOf, boundBoxOf
    - [x] ftrlist, typeIdOf, isDerivedFrom, isTouched, isDependOn, featurePropertiesOf, addObject
    - [x] forceTouch, retouch
    - [x] weakRecomputable, weakRecompute, recompute

- [ ] Variable
    - [ ] Variable(Scalar/Vector/Matrix/Transformation)

- [x] ViewBox
    - [x] getViewBox, initViewBox, setMaxBoundBox
    - [x] isBounded
    - [x] fitBounded, fitFeatures
    - [x] hideAllUnbounded, viewAllBounded, viewBoundedSelections

- [x] SubObject
    - [x] subFaceLinksOf, subShapeOf, subColorOf
    - [x] trace, outFaceLinksOf, outOf
    - [x] getSubSelection, shiftToSelection

- [x] Operation
    - [x] Compound, Intersection, Union, AbsoluteComplement, Image
    - [x] common, fuse, cut, complement, transform, compound, compoundFuse, compoundTransform, partition, fragment, slice
    - [x] isOutside, isInside, catch, noCollision

- [x] Primitive
    - [x] Feature
    - [x] WholeSpace, Halfspace, InfiniteCylinder, SemiInfiniteCone
    - [x] Sphere, Box, Cylinder, Cone
    - [x] show, contruct, SymPyExpressionOf

- [x] Wrapper
    - [x] Apart, Mask
    - [x] apart, mask
    - [ ] unwrap

##### Commands:
- [x] Control
    - [x] Toggle(Transparency/Touched)
    - [x] (/Force)RefreshSelected
    - [x] ShiftToChildren, View, Focus

- [x] Primitive
    - [x] AdjustViewBox
    - [x] Create(Box/Cylinder/Cone/Sphere)
    - [x] Create(Halfspace/InfiniteCylinder/InfiniteCone/WholeSpace)

- [x] Operation
    - [x] Common, Fuse, Cut, Complement, Transform
    - [x] Partition, Fragment, Slice
    - [x] Compound(/Remove/Fuse/Transform)
    - [x] Apart, Mask

- [ ] Check
    - [ ] isBounded, isEmpty
    - [ ] isOutside, isInside, catch, noCollision
