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

import magicball.affine as affine
doctest.testmod(affine)

import magicball.euclid as euclid
doctest.testmod(euclid)

import magicball.path as path
doctest.testmod(path)
