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

import symplus.funcplus as funcplus
doctest.testmod(funcplus)

import symplus.strplus as strplus
doctest.testmod(strplus)

import magicball.engine.basic as basic
doctest.testmod(basic)

import magicball.engine.marching as marching
doctest.testmod(marching)

import magicball.model.path as path
doctest.testmod(path)

import magicball.model.affine as affine
doctest.testmod(affine)

import magicball.model.euclid as euclid
doctest.testmod(euclid)

import magicball.model.poly as poly
doctest.testmod(poly)

import magicball.puzzle.phy as phy
doctest.testmod(phy)

import magicball.museum.RubiksCube as RubiksCube
doctest.testmod(RubiksCube)

