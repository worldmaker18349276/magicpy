import doctest


import magicball.sympy.util as util
doctest.testmod(util)

import magicball.sympy.matplus as matplus
doctest.testmod(matplus)

import magicball.sympy.setplus as setplus
doctest.testmod(setplus)

import magicball.sympy.toplus as toplus
doctest.testmod(toplus)

import magicball.sympy.polyplus as polyplus
doctest.testmod(polyplus)

import magicball.sympy.affine as affine
doctest.testmod(affine)

