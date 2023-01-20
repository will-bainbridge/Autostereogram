#!/usr/bin/python3

#-------------------------------------------------------------------------------
#
# This file is part of Autostereogram
#
# https://github.com/will-bainbridge/Autostereogram
#
# Copyright (C) 2023 Will Bainbridge
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#-------------------------------------------------------------------------------

import cv2
import optparse
import numpy as np
from time import process_time

np.set_printoptions(linewidth=100)

parser = optparse.OptionParser(usage='%prog [options] <x-resolution> <y-resolution> <radius> <output>')

options, args = parser.parse_args()

if len(args) != 4:
    parser.error("incorrect number of arguments")

try:
    shape = int(args[1]), int(args[0])
except ValueError:
    parser.error("x/y-resolution is not an integer")

try:
    radius = float(args[2])
except ValueError:
    parser.error("radius is not a number")

outputPath = args[3]

pattern = np.zeros((shape[0], shape[1], 3), dtype=np.uint8)
patternSet = np.zeros((shape[0], shape[1]), dtype=bool)

eps = np.finfo(float).eps

def mag(x):
    return np.sqrt(np.sum(np.square(x), axis=0))

unset = 0

time0 = process_time()
time = process_time()

while unset < shape[0]*shape[1]:

    centre = np.random.random((2, ))*shape

    colour = np.random.randint(0, np.iinfo(np.uint8).max, (3, ))

    ij0 = np.floor(centre - radius).astype(int)
    ij1 = np.ceil(centre + radius).astype(int)

    ij = np.array(np.meshgrid(range(ij0[0], ij1[0]), range(ij0[1], ij1[1])))

    a = mag(ij + [[[0]],[[0]]] - centre[:,None,None]) - radius
    b = mag(ij + [[[1]],[[0]]] - centre[:,None,None]) - radius
    c = mag(ij + [[[0]],[[1]]] - centre[:,None,None]) - radius
    d = mag(ij + [[[1]],[[1]]] - centre[:,None,None]) - radius

    ij[0] = ij[0] % shape[0]
    ij[1] = ij[1] % shape[1]

    def fCorner(a, b, c, d):
        return a*a/(abs(c)+abs(a))/(abs(b)+abs(a))/2

    def fSide(a, b, c, d):
        return (abs(a)/(abs(c)+abs(a))+abs(b)/(abs(d)+abs(b)))/2

    f = (
            (a < 0)*(b < 0)*(c < 0)*(d < 0)*1
          + (a < 0)*(b >= 0)*(c >= 0)*(d >= 0)*fCorner(a, b, c, d)
          + (a >= 0)*(b < 0)*(c < 0)*(d < 0)*(1 - fCorner(-a, -b, -c, -d))
          + (a >= 0)*(b < 0)*(c >= 0)*(d >= 0)*fCorner(b, d, a, c)
          + (a < 0)*(b >= 0)*(c < 0)*(d < 0)*(1 - fCorner(-b, -d, -a, -c))
          + (a >= 0)*(b >= 0)*(c < 0)*(d >= 0)*fCorner(c, a, d, b)
          + (a < 0)*(b < 0)*(c >= 0)*(d < 0)*(1 - fCorner(-c, -a, -d, -b))
          + (a >= 0)*(b >= 0)*(c >= 0)*(d < 0)*fCorner(d, c, b, a)
          + (a < 0)*(b < 0)*(c < 0)*(d >= 0)*(1 - fCorner(-d, -c, -b, -a))
          + (a < 0)*(b < 0)*(c >= 0)*(d >= 0)*fSide(a, b, c, d)
          + (a >= 0)*(b >= 0)*(c < 0)*(d < 0)*(1 - fSide(-a, -b, -c, -d))
          + (a >= 0)*(b < 0)*(c >= 0)*(d < 0)*fSide(b, d, a, c)
          + (a < 0)*(b >= 0)*(c < 0)*(d >= 0)*(1 - fSide(-b, -d, -a, -c))
          )

    pattern[ij[0],ij[1],:] = (
            (1 - f[:,:,None])*pattern[ij[0],ij[1],:]
          + f[:,:,None]*colour[None,None,:]
          )

    ijStar = ij[:,(a < 0)*(b < 0)*(c < 0)*(d < 0)]
    unset -= np.sum(patternSet[ijStar[0],ijStar[1]])
    patternSet[ijStar[0],ijStar[1]] = True
    unset += np.sum(patternSet[ijStar[0],ijStar[1]])

    time1 = process_time()
    if int(time) != int(time1):
        print('%g%% completed in %is' % (100*unset/shape[0]/shape[1], int(time1 - time0)))
    time = time1

cv2.imwrite(outputPath, pattern)
