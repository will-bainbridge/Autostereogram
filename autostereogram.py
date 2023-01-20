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
import enum
import optparse
import numpy as np

class Align(enum.Enum):
    left, l = 1, 1
    right, r = 2, 2
    centre, center, c = 3, 3, 3

parser = optparse.OptionParser(usage='%prog [options] <depth> <pattern> <output>')

parser.add_option(
        '-f', '--factor',
        type=float,
        default=0.02,
        help='Maximum factor by which the image distorts. Default 0.02.',
        metavar='FACTOR'
        )
parser.add_option(
        '-a', '--align',
        type=str,
        default=Align.centre.name,
        help='Alignment of the undistorted plane. Left, right or centre. Default centre.',
        metavar='ALIGN'
        )

options, args = parser.parse_args()

if len(args) != 3:
    parser.error("incorrect number of arguments")

depthPath, patternPath, outputPath = args

try:
    align = Align[options.align.lower()]
except:
    parser.error('Alignment \"' + options.align + '\" not recognised')

depth = cv2.imread(depthPath, cv2.IMREAD_GRAYSCALE)
if depth is None:
    raise IOerror(depthPath + ' could not be read')

pattern = cv2.imread(patternPath)
if pattern is None:
    raise IOerror(patternPath + ' could not be read')

D, W = depth.shape[:2]
d, w = pattern.shape[:2]

shift = np.round(options.factor*W*depth/256).astype(int)

x, y = np.meshgrid(range(0, w + W), range(0, D))
x = (x - W//2) % w

if align == Align.left:
    for i in range(W):
        x[:, i + w] = x[range(D), i + shift[:,i] % w]
elif align == Align.right:
    for i in range(W - 1, -1, -1):
        x[:, i] = x[range(D), i + w - shift[:,i] % w]
elif align == Align.centre:
    for i in range(W//2 + np.round(options.factor*W/2).astype(int) - 1, -1, -1):
        x[:, i] = x[range(D), i + w - shift[:,i] % w]
    for i in range(W//2 - np.round(options.factor*W).astype(int), W):
        x[:, i + w] = x[range(D), i + shift[:,i] % w]

output = pattern[y % d, x]

cv2.imwrite(outputPath, output)
