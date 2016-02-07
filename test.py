import doctest


import symplus.util as util
doctest.testmod(util)

import symplus.matplus as matplus
doctest.testmod(matplus)

import symplus.logicplus as logicplus
doctest.testmod(logicplus)

import symplus.simplus as simplus
doctest.testmod(simplus)

import symplus.setplus as setplus
doctest.testmod(setplus)

import symplus.topoplus as topoplus
doctest.testmod(topoplus)

import symplus.funcplus as funcplus
doctest.testmod(funcplus)

import symplus.strplus as strplus
doctest.testmod(strplus)

import magicpy.engine.basic as basic
doctest.testmod(basic)

import magicpy.engine.marching as marching
doctest.testmod(marching)

import magicpy.model.path as path
doctest.testmod(path)

import magicpy.model.affine as affine
doctest.testmod(affine)

import magicpy.model.euclid as euclid
doctest.testmod(euclid)

import magicpy.model.poly as poly
doctest.testmod(poly)

import magicpy.puzzle.phy as phy
doctest.testmod(phy)

import magicpy.museum.RubiksCube as RubiksCube
doctest.testmod(RubiksCube)

