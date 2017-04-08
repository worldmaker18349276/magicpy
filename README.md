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
- [x] typlus
  > is_Tuple, is_Symbol, is_Number, is_Boolean, is_Matrix, is_Function  
  > type_match  

- [x] tuplus
  > pack_if_not, unpack_if_can, repack_if_can  

- [x] symbplus
  > free_symbols, rename_variables_in  

- [x] funcplus
  > Functor  
  > Compose, Inverse, Apply  

- [x] logicplus
  > Forall, Exist  

- [x] setplus
  > AbstractSet, AbsoluteComplement  
  > as_abstract (Interval, ProductSet)  
  > Image, Contains  
  > simplify_boolean  
  > is_open, is_close  
  > Interior, Closure, Exterior  
  > regularize, Regularization, Regularized(AbsoluteComplement/Intersection/Union)  
  > Topology, DiscreteTopology, NaturalTopology  

- [x] matplus
  > basic vector operation (norm, normalize, dot, cross, angle, project)  

- [x] simplus
  > sqrt (sqrtsimp, with_sqrtsimp)  
  > matrix (matsimp, with_matsym)  
  > relational (polyrelsimp, logicrelsimp)  

- [x] strplus
  > MathPrinter, pr, mprint, mstr, init_mprinting  

- [x] path
  > FreeMonoid, Word  
  > PathMonoid, Path  
  > (Lambda/Additive/Multiplicative/Transformation)Path  
  > (Tensor/Concatenated/Sliced)Path  

- [x] affine
  > tvec, rquat, parity, zfac, stri  
  > (/Affine/Euclidean)Transformation  
  > rotation, translation, reflection, scaling, shearing  
  > regular motion (rotate, shift)  

- [ ] euclid
  > EuclideanSpace, WholeSpace  
  > Halfspace, Sphere, InfiniteCylinder, SemiInfiniteCone, Revolution  
  > Cube, Cylinder, Cone  
  > \+ EuclideanTopology (regular_open, interior, closure)  

- [ ] poly
  > \+ vertices of 5 regular polyhedron  
  > \+ ConvexPolyhedron (from_hrepr, as_hrepr)  
  > \+ PointGroup  
  > \+ cut_by, is_disjoint, is_subset  

### magicpy: (puzzle model)

- solid:
    - [x] general
      > SolidEngine  

    - [ ] sym
      > SymbolicSolidEngine  
      > SymbolicSolidEngineVolumeAlgo  

    - [x] marching
      > Voxels, VoxelEngine  

    - [ ] board
      > \+ Board(show, hide, animate, texture(color, transparent, highlight))  


- puzzle:
    - [x] basic
      > Puzzle, (/Wrapped/Identity/Concatenated/Continuous)Operation  
      > TensorPuzzle, (Tensor/Parrallel)Operation  
      > CombinationalPuzzle, (Combinational/ContinuousCombinational/Selective)Operation  

    - [ ] phy
      > PhysicalPuzzle, (Physical/Partitional)Operation  
      > Symbolic(/SE3/SO3/T3)PhysicalPuzzle, Symbolic(Physical/Partitional)Operation  
      > \+ MagicBall/MagicShell/Interlock  


- museum:
    - [x] FifteenPuzzle
    - [x] RubiksCube
    - [x] ball2x2x2
    - [x] MirrorCube
    - [ ] LightingGame


### MagicPart: (FreeCAD module)
- [x] Basic
  > fuzzyCompare(float, list, dict, Quantity, Vector, Rotation, Placement)  
  > spstr2spexpr, spexpr2spstr, fcexpr2spexpr, spexpr2fcexpr  
  > Param  

- Shapes:
    - [x] Utilities
      > reshape, mass, center  

    - [ ] Operation
      > complement, common, fuse, compound, transform  
      > \+ is_null, is_outside, is_inside, no_collision  

    - [ ] Primitive
      > makeConicalFrustum, construct  
      > \+ perturbation (to avoid OCC bugs)  

    - [x] BooleanTracing
      > biter, innerPointsOf, trace  


- Meshes:
    - [x] Utilities
      > asMesh, remesh, orientation, mass, center  

    - [ ] Operation
      > complement, common, fuse, compound, transform  
      > \+ is_null, is_outside, is_inside, no_collision  

    - [x] Primitive
      > makeConicalFrustum, construct  


- Features:
    - [x] Utilities
      > centerOf, massOf, meshOf, boundBoxOf  
      > ftrlist, typeIdOf, isDerivedFrom, isTouched, isDependOn, featurePropertiesOf, addObject  
      > forceTouch, retouch  
      > weakRecomputable, weakRecompute, recompute  

    - [ ] Variable
      > \+ Variable(Scalar/Vector/Matrix/Transformation)  

    - [x] ViewBox
      > getViewBox, initViewBox, setMaxBoundBox  
      > isBounded  
      > fitBounded, fitFeatures  
      > hideAllUnbounded, viewAllBounded, viewBoundedSelections  

    - [x] SubObject
      > subFaceLinksOf, subShapeOf, subColorOf  
      > trace, outFaceLinksOf, outOf  
      > getSubSelection, shiftToSelection  

    - [x] Operation
      > Compound, Intersection, Union, AbsoluteComplement, Image  
      > common, fuse, cut, complement, transform, compound, compoundFuse, compoundTransform, partition, fragment, slice  
      > isOutside, isInside, catch, noCollision  

    - [x] Primitive
      > Feature  
      > WholeSpace, Halfspace, InfiniteCylinder, SemiInfiniteCone  
      > Sphere, Box, Cylinder, Cone  
      > show, contruct, SymPyExpressionOf  

    - [x] Wrapper
      > Apart, Mask  
      > apart, mask  
      > \+ unwrap  


- Commands:
    - [x] Control
      > Toggle(Transparency/Touched)  
      > (/Force)RefreshSelected  
      > ShiftToChildren, View, Focus  

    - [x] Primitive
      > AdjustViewBox  
      > Create(Box/Cylinder/Cone/Sphere)  
      > Create(Halfspace/InfiniteCylinder/InfiniteCone/WholeSpace)  

    - [x] Operation
      > Common, Fuse, Cut, Complement, Transform  
      > Partition, Fragment, Slice  
      > Compound(/Remove/Fuse/Transform)  
      > Apart, Mask  

    - [ ] Check
      > \+ isBounded, isEmpty  
      > \+ isOutside, isInside, catch, noCollision  
