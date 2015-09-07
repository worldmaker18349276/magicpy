import doctest


import magicball.symplus.util as util
doctest.testmod(util)

import magicball.symplus.matplus as matplus
doctest.testmod(matplus)

import magicball.symplus.logicplus as logicplus
doctest.testmod(logicplus)

import magicball.symplus.relplus as relplus
doctest.testmod(relplus)

import magicball.symplus.setplus as setplus
doctest.testmod(setplus)

import magicball.symplus.strplus as strplus
doctest.testmod(strplus)

import magicball.symplus.path as path
doctest.testmod(path)

import magicball.engine.sample as sample
doctest.testmod(sample)

import magicball.model.affine as affine
doctest.testmod(affine)

import magicball.model.euclid as euclid
doctest.testmod(euclid)

import magicball.model.poly as poly
doctest.testmod(poly)

import magicball.puzzle.phy as phy
doctest.testmod(phy)

