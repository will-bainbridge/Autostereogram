# Autostereogram

* Author: Will Bainbridge
* Date: 2023
* GitHub: <https://github.com/will-bainbridge/Autostereogram>

# License

Autostrerogram is provided under the terms of the GPL License v3.

# Description

Autostereogram is a simple pair of scripts for creating autostereograms, or "magic eye" images.

# Dependencies

Python 3, with cv2, numpy, and optparse.

# Usage

Create a random pattern image, 200x1000 pixels in size, filled with 10 pixel dots:

    ./pattern.py 200 1000 10 pattern.png

Use the pattern image and the example depth image for the Utah teapot to create an autostereogram:

    ./autostereogram.py utah.png pattern.png magic.png

Open magic.png in an image viewer, unfocus your eyes, and see a three-dimensional teapot!

To view additional settings and options, call the scripts with the argument `--help`.
